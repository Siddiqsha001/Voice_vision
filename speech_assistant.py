import pyttsx3
import speech_recognition as sr
import wikipedia


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

def main():
    speak("Welcome. How can I assist you today?")
    while True:
        command = query().lower()
        if "exit" in command or "quit" in command or "bye" in command:
            speak("Goodbye!")
            break
        elif "search" in command:
            speak("What would you like to search for?")
            topic = query()
            if topic:
                result = search(topic)
                speak(result)
        else:
            speak("Sorry, I can't help with that.")

if __name__ == "__main__":
    main()
