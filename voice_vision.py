import cv2
import numpy as np
import time
import pyttsx3
from flask import Flask, Response

app = Flask(__name__)

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Load YOLO model
def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")  # Make sure these files are in your working directory
    with open("coco.names", "r") as f:  # Ensure coco.names is in your working directory
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    return net, classes, output_layers

# Detect objects in the frame
def detect_objects(frame, net, output_layers, classes):
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    return class_ids, confidences, boxes

# Function to speak detected object
def speak_object(class_ids, classes):
    if class_ids:
        object_name = classes[class_ids[0]]
        engine.say(f"Object detected: {object_name}")
        engine.runAndWait()

# Flask route to stream video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_video():
    net, classes, output_layers = load_yolo()

    cap = cv2.VideoCapture(0)  # Use the webcam

    last_detection_time = 0  # To control the 5 seconds gap
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Detect objects every 5 seconds
        current_time = time.time()
        if current_time - last_detection_time > 5:
            class_ids, confidences, boxes = detect_objects(frame, net, output_layers, classes)
            speak_object(class_ids, classes)
            last_detection_time = current_time

        # Show the frame
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

if __name__ == "__main__":
    app.run(host='172.20.10.4', port=8080, threaded=True)

