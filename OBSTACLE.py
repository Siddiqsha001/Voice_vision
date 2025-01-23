import cv2
import pyttsx3
import numpy as np
import threading
import time
import speech_recognition as sr

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

engine_busy = False

ip_webcam_url = "http://172.17.24.188:8080/video"

def detect_obstacle_in_frame(frame):
    # Dummy logic for obstacle detection
    obstacle_detected = False
    direction = None

    # Example: Simulate obstacle detection
    if np.random.rand() < 0.3:  # 30% chance of detecting an obstacle
        obstacle_detected = True
        if np.random.rand() < 0.5:
            direction = "left"
        else:
            direction = "right"

    return obstacle_detected, direction

# Function to speak text using pyttsx3
def speak(text):
    global engine_busy
    if not engine_busy:
        engine_busy = True
        engine.say(text)
        engine.runAndWait()
        engine_busy = False  # Reset the flag after speaking

# Function to listen for voice commands
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source, timeout=5)  # Timeout after 5 seconds of silence
        try:
            command = recognizer.recognize_google(audio)
            print(f"Recognized command: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the command.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return None

# Continuously listen for voice commands and perform obstacle detection
while True:
    command = listen_for_command()
    if command is not None:
        if "stop" in command:
            break
        else:
            cap = cv2.VideoCapture(ip_webcam_url)
            ret, frame = cap.read()
            if ret:
                obstacle_detected, direction = detect_obstacle_in_frame(frame)
                if obstacle_detected:
                    if direction == "left":
                        response = "Obstacle detected on the left. Please go right."
                        speak(response)
                    elif direction == "right":
                        response = "Obstacle detected on the right. Please go left."
                        speak(response)
                    else:
                        response = "Unknown obstacle direction. Please take precaution."
                        speak(response)
                else:
                    response = "No obstacle detected. Continue on the current route."
                    speak(response)
                print(response)
                cap.release()
            else:
                speak("Error: Unable to access camera. Please check the camera connection.")
