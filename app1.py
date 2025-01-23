from flask import Flask, jsonify, request
import cv2
import pyttsx3
import speech_recognition as sr
import webbrowser
from ultralytics import YOLO
import numpy as np
import wikipedia
import easyocr
import requests
from PIL import Image
from io import BytesIO
import mysql.connector
import logging

app = Flask(__name__)

# Load a smaller, faster YOLOv8 model
model = YOLO('yolov8n.pt')

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Database configuration
db_config = {
    'host': "LAPTOP-E8FD7K0H",
    'user': "root",
    'password': "SI41",
    'database': "voice"
}

# Variable to track if "hey vision" has been said
hey_vision_said = False

# Flag to check if the TTS engine is busy
engine_busy = False

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to speak text using pyttsx3
def speak(text):
    global engine_busy
    if not engine_busy:
        engine_busy = True
        engine.say(text)
        engine.runAndWait()
        engine_busy = False

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
                if label == "person":  # Only detect persons
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

# Function to estimate distance based on bounding box height
def estimate_distance(bbox_height):
    # Dummy function to estimate distance from bounding box height
    # You may replace this with a proper distance estimation function
    focal_length = 615  # example focal length in pixels
    real_height = 1.7  # average height of a person in meters
    distance = (focal_length * real_height) / bbox_height
    return distance

# Function to announce detected persons and their distance
def announce_persons(detected_objects):
    for obj, confidence, bbox in detected_objects:
        _, _, _, h = bbox
        distance = estimate_distance(h)
        announcement = f"Detected a person at approximately {distance:.2f} meters away"
        speak(announcement)

# Function to recognize voice commands
def recognize_voice():
    global hey_vision_said
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            print("Listening for command...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                if "hey vision" in command.lower() and not hey_vision_said:
                    print("Hey Vision activated!")
                    speak("Hey Vision activated!")
                    hey_vision_said = True
                    continue
                elif hey_vision_said:
                    return command.lower()
            except sr.UnknownValueError:
                speak("Could not understand the command.")
            except sr.RequestError:
                speak("Could not request results; check your network connection.")
    return ""

# Function to open social media
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

# Function to open a website
def open_website(website):
    url = f"http://{website}" if not website.startswith("http") else website
    webbrowser.open(url)
    speak(f"Opening {website}")

# Function to search on Wikipedia
def search(query):
    try:
        result = wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        result = str(e)
    except wikipedia.exceptions.PageError:
        result = "Sorry, I couldn't find any results."
    return result

# Function to extract text from image
def read_text(image_path, language='en'):
    try:
        # Load the image
        if image_path.startswith('http'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_path)
        
        # Initialize EasyOCR reader
        reader = easyocr.Reader([language])
        result = reader.readtext(image)
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
        speak("An error occurred while reading the text from the image.")

# Function to handle user creation
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

# Function to authenticate user
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

# Route to handle voice commands
@app.route('/voice_command', methods=['POST'])
def process_voice_command():
    global hey_vision_said
    command = recognize_voice()
    response = ""

    if hey_vision_said:
        if "open" in command:
            platform = command.replace("open", "").strip()
            open_social_media(platform)
            response = f"Opening {platform}"
        elif "detect objects" in command:
            response = "Object detection activated!"
            # Start object detection
            ip_webcam_url = "http://192.168.43.1:8080/video"  # Replace with your IP webcam URL
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
                    cv2.imshow("Detected Objects", frame_with_boxes)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                else:
                    response = "No persons detected."
                    speak(response)
            else:
                response = "Failed to capture frame from video stream."
                speak(response)
            cap.release()
        elif "search" in command:
            query = command.replace("search", "").strip()
            result = search(query)
            speak(result)
            response = result
        elif "read text from image" in command:
            image_path = request.json.get('image_path')
            read_text(image_path)
            response = "Reading text from image"
        else:
            response = "Command not recognized."
            speak(response)
    else:
        response = "Please say 'Hey Vision' to activate the system."

    return jsonify({'response': response})

# Route to handle user creation
@app.route('/create_user', methods=['POST'])
def handle_create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if create_user(username, password):
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'message': 'Failed to create user'}), 500

# Route to handle user authentication
@app.route('/login', methods=['POST'])
def handle_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if authenticate_user(username, password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)
