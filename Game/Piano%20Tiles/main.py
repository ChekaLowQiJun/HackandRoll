#Credit to pyGuru123 for creating the template for the game and most of the inspiration
#Controller for playing the game using webcam done by Cheka 

#Importing relevant libraries

from ultralytics import YOLO
import cv2
from cv2 import VideoCapture
import json
import random
import pygame
from threading import Thread
from objects import Tile, Square, Text, Button, Counter
import pyautogui

# Initialise pygame

pygame.init()
SCREEN = WIDTH, HEIGHT = 288, 512
TILE_WIDTH = WIDTH // 4
TILE_HEIGHT = 130

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
	win = pygame.display.set_mode(SCREEN)
else:
	win = pygame.display.set_mode(SCREEN | pygame.SCALED | pygame.FULLSCREEN)

clock = pygame.time.Clock()
FPS = 30

# Colours

WHITE = (255, 255, 255)
GRAY = (75, 75, 75)
BLUE = (30, 144, 255)
GREEN = (0, 255, 0)  
RED = (50, 50, 255)
BLACK = (0, 0, 0)
PINK = (203, 192, 255)
DARKBLUE = (255, 0, 0)
THICKNESS = 2

# Loading Images

bg_img = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/bg.png')
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

piano_img = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/piano.png')
piano_img = pygame.transform.scale(piano_img, (212, 212))

title_img = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/title.png')
title_img = pygame.transform.scale(title_img, (200, 50))

start_img = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/start.png')
start_img = pygame.transform.scale(start_img, (120, 40))
start_rect = start_img.get_rect(center=(WIDTH//2, HEIGHT-80))

overlay = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/red overlay.png')
overlay = pygame.transform.scale(overlay, (WIDTH, HEIGHT))

# Loading Music
buzzer_fx = pygame.mixer.Sound('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Sounds/piano-buzzer.mp3')

pygame.mixer.music.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Sounds/piano-bgmusic.mp3')
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(loops=-1)

# Loading Fonts 

score_font = pygame.font.Font('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Fonts/Futura condensed.ttf', 32)
title_font = pygame.font.Font('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Fonts/Alternity-8w7J.ttf', 30)
gameover_font = pygame.font.Font('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Fonts/Alternity-8w7J.ttf', 40)

title_img = title_font.render('Piano Tiles', True, WHITE)

# Buttons

close_img = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/closeBtn.png')
replay_img = pygame.image.load('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/replay.png')
sound_off_img = pygame.image.load("/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/soundOffBtn.png")
sound_on_img = pygame.image.load("/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Assets/soundOnBtn.png")

close_btn = Button(close_img, (24, 24), WIDTH // 4 - 18, HEIGHT//2 + 120)
replay_btn = Button(replay_img, (36,36), WIDTH // 2  - 18, HEIGHT//2 + 115)
sound_btn = Button(sound_on_img, (24, 24), WIDTH - WIDTH // 4 - 18, HEIGHT//2 + 120)

# Groups and Objects

tile_group = pygame.sprite.Group()
square_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()

time_counter = Counter(win, gameover_font)

# Helper Functions

def get_speed(score):
	return 200 + 5 * score

def play_notes(notePath):
	pygame.mixer.Sound(notePath).play()

with open('/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/notes.json') as file:
	notes_dict = json.load(file)

# Variables

score = 0
high_score = 0
speed = 0

clicked = False
pos = None

home_page = True
game_page = False
game_over = False
sound_on = True

count = 0
overlay_index = 0

# Loading the model

model = YOLO("/Users/cheka/Documents/Projects/HackandRoll/runs/detect/train4/weights/best.pt")

# Starting up the Webcam

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

running = True
while running:
	pos = None

	ret, frame = cap.read()
	if not ret:
		break

	# Make it a Mirror Image
	frame = cv2.flip(frame, 1)

	# Perform prediction

	results = model(frame, conf = 0.65, device = 'mps')

    # Draw predictions on the frame

	annotated_frame = results[0].plot()

    # Coordinate of Targets

	one_top_left = (500, 500)
	one_bottom_right = (700, 700)
	two_top_left = (702, 500)
	two_bottom_right = (902, 700)
	three_top_left = (904, 500)
	three_bottom_right = (1104, 700)
	four_top_left = (1106, 500)
	four_bottom_right = (1306, 700)

    # Draw the rectangle on the current frame

	cv2.rectangle(annotated_frame, one_top_left, one_bottom_right, GREEN, THICKNESS)
	cv2.rectangle(annotated_frame, two_top_left, two_bottom_right, RED, THICKNESS)
	cv2.rectangle(annotated_frame, three_top_left, three_bottom_right, BLACK, THICKNESS)
	cv2.rectangle(annotated_frame, four_top_left, four_bottom_right, PINK, THICKNESS)

	# Loop through all the objects in the results

	for obj in results[0].boxes.data:
		x1, y1, x2, y2 = obj[:4]  # Coordinates of the bounding box
    
        # Calculate the center of the bounding box

		center_x = (x1 + x2) / 2
		center_y = (y1 + y2) / 2
    
        # Define the size of the small rectangle to draw (adjust size as needed)

		small_rect_width = 20
		small_rect_height = 20
    
        # Calculate the top-left corner of the small rectangle

		small_rect_x1 = int(center_x - small_rect_width / 2)
		small_rect_y1 = int(center_y - small_rect_height / 2)   
    
        # Calculate the bottom-right corner of the small rectangle

		small_rect_x2 = int(center_x + small_rect_width / 2)
		small_rect_y2 = int(center_y + small_rect_height / 2)
    
        # Draw the small rectangle 

		cv2.rectangle(annotated_frame, (small_rect_x1, small_rect_y1), (small_rect_x2, small_rect_y2), (0, 0, 255), 2)

		if center_x < one_top_left[0] + 200 and center_x > one_top_left[0] and center_y < one_bottom_right[1] and center_y > one_bottom_right[1] - 200 and not game_over and game_page:
			pyautogui.click(34, 382)

		elif center_x < two_top_left[0] + 200 and center_x > two_top_left[0] and center_y < two_bottom_right[1] and center_y > two_bottom_right[1] - 200 and not game_over and game_page:
			pyautogui.click(107, 382)
        
		elif center_x < three_top_left[0] + 200 and center_x > three_top_left[0] and center_y < three_bottom_right[1] and center_y > three_bottom_right[1] - 200 and not game_over and game_page:
			pyautogui.click(184, 382)

		elif center_x < four_top_left[0] + 200 and center_x > four_top_left[0] and center_y < four_bottom_right[1] and center_y > four_bottom_right[1] - 200 and not game_over and game_page:
			pyautogui.click(256, 382)

    # Display the frame

	cv2.imshow("Piano Tiles with Webcam", annotated_frame)

    # Break loop on 'q' key press

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

	count += 1
	if count % 100 == 0:
			square = Square(win)
			square_group.add(square)
			counter = 0

	win.blit(bg_img, (0,0))
	square_group.update()

	# Look out for events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE or \
				event.key == pygame.K_q:
				running = False

		if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
			pos = event.pos

	if home_page:
		win.blit(piano_img, (WIDTH//8, HEIGHT//8))
		win.blit(start_img, start_rect)
		win.blit(title_img, (WIDTH // 2 - title_img.get_width() / 2 + 10, 300))

		if pos and start_rect.collidepoint(pos):
			home_page = False
			game_page = True

			x = random.randint(0, 3)
			t = Tile(x * TILE_WIDTH, -TILE_HEIGHT, win)
			tile_group.add(t)

			pos = None

			notes_list = notes_dict['2']
			note_count = 0
			pygame.mixer.set_num_channels(len(notes_list))

	if game_page:
		time_counter.update()
		if time_counter.count <= 0:
			for tile in tile_group:
				tile.update(speed)

				if pos:
					if tile.rect.collidepoint(pos):
						if tile.alive:
							tile.alive = False
							score += 1
							if score >= high_score:
								high_score = score
							

							note = notes_list[note_count].strip()
							th = Thread(target=play_notes, args=(f'/Users/cheka/Documents/Projects/HackandRoll/Game/Piano%20Tiles/Sounds/{note}.ogg', ))
							th.start()
							th.join()
							note_count = (note_count + 1) % len(notes_list)

							tpos = tile.rect.centerx - 10, tile.rect.y
							text = Text('+1', score_font, tpos, win)
							text_group.add(text)

						pos = None

				if tile.rect.bottom >= HEIGHT and tile.alive:
					if not game_over:
						tile.color = (255, 0, 0)
						buzzer_fx.play()
						game_over = True

			if len(tile_group) > 0:
				t = tile_group.sprites()[-1]
				if t.rect.top + speed >= 0:
					x = random.randint(0, 3)
					y = -TILE_HEIGHT - (0 - t.rect.top)
					t = Tile(x * TILE_WIDTH, y, win)
					tile_group.add(t)

			text_group.update(speed)
			img1 = score_font.render(f'Score : {score}', True, WHITE)
			win.blit(img1, (70 - img1.get_width() / 2, 10))
			img2 = score_font.render(f'High : {high_score}', True, WHITE)
			win.blit(img2, (200 - img2.get_width() / 2, 10))
			for i in range(4):
				pygame.draw.line(win, WHITE, (TILE_WIDTH * i, 0), (TILE_WIDTH*i, HEIGHT), 1)

			speed = int(get_speed(score) * (FPS / 1000))

			if game_over:
				speed = 0

				if overlay_index > 20:
					win.blit(overlay, (0,0))

					img1 = gameover_font.render('Game over', True, WHITE)
					img2 = score_font.render(f'Score : {score}', True, WHITE)
					win.blit(img1, (WIDTH // 2 - img1.get_width() / 2, 180))
					win.blit(img2, (WIDTH // 2 - img2.get_width() / 2, 250))

					if close_btn.draw(win):
						running = False

					if replay_btn.draw(win):
						index = random.randint(1, len(notes_dict))
						notes_list = notes_dict[str(index)]
						note_count = 0
						pygame.mixer.set_num_channels(len(notes_list))

						text_group.empty()
						tile_group.empty()
						score = 0
						speed = 0
						overlay_index = 0
						game_over = False

						time_counter = Counter(win, gameover_font)

						x = random.randint(0, 3)
						t = Tile(x * TILE_WIDTH, -TILE_HEIGHT, win)
						tile_group.add(t)

					if sound_btn.draw(win):
						sound_on = not sound_on
				
						if sound_on:
							sound_btn.update_image(sound_on_img)
							pygame.mixer.music.play(loops=-1)
						else:
							sound_btn.update_image(sound_off_img)
							pygame.mixer.music.stop()
				else:
					overlay_index += 1
					if overlay_index % 3 == 0:
						win.blit(overlay, (0,0))

	pygame.draw.rect(win, BLUE, (0,0, WIDTH, HEIGHT), 2)
	clock.tick(FPS)
	pygame.display.update()

pygame.quit()

# Release resources

cap.release()
cv2.destroyAllWindows()