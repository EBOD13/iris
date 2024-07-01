import time

import torch
import random
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine
import json
import nltk
import spacy
import re
import pickle
import speech_recognition as sr
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import numpy as np
from spotify_player import SpotifyPlayer


class Chatbot:
    def __init__(self, model_path, intents_path, words_path, classes_path):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.model = load_model(model_path)
        self.intents = json.loads(open(intents_path).read())
        self.words = pickle.load(open(words_path, 'rb'))
        self.classes = pickle.load(open(classes_path, 'rb'))
        self.lemmatizer = WordNetLemmatizer()
        self.spotifyplayer = SpotifyPlayer()
        self.NER = spacy.load("en_core_web_lg")
        self.recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Adjusting for ambient noise, please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=5)
        print("Iris is ready to listen...")

    def get_time_context(self, text):
        time_context = ["next", "last"]
        time_frames = ["today", "tomorrow", "month", "night", "yesterday", "week", "monday", "tuesday", "wednesday",
                       "thursday", "friday", "saturday", "sunday", "month"]
        time_word_found = word_tokenize(text.lower())
        combined_word = ""
        for word in time_word_found:
            if word in time_context:
                combined_word += word
            if word in time_frames:
                combined_word += " " + word
        return combined_word.strip()

    def get_bert_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        return outputs['last_hidden_state'].squeeze(0).mean(dim=0).numpy()

    def cosine_similarity_bert(self, s1, s2):
        emb1 = self.get_bert_embedding(s1)
        emb2 = self.get_bert_embedding(s2)
        return 1 - cosine(emb1, emb2)

    def check_similarity(self, intent_tag, user_input):
        max_similarity = 0
        level = "Very bad"  # Default level

        for intent in self.intents['intents']:
            if intent['tag'] == intent_tag:
                for pattern in intent['patterns']:
                    similarity = self.cosine_similarity_bert(user_input, pattern)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        # Check conditions for playing the song
                        if intent['tag'] in ["play_asked_song", "play_random_song"] and max_similarity >= 0.78234:
                            try:
                                # playsound(song)
                                level = "Playing song"
                            except Exception as e:
                                print(f"Failed to play sound: {e}")
                        else:
                            level = "Very bad"

        return f"{level}: {max_similarity}"

    def play_from_spotify(self, text_input):
        intents_list = self.predict_class(text_input)
        if intents_list[0]['intent'] == "play_random_song":
            self.spotifyplayer.play_random_track()
        elif intents_list[0]['intent'] == "play_random_song_by_artist":
            pattern = r'\b(?:by|from)\s*(.*)'
            matches = re.findall(pattern, text_input, flags=re.IGNORECASE)
            if matches:
                self.spotifyplayer.play_song_by_artist(matches[0].strip())
            else:
                print("No match found")
        elif intents_list[0]['intent'] == "pause_track":
            self.spotifyplayer.pause_track()
        elif intents_list[0]['intent'] == "resume_track":
            self.spotifyplayer.resume_track()
        return

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bow(self, sentence, words, show_details=True):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for s in sentence_words:
            for i, w in enumerate(words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print(f"Found in bag: {w}")
        return np.array(bag)

    def predict_class(self, sentence):
        p = self.bow(sentence, self.words, show_details=False)
        res = self.model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.28
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = [{"intent": self.classes[r[0]], "probability": str(r[1])} for r in results]
        return return_list

    def get_response(self, intents_list):
        tag = intents_list[0]['intent']
        for intent in self.intents['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
        return "I'm not sure how to respond to that."

    def chatbot_response(self, text):
        intents_list = self.predict_class(text)
        response = self.get_response(intents_list)
        return intents_list, response

    def listen_and_process(self):
        with sr.Microphone() as source:
            print("Listening for 'Iris'...")
            while True:
                audio_data = self.recognizer.listen(source, phrase_time_limit=3)
                try:
                    text = self.recognizer.recognize_google(audio_data)
                    activation_keys = self.intents['intents'][0]['patterns']
                    if any(key in text.lower() for key in activation_keys):
                        print("Keyword detected. Listening for commands...")
                        break
                except sr.UnknownValueError:
                    print("Waiting for the keyword 'Iris'...")
                    time.sleep(5)

        print("Keyword detected. Now fully activating speech recognition...")
        with sr.Microphone() as source:
            audio_data = self.recognizer.listen(source, phrase_time_limit=5)
            try:
                text = self.recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
                return None


if __name__ == "__main__":
    chatbot = Chatbot('../data/training/chatbot_model.h5',
                      '../data/dataset/inputs.json',
                      '../data/training/words.pkl',
                      '../data/training/classes.pkl')
    start = True

    while start:
        query = chatbot.listen_and_process()
        if query:
            try:
                intents, response = chatbot.chatbot_response(query)
                print(chatbot.play_from_spotify(query))
                print(f"Intention: {intents[0]['intent']}")
                print(response.capitalize())
            except Exception as e:
                print(f'Error: {e}')
                print('You may need to rephrase your question.')
