import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import requests

engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print(f"Proton 🔙: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        print("🧠 Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"🧒 You said: {query}")
    except sr.UnknownValueError:
        speak("Sorry, I didn’t get that. Please repeat.")
        return ""
    except sr.RequestError:
        speak("Network error. Check your connection.")
        return ""
    return query.lower()

def launch_gesture_recognition():
    try:
        response = requests.get("http://127.0.0.1:8000/start")
        if response.status_code == 200:
            speak("Launching gesture recognition.")
        else:
            speak("Failed to launch gesture recognition.")
    except:
        speak("Unable to connect to gesture system.")

def stop_gesture_recognition():
    try:
        response = requests.get("http://127.0.0.1:8000/stop")
        if response.status_code == 200:
            speak("Stopped gesture recognition.")
        else:
            speak("Failed to stop gesture recognition.")
    except:
        speak("Unable to connect to gesture system.")

def google_search(query):
    url = f"https://www.google.com/search?q={query}"
    speak(f"Searching Google for {query}")
    webbrowser.open(url)

def find_location(place):
    url = f"https://www.google.com/maps/place/{place.replace(' ', '+')}"
    speak(f"Finding location: {place}")
    webbrowser.open(url)

def get_datetime():
    now = datetime.datetime.now()
    speak(f"The current date is {now.strftime('%B %d, %Y')} and the time is {now.strftime('%I:%M %p')}")

def navigate_files():
    speak("Opening file explorer.")
    os.startfile("explorer.exe")

def copy_text():
    speak("Copied text.")
    os.system('echo off | clip')

def paste_text():
    speak("Pasting text.")
    os.system('powershell Get-Clipboard')

def main():
    speak("Hello, I am Proton, your voice assistant.")
    active = True

    while True:
        if active:
            query = take_command()
            if not query:
                continue

            if "launch gesture" in query or "open gesture" in query:
                launch_gesture_recognition()

            elif "stop gesture" in query:
                stop_gesture_recognition()

            elif "search google for" in query:
                google_search(query.replace("search google for", "").strip())

            elif "find location" in query:
                place = query.replace("find location", "").strip()
                find_location(place)

            elif "open file explorer" in query or "navigate files" in query:
                navigate_files()

            elif "what's the time" in query or "date" in query:
                get_datetime()

            elif "copy" in query:
                copy_text()

            elif "paste" in query:
                paste_text()

            elif "sleep" in query or "stop listening" in query:
                speak("Sleeping. Say 'wake up' to activate me again.")
                active = False

            elif "exit" in query or "goodbye" in query:
                speak("Goodbye. Have a nice day!")
                break

            else:
                speak("Sorry, I didn't understand that command.")

        else:
            query = take_command()
            if "wake up" in query:
                speak("I am back online.")
                active = True

if __name__ == "__main__":
    main()
