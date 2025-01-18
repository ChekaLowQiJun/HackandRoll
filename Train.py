from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model.train(data='/Users/cheka/Documents/Projects/HackandRoll/training_data/HandDetection.v1i.yolov8/data.yaml', epochs = 30, patience = 5, save = True, device = 'mps')