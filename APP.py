from flask import Flask, render_template, jsonify, request
import cv2
import pyttsx3
import speech_recognition as sr
import webbrowser
from ultralytics import YOLO
import numpy as np
import wikipedia
import base64  #binary to text(encoding)
import easyocr
import requests
from PIL import Image
from io import BytesIO
import logging
import mysql.connector

app = Flask(__name__)

model = YOLO('yolov8n.pt') 
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
recognizer = sr.Recognizer()
hey_vision_said = False

engine_busy = False
db_config = {
    'host': "LAPTOP-E8FD7K0H",
    'user': "root",
    'password': "SI41",
    'database': "voice"
}

#logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
def draw_boxes(frame, detected_objects):
    for obj, confidence, bbox in detected_objects:
        x, y, w, h = bbox
        color = (0, 255, 0) 
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"{obj}: {confidence:.2f}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
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
    global engine_busy
    if not engine_busy:
        engine_busy = True
        engine.say(text)
        engine.runAndWait()
        engine_busy = False
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
                return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the command.")
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

def get_voice_input(prompt):
    with sr.Microphone() as source:
        speak(prompt)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, there was an issue with the speech recognition service.")
        return None
def create_user(username, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        logging.error("Error: %s", err)
        return False
def authenticate_user(username, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and result[0] == password:
            return True
        else:
            return False
    except mysql.connector.Error as err:
        logging.error("Error: %s", err)
        return False
def read_text(image_path, language='en'):
    try:
        if image_path.startswith('http'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_path)
        image = image.convert('RGB')
        reader = easyocr.Reader([language])
        result = reader.readtext(np.array(image))

        extracted_text = ' '.join([text[1] for text in result])

        if extracted_text:
            logging.info("Extracted Text: %s", extracted_text)
            print("Extracted Text:", extracted_text)
            speak(extracted_text)
        else:
            logging.warning("No text found in the image.")
            print("No text found in the image.")
            speak("No text found in the image.")
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        print(f"An error occurred: {str(e)}")
        speak(f"An error occurred: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_command', methods=['POST'])
def process_command():
    global hey_vision_said
    command = request.json['command']
    response = ""

    if hey_vision_said:
        if "open" in command:
            platform = command.replace("open", "").strip()
            open_social_media(platform)
            response = f"Opening {platform}"
        elif "detect objects" in command:
            response = "Object detection activated!"
            ip_webcam_url = "http://192.168.43.1:8080/video" 
            cap = cv2.VideoCapture(ip_webcam_url)
            if not cap.isOpened():
                response = "Unable to open video stream"
                speak(response)
                return jsonify({'response': response})

            ret, frame = cap.read()
            if ret:
                resized_frame = cv2.resize(frame, (640, 480))
                detected_objects = detect_objects(resized_frame)

                if detected_objects:
                    announce_persons(detected_objects)
                    frame_with_boxes = draw_boxes(resized_frame, detected_objects)

                    _, buffer = cv2.imencode('.jpg', frame_with_boxes)
                    encoded_image = base64.b64encode(buffer).decode('utf-8')
                    response = f"data:image/jpeg;base64,{encoded_image}"
                else:
                    speak("No persons detected.")
                    response = "No persons detected."
            else:
                response = "Unable to read video stream"

            cap.release()
        elif "bye" in command:
            response = "Goodbye!"
            speak(response)
            return jsonify({'response': response, 'close_tab': True})
        elif "extract" in command:
            response = "Reading text from the image."
            image_path = 'https://wallup.net/wp-content/uploads/2018/09/30/912968-quotes-typography-text-quote-motivational-inspirational.jpg'
            read_text(image_path, language='en')
        else:
            response = search(command)
            speak(response)
    elif "hey vision" in command:
        hey_vision_said = True
        response = "Hey Vision activated!"
        speak(response)

    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
