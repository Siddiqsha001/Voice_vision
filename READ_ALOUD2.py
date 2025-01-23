import easyocr
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)  
engine.setProperty('volume', 1.0)  

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  

def read_text(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    extracted_text = ' '.join([text[1] for text in result])

    if extracted_text:
        print("Extracted Text:", extracted_text)
        engine.say(extracted_text)
        engine.runAndWait()
    else:
        print("No text found in the image.")
image_path = 'https://tse3.mm.bing.net/th?id=OIP.umhHDYDoEvxMhbLdw6qMGQHaEK&pid=Api&P=0&h=180'
read_text(image_path)