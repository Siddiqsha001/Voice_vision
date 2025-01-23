import cv2
import pyttsx3
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

engine = pyttsx3.init()

def detect_objects(image):
    detected_objects = [("person", (100, 100, 200, 200))]  
    return detected_objects

def get_dominant_color(image, bbox):
    x, y, w, h = bbox
    roi = image[y:y+h, x:x+w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    roi = roi.reshape((roi.shape[0] * roi.shape[1], 3))
    
    kmeans = KMeans(n_clusters=1)
    kmeans.fit(roi)
    dominant_color = kmeans.cluster_centers_[0].astype(int)
    
    return dominant_color

def color_to_text(color):
    r, g, b = color
    color_names = {
        'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
        'yellow': (255, 255, 0), 'magenta': (255, 0, 255), 'cyan': (0, 255, 255),
        'white': (255, 255, 255), 'black': (0, 0, 0), 'gray': (128, 128, 128),
        'maroon': (128, 0, 0), 'olive': (128, 128, 0), 'dark green': (0, 128, 0),
        'purple': (128, 0, 128), 'teal': (0, 128, 128), 'navy': (0, 0, 128),
        'orange': (255, 165, 0), 'pink': (255, 192, 203), 'brown': (165, 42, 42)
    }

    closest_color_name = 'unknown color'
    min_distance = float('inf')

    for name, rgb in color_names.items():
        distance = np.sqrt((r - rgb[0])**2 + (g - rgb[1])**2 + (b - rgb[2])**2)
        if distance < min_distance:
            min_distance = distance
            closest_color_name = name

    return closest_color_name

def generate_description(detected_objects, frame):
    descriptions = []
    for obj, bbox in detected_objects:
        dominant_color = get_dominant_color(frame, bbox)
        color_text = color_to_text(dominant_color)
        description = f"A {obj} is detected wearing {color_text}."
        descriptions.append(description)
    return descriptions

def speak(text):
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        detected_objects = detect_objects(frame)
        
        descriptions = generate_description(detected_objects, frame)
        
        for description in descriptions:
            speak(description)
        
        cv2.imshow('Frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
