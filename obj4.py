import cv2
from ultralytics import YOLO
import numpy as np

# Load YOLOv8 model
model = YOLO('yolov8x.pt')  # Use a more accurate model like yolov8x.pt

# Function to perform object detection
def detect_objects(frame):
    results = model(frame)
    detected_objects = []

    for result in results:
        boxes = result.boxes.data.numpy()  # Get bounding boxes
        for box in boxes:
            x1, y1, x2, y2, score, class_id = box
            if score > 0.5:  # Confidence threshold
                label = model.names[int(class_id)]
                detected_objects.append((label, score, (int(x1), int(y1), int(x2-x1), int(y2-y1))))
    
    return detected_objects

# Function to draw bounding boxes and labels on the image
def draw_boxes(frame, detected_objects):
    for obj, confidence, bbox in detected_objects:
        x, y, w, h = bbox
        color = (0, 255, 0)  # Green color for bounding boxes
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{obj}: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

# Main function to perform object detection on a video feed
def main():
    cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide path to video file

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        detected_objects = detect_objects(frame)
        frame_with_boxes = draw_boxes(frame, detected_objects)
        
        cv2.imshow('Object Detection', frame_with_boxes)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
