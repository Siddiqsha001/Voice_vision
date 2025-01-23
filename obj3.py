import cv2
from ultralytics import YOLO
import numpy as np
import pyttsx3
import speech_recognition as sr

# Load a smaller, faster YOLOv8 model
model = YOLO('yolov8n.pt')  # Use yolov8n.pt for a faster model

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Initialize speech recognizer
recognizer = sr.Recognizer()

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

# Function to announce detected objects
def announce_objects(detected_objects):
    for obj, confidence, bbox in detected_objects:
        announcement = f"Detected {obj} with confidence {confidence:.2f}"
        engine.say(announcement)
    engine.runAndWait()

# Function to recognize voice commands
def recognize_voice():
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the command.")
        except sr.RequestError:
            print("Could not request results; check your network connection.")
    return ""

# Main function to perform object detection
def main():
    cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide path to video file

    while True:
        command = recognize_voice()
        if "objects" in command:
            ret, frame = cap.read()
            if not ret:
                break
            
            resized_frame = cv2.resize(frame, (640, 480))  # Resize frame for faster processing
            detected_objects = detect_objects(resized_frame)
            
            if detected_objects:
                for obj, confidence, bbox in detected_objects:
                    print(f"Detected {obj} with confidence {confidence:.2f}")
                announce_objects(detected_objects)
            else:
                engine.say("No objects detected.")
                engine.runAndWait()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
