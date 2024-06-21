import speech_recognition as sr
import spacy

# Load the spaCy NER model
NER = spacy.load("en_core_web_lg")

# Load the punctuation restoration model

def listen_and_process():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        print("Listening...")
        audio_data = recognizer.listen(source)

    try:
        # Recognize speech using Google's speech recognition
        text = recognizer.recognize_google(audio_data)
        print("Raw transcription:", text)

        # Restore punctuation
        # Process the punctuated text with spaCy's NER
        formatted_text = NER(text)
        for entity in formatted_text.ents:
            print(f"{entity.text} ({entity.label_})")

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")

# Main loop to continuously listen and process speech
listen_and_process()