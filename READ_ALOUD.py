import easyocr
import pyttsx3
import requests
from PIL import Image
from io import BytesIO
import logging
import mysql.connector
import speech_recognition as sr

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db_config = {
    'host': "LAPTOP-E8FD7K0H",
    'user': "root",
    'password': "SI41",
    'database': "voice"
}

def get_voice_input(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        engine.say(prompt)
        engine.runAndWait()
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        engine.say("Sorry, I did not understand that.")
        engine.runAndWait()
        return None
    except sr.RequestError:
        engine.say("Sorry, there was an issue with the speech recognition service.")
        engine.runAndWait()
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
            engine.say(extracted_text)
            engine.runAndWait()
        else:
            logging.warning("No text found in the image.")
            print("No text found in the image.")

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        print(f"An error occurred: {str(e)}")

# Main workflow
engine.say("Welcome! Do you want to sign up or log in?")
engine.runAndWait()
action = get_voice_input("Please say 'sign up' or 'log in'.")

if action and action.lower() in ['sign up', 'login']:
    username = get_voice_input("Please say your username.")
    password = get_voice_input("Please say your password.")
    
    if action.lower() == 'sign up':
        if create_user(username, password):
            engine.say("Sign up successful. You can now log in.")
            engine.runAndWait()
        else:
            engine.say("Sign up failed. Please try again.")
            engine.runAndWait()
    elif action.lower() == 'login':
        if authenticate_user(username, password):
            engine.say("Login successful. You can now hear the text from the image.")
            engine.runAndWait()
            image_path = 'https://wallup.net/wp-content/uploads/2018/09/30/912968-quotes-typography-text-quote-motivational-inspirational.jpg'
            read_text(image_path, language='en')
        else:
            engine.say("Login failed. Please check your username and password and try again.")
            engine.runAndWait()
else:
    engine.say("Invalid input. Please restart the program and try again.")
    engine.runAndWait()
