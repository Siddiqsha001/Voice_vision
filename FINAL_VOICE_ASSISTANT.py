import cv2
import pyttsx3
import speech_recognition as sr
import wikipedia
import webbrowser
from ultralytics import YOLO
import numpy as np

from Colour_desc import speak
from obj2 import open_social_media, open_website, search

# Load a smaller, faster YOLOv8 model
model = YOLO('yolov8n.pt')  # Use yolov8n.pt for a faster model

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Variable to track if "hey vision" has been said
hey_vision_said = False

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
    global hey_vision_said
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            if "hey vision" in command.lower() and not hey_vision_said:
                print("Hey Vision activated!")
                engine.say("Hey Vision activated!")
                engine.runAndWait()
                hey_vision_said = True
                return recognize_voice()
            elif hey_vision_said:
                print(f"You said: {command}")
                return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the command.")
        except sr.RequestError:
            print("Could not request results; check your network connection.")
    return ""

# Main function to perform object detection
def main():
    speak("Welcome. How can I assist you today?")
    while True:
        command = recognize_voice().lower()
        if "objects" in command:
            cap = cv2.VideoCapture(0)  # Use 0 for webcam, or provide path to video file
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
            
            cap.release()

        elif "exit" in command or "quit" in command or "bye" in command:
            speak("Goodbye!")
            break
        elif "open" in command:
            platform = command.replace("open", "").strip()
            open_social_media(platform)
        elif "go to" in command:
            website = command.replace("go to", "").strip()
            open_website(website)
        else:
            if command:
                result = search(command)
                speak(result)
            else:
                speak("Please ask a question.")

if __name__ == "__main__":
    main()
