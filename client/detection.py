from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator

model = YOLO('yolov5nu.pt')

def detection(frame) :
    results = model(frame, verbose=False, stream=True)
    annotator = Annotator(frame)
    for r in results:
        for box in r.boxes:
            annotator.box_label(box.xyxy[0], f"{r.names[int(box.cls)]} {float(box.conf):.2}")