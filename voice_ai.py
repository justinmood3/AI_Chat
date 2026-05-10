import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()
r = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        audio = r.listen(source)
        return r.recognize_google(audio)