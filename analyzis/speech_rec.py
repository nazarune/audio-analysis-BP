import speech_recognition as sr

def transcribe(audio_file, locale):
    filename = audio_file
    results = {'file': filename}

    r = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)  # Load audio to memory
        try:
            results['text'] = r.recognize_google(audio_data, language=locale)  # Convert from speech to text
        except: 
            results['text'] = "can't transcribe or not detected"

    return results
