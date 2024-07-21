import os
import google.generativeai as genai
from dotenv import load_dotenv
import re
import time
import ast
import speech_recognition as sr
import threading
from spotify_player import SpotifyPlayer
from speech_transcriber import Recorder
import simpleaudio as sa
from elevenlabs import play
from elevenlabs.client import ElevenLabs


# Load the .env where all the API Keys are located
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.environ["GEMINI_API"])

class IrisChat:
    def __init__(self):
        self.spotifyplayer = SpotifyPlayer()
        self.record = Recorder()
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            system_instruction="You are my personal assistant capable of performing many tasks. "
                               "Your name is Iris and you will refer to me as Mr. Daniel in a polite manner. "
                               "When prompted to perform an action related to music, you will identify the intent of "
                               "the prompt as either 'pause_track', 'resume_track', 'play_next_track', "
                               "'play_previous_track', 'play_random_song_by_artist', 'play_random_song' or "
                               "'play_specific_song', whereby you should only respond with the name of the artist, "
                               "song and the intent as a python list that looks like this: ['artist_name', 'song', "
                               "'intent']. If there is no song or artist, the list should have the value of None. "
                               "Just return the list. You can also answer any other questions accordingly."
        )
        self.recognizer = sr.Recognizer()
        self.history = []
        self.artist = ''
        self.song = ''
        self.intent_methods = {
            'play_random_song': self.spotifyplayer.play_random_saved_track,
            'resume_track': self.spotifyplayer.resume_track,
            'pause_track': self.spotifyplayer.pause_track,
            'play_next_track': self.spotifyplayer.play_next_track,
            'play_previous_track': self.spotifyplayer.play_previous_track,
            'play_random_song_by_artist': lambda artist: self.spotifyplayer.play_song_by_artist(artist),
            'play_specific_song': lambda song: self.spotifyplayer.play_given_song(song)
        }

    def text_to_speech(self, response):
        client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"), # Defaults to ELEVEN_API_KEY
        )

        audio = client.generate(
            text=response,
            voice="Grace",
            model="eleven_multilingual_v2"
        )
        play(audio)

    def get_music_intent(self, text_input):
        pattern = r'^\[.*\]$'
        match = re.match(pattern, text_input.strip())
        if match:
            parsed_list = ast.literal_eval(text_input)
            response = None
            result = {'artist': parsed_list[0],
                      'song': parsed_list[1],
                      'intent': parsed_list[2]}
            self.song = result['song']
            self.artist = result['artist']
            music_intent = result['intent']
            if music_intent in self.intent_methods:
                if music_intent == 'play_random_song_by_artist':
                    response = self.intent_methods[music_intent](self.artist)
                elif music_intent == 'play_specific_song':
                    response = self.intent_methods[music_intent](self.song)
                else:
                    response = self.intent_methods[music_intent]()
                return [True, response]
        else:
            return [False, None]

    def start(self, user_input):
        chat_session = self.model.start_chat(history=self.history)
        response = chat_session.send_message(user_input)
        model_response = response.text
        self.history.append({"role": "user", "parts": [user_input]})
        self.history.append({"role": "model", "parts": [model_response]})
        music_intent = self.get_music_intent(model_response)

        if music_intent[0]:
            print(music_intent[1])
        else:
            self.text_to_speech(model_response)

    def listen_and_run(self):
        with sr.Microphone() as source:
            print("Listening for activation...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            recognized_text = self.recognizer.recognize_google(audio)

            if recognized_text.lower() == "activate iris" or "hi iris":
                time.sleep(1)
                wave_obj = sa.WaveObject.from_wave_file("path to audio file played after activation")
                play_obj = wave_obj.play()
                play_obj.wait_done()
                time.sleep(1)

                self.record_audio_and_respond()
            else:
                print("Command not recognized or not 'activate iris'.")

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    def record_audio_and_respond(self):
        user_input = self.record.record()  # Replace with your method to get user input
        self.start(user_input)

    def run(self):
        while True:
            self.listen_and_run()

if __name__ == "__main__":
    chat = IrisChat()
    threading.Thread(target=chat.run).start()
