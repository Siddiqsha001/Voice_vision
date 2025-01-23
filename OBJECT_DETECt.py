import cv2
import pyttsx3
import speech_recognition as sr
import webbrowser
from ultralytics import YOLO
import numpy as np
import wikipedia

model = YOLO('yolov8n.pt') 

engine = pyttsx3.init()

recognizer = sr.Recognizer()

hey_vision_said = False

def detect_objects(frame):
    results = model(frame)
    detected_objects = []

    for result in results:
        boxes = result.boxes.data.numpy() 
        for box in boxes:
            x1, y1, x2, y2, score, class_id = box
            if score > 0.5:  
                label = model.names[int(class_id)]
                if label == "person":  
                    detected_objects.append((label, score, (int(x1), int(y1), int(x2-x1), int(y2-y1))))
    
    return detected_objects


def estimate_distance(bbox_height):
   
    focal_length = 615 
    real_height = 1.7 
    distance = (focal_length * real_height) / bbox_height
    return distance


def announce_persons(detected_objects):
    for obj, confidence, bbox in detected_objects:
        _, _, _, h = bbox
        distance = estimate_distance(h)
        announcement = f"Detected a person at approximately {distance:.2f} meters away"
        speak(announcement)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def recognize_voice():
    global hey_vision_said
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            if "hey vision" in command.lower() and not hey_vision_said:
                print("Hey Vision activated!")
                speak("Hey Vision activated!")
                hey_vision_said = True
                return recognize_voice()
            elif hey_vision_said:
                print("Activate through keyword")
                return command.lower()
        except sr.UnknownValueError:
            print("Could not request results; check your network connection.")
        except sr.RequestError:
            print("Could not request results; check your network connection.")
    return ""

def open_social_media(platform):
    urls = {
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
        "snapchat": "https://www.snapchat.com",
        "tiktok": "https://www.tiktok.com",
        "pinterest": "https://www.pinterest.com",
        "reddit": "https://www.reddit.com",
        "tumblr": "https://www.tumblr.com",
        "whatsapp": "https://web.whatsapp.com",
        "telegram": "https://web.telegram.org",
        "youtube": "https://www.youtube.com",
    }
    url = urls.get(platform.lower())
    if url:
        webbrowser.open(url)
        speak(f"Opening {platform}")
    else:
        speak(f"Sorry, I can't open {platform}")
def open_website(website):
    url = f"http://{website}" if not website.startswith("http") else website
    webbrowser.open(url)
    speak(f"Opening {website}")

def search(query):
    try:
        result = wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        result = str(e)
    except wikipedia.exceptions.PageError:
        result = "Sorry, I couldn't find any results."
    return result

def main():
    speak("Welcome. How can I assist you today?")
    while True:
        command = recognize_voice().lower()
        if "objects" in command:
            ip_webcam_url = "http://172.20.10.4:8080/video"  
            cap = cv2.VideoCapture(ip_webcam_url)
            if not cap.isOpened():
                print("Error: Unable to open video stream")
                speak("Unable to open video stream")
                continue

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Unable to read frame")
                    cap.release()
                    break  

                resized_frame = cv2.resize(frame, (640, 480))  
                detected_objects = detect_objects(resized_frame)

                print(f"Detected objects: {detected_objects}") 

                if detected_objects:
                    for obj, confidence, bbox in detected_objects:
                        print(f"Detected {obj} with confidence {confidence:.2f}")
                    announce_persons(detected_objects)
                else:
                    speak("No persons detected.")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

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