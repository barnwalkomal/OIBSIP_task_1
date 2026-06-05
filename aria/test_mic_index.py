import speech_recognition as sr

try:
    with sr.Microphone() as source:
        print("Mic created with NO index")
except Exception as e:
    import traceback
    traceback.print_exc()
