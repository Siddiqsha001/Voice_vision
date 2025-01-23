import cv2
import pyttsx3
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

engine = pyttsx3.init()

def detect_objects(image):
    detected_objects = [("person", (100, 100, 200, 200))]  
    return detected_objects

def get_colors(image, bbox, k=5):
    x, y, w, h = bbox
    roi = image[y:y+h, x:x+w]
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    roi = roi.reshape((roi.shape[0] * roi.shape[1], 3))
    
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(roi)
    colors = kmeans.cluster_centers_.astype(int)
    counts = Counter(kmeans.labels_)
    
    return colors, counts

def color_to_text(color):
    # Convert RGB to HEX
    r, g, b = color
    hex_color = f'#{r:02x}{g:02x}{b:02x}'
    
    # Use a simple dictionary to map HEX to color names (extend this as needed)
    color_names = {
        '#ff0000': 'red', '#00ff00': 'green', '#0000ff': 'blue', 
        '#ffff00': 'yellow', '#ff00ff': 'magenta', '#00ffff': 'cyan',
        '#ffffff': 'white', '#000000': 'black', '#808080': 'gray',
        '#800000': 'maroon', '#808000': 'olive', '#008000': 'dark green',
        '#800080': 'purple', '#008080': 'teal', '#000080': 'navy',
        # Add more colors as needed
    }
    
    # Find the closest color name by converting to LAB color space
    min_distance = float('inf')
    closest_color_name = 'unknown color'
    
    for hex_val, name in color_names.items():
        hr, hg, hb = tuple(int(hex_val[i:i+2], 16) for i in (1, 3, 5))
        distance = np.sqrt((r - hr)**2 + (g - hg)**2 + (b - hb)**2)
        
        if distance < min_distance:
            min_distance = distance
            closest_color_name = name
    
    return closest_color_name

def generate_description(detected_objects, frame):
    descriptions = []
    for obj, bbox in detected_objects:
        colors, counts = get_colors(frame, bbox)
        color_descriptions = []
        for color, count in zip(colors, counts):
            color_text = color_to_text(color)
            if color_text not in color_descriptions:
                color_descriptions.append(color_text)
        
        color_description = ', '.join(color_descriptions)
        description = f"A {obj} is detected wearing {color_description}."
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
