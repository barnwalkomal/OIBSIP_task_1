import speech_recognition as sr
import traceback
try:
    with sr.Microphone() as source:
        print("Mic created")
except Exception as e:
    traceback.print_exc()
