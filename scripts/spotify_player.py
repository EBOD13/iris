import os
import random
import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import time

load_dotenv()


class SpotifyPlayer:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI = 'http://localhost:5000/callback'
        self.SCOPE = 'user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-read'
        self.current_track = None
        self.playback_thread = None
        self.playback_thread_stop = threading.Event()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id,
                                                            client_secret=self.client_secret,
                                                            redirect_uri=self.REDIRECT_URI,
                                                            scope=self.SCOPE))

    def get_active_device(self):
        devices = self.sp.devices()
        available_devices = devices.get('devices', [])

        if not available_devices:
            print("No devices found. Make sure your Spotify app is running and logged in.")
            return None

        active_device = next((device for device in available_devices if device['is_active']), None)

        if not active_device:
            print("No active devices found. Make sure at least one device is actively playing music.")
            return None

        return active_device['id']

    def activate_device(self):
        devices = self.sp.devices()
        available_devices = devices.get('devices', [])

        # Find inactive devices
        inactive_devices = [device for device in available_devices if not device['is_active']]
        if not inactive_devices:
            print("No inactive devices found.")
            return None

        # Get the first inactive device id
        inactive_device_id = inactive_devices[0]['id']

        try:
            # Transfer playback to the inactive device
            self.sp.transfer_playback(device_id=inactive_device_id)
            return inactive_device_id
        except spotipy.SpotifyException as e:
            print(f"Error activating device: {e}")
            return None

    def queue_random_tracks(self, count=15):
        try:
            characters = 'abcdefghijklmnopqrstuvwxyz'
            for _ in range(count):
                random_character = random.choice(characters)
                if random.randint(0, 1) == 0:
                    random_search = random_character + '%'
                else:
                    random_search = '%' + random_character + '%'

                result = self.sp.search(q=random_search, limit=1, type='track')
                if result['tracks']['items']:
                    random_track = result['tracks']['items'][0]
                    track_uri = random_track['uri']
                    self.sp.add_to_queue(track_uri)
                    # print(f"Queued random track: {random_track['name']} by {random_track['artists'][0]['name']}.")
                else:
                    print("No track found for the random search string.")
        except Exception as e:
            print(f"Error occurred while queuing tracks: {e}")

    def play(self, track_uri):
        active_device_id = self.get_active_device()
        if not active_device_id:
            active_device_id = self.activate_device()

        if active_device_id:
            self.sp.start_playback(device_id=active_device_id, uris=[track_uri])
            self.queue_random_tracks()  # Queue initial set of random tracks
            self.playback_thread_stop.clear()
            if not self.playback_thread or not self.playback_thread.is_alive():
                self.playback_thread = threading.Thread(target=self.monitor_current_track)
                self.playback_thread.start()

    def play_given_song(self, song_name):
        result = self.sp.search(q=song_name, limit=1, type='track')
        if result['tracks']['items']:
            track = result['tracks']['items'][0]
            track_uri = track['uri']
            artist_name = track['artists'][0]['name']
            self.current_track = track
            self.play(track_uri)
            return f"Sure! Now playing '{song_name}' by {artist_name}"
        else:
            print(f"Song '{song_name}' not found.")

    def play_random_saved_track(self):
        try:
            list_tracks = self.sp.current_user_saved_tracks(limit=50)
            tracks = list_tracks['items']
            track_uris = [track['track']['uri'] for track in tracks]
            if not track_uris:
                print("No tracks found in your library.")
                return

            random_track_uri = random.choice(track_uris)
            self.current_track = self.sp.track(random_track_uri)
            artist_name = self.current_track['artists'][0]['name']
            self.play(random_track_uri)
            return f"Now, playing {self.current_track['name']} by {artist_name}"

        except Exception as e:
            print(f"Error occurred: {e}")

    def play_next_track(self):
        try:
            self.sp.next_track()
            return "Of course! The next track is now playing"
        except spotipy.SpotifyException as e:
            print(f"Spotify error occurred: {e}")

    def play_previous_track(self):
        try:
            self.sp.previous_track()
            return "Sure, I resumed playing the previous track"
        except spotipy.SpotifyException as e:
            print(f"Error playing previous track: {e}")

    def pause_track(self):
        try:
            self.sp.pause_playback()
            return "Track paused"
        except spotipy.SpotifyException as e:
            print(f"Spotify error: {e}")

    def resume_track(self):
        try:
            active_device_id = self.get_active_device()
            if not active_device_id:
                active_device_id = self.activate_device()

            if active_device_id:
                self.sp.start_playback(device_id=active_device_id)
                return "Certainly, the music has resumed playing"
            else:
                return ("Apologies Mr. Daniel, but I'm unable to complete that task as there is no active device "
                        "detected.")

        except spotipy.SpotifyException:
            return "No active device"

    def get_playlist_ids(self):
        try:
            list_of_playlist = []
            playlists = self.sp.current_user_playlists(limit=50)
            for playlist in playlists['items']:
                list_of_playlist.append(playlist['id'])
            return list_of_playlist
        except Exception as e:
            print(f"Error occurred: {e}")
            return []

    def get_playlist_tracks(self, playlist_id):
        tracks = []
        offset = 0

        while True:
            result = self.sp.playlist_items(playlist_id, limit=100, offset=offset)
            if not result['items']:
                break
            tracks.extend(result['items'])
            offset += 100
        return tracks

    def monitor_current_track(self):
        while not self.playback_thread_stop.is_set():
            playback = self.sp.current_playback()
            if playback and playback['is_playing']:
                current_track_id = playback['item']['id']
                if self.current_track and self.current_track['id'] != current_track_id:
                    self.queue_random_tracks()  # Queue more tracks when the current track finishes
                    time.sleep(1)
            time.sleep(5)  # Check every 5 seconds

    def play_random_playlist(self):
        playlist_ids = self.get_playlist_ids()
        if not playlist_ids:
            print("No playlists found.")
            return

        playlist_id = random.choice(playlist_ids)
        try:
            tracks = self.get_playlist_tracks(playlist_id)

            if not tracks:
                print("No tracks found in the playlist")
                return

            track_uris = [track['track']['uri'] for track in tracks]

            if not track_uris:
                print("No track URIs found.")
                return

            random_track = random.choice(track_uris)
            self.current_track = self.sp.track(random_track)
            self.play(random_track)
            print(f"Playing random track: {self.current_track['name']} by {self.current_track['artists'][0]['name']}")

        except spotipy.SpotifyException as e:
            print(f"Spotify API error occurred: {e}")

    def play_song_by_artist(self, artist_name):
        search_results = self.sp.search(q=f'artist:{artist_name}', type='track', limit=50)

        if search_results:
            track = random.choice(search_results['tracks']['items'])
            track_uri = track['uri']
            self.play(track_uri)
        else:
            print("Could not find artist or track")

