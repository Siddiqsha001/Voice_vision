import cv2
import numpy as np
import time
import pyttsx3
import speech_recognition as sr
from flask import Flask, Response

app = Flask(__name__)

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Function to speak text using pyttsx3
def speak(text):
    engine.say(text)
    engine.runAndWait()

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

# Function to recognize voice command
def recognize_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Sorry, the speech service is unavailable.")
            return ""

# Main function
def main():
    speak("Welcome. How can I assist you today?")
    while True:
        command = recognize_voice().lower()
        if "objects" in command:
            ip_webcam_url = "http://172.20.10.4:8080/video"  # Replace with your webcam's URL
            cap = cv2.VideoCapture(ip_webcam_url)
            if not cap.isOpened():
                print("Error: Unable to open video stream")
                speak("Unable to open video stream")
                continue

            net, classes, output_layers = load_yolo()
            last_detection_time = 0  # To control the 5 seconds gap

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Unable to read frame")
                    cap.release()
                    break

                # Detect objects every 5 seconds
                current_time = time.time()
                if current_time - last_detection_time > 5:
                    class_ids, confidences, boxes = detect_objects(frame, net, output_layers, classes)
                    speak_object(class_ids, classes)
                    last_detection_time = current_time

                # Show the frame (optional)
                cv2.imshow("Object Detection", frame)

                # Break loop if user says 'exit' or 'quit'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

# Function to speak detected object
def speak_object(class_ids, classes):
    if class_ids:
        object_name = classes[class_ids[0]]
        speak(f"Object detected: {object_name}")

if __name__ == "__main__":
    main()