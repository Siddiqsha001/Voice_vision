import pyttsx3
import speech_recognition as sr
import wikipedia
import webbrowser

def speak(string):
    engine = pyttsx3.init()
    engine.say(string)
    engine.runAndWait()

def query():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return ""

def search(string):
    try:
        summary = wikipedia.summary(string, sentences=1)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return "There are multiple entries for this term. Please be more specific."
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find any information on that topic."

def open_social_media(platform):
    if platform == "instagram":
        webbrowser.open("https://www.instagram.com/")  
    elif platform == "whatsapp":
        webbrowser.open("https://web.whatsapp.com/") 
    elif platform == "linkedin":
        webbrowser.open("https://www.linkedin.com/")  
    elif platform == "email":
        webbrowser.open("mailto:")  
    elif platform == "telegram":
        webbrowser.open("https://web.telegram.org/") 
    elif platform == "youtube":
        webbrowser.open("https://www.youtube.com/")  
    else:
        speak("Sorry, I can't open that social media platform.")

def open_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        speak(f"Opening {url}")
    except Exception as e:
        speak(f"Sorry, I couldn't open {url}")

def main():
    speak("Welcome. How can I assist you today?")
    while True:
        command = query().lower()
        if "exit" in command or "quit" in command or "bye" in command:
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
