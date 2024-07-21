import whisper
import pyaudio
import math
import struct
import wave
import time
import datetime
import os
import threading

TRIGGER_RMS = 10  # start recording above 10
RATE = 16000  # sample rate
TIMEOUT_SECS = 1  # silence time after which recording stops
FRAME_SECS = 0.25  # length of frame (chunks) to be processed at once in secs
CUSHION_SECS = 1  # amount of recording before and after sound

SHORT_NORMALIZE = (1.0 / 32768.0)
FORMAT = pyaudio.paInt16
CHANNELS = 1
SHORT_WIDTH = 2
CHUNK = int(RATE * FRAME_SECS)
CUSHION_FRAMES = int(CUSHION_SECS / FRAME_SECS)
TIMEOUT_FRAMES = int(TIMEOUT_SECS / FRAME_SECS)

OUTPUT_DIR = './audio/recordings'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


class Recorder:
    @staticmethod
    def rms(frame):
        count = len(frame) / SHORT_WIDTH
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
        self.time = time.time()
        self.quiet = []
        self.quiet_idx = -1
        self.timeout = 0
        self.file_index = 1
        self.transcribe_text = None
        self.transcription_done = threading.Event()

    def record(self):
        self.transcription_done.clear()  # Clear the event at the start of each recording
        print('Ready to listen...')
        while True:
            sound = []
            start = time.time()
            begin_time = None
            while True:
                data = self.stream.read(CHUNK)
                rms_val = self.rms(data)
                if self.inSound(data):
                    sound.append(data)
                    if begin_time is None:
                        begin_time = datetime.datetime.now()
                else:
                    if len(sound) > 0:
                        # Start a new thread to save and process the recording
                        threading.Thread(target=self.save_and_process, args=(sound.copy(), begin_time)).start()
                        sound.clear()
                        begin_time = None
                    else:
                        self.queueQuiet(data)

                curr = time.time()
                secs = int(curr - start)
                tout = 0 if self.timeout == 0 else int(self.timeout - curr)
                label = 'Listening' if self.timeout == 0 else 'Recording'
                print('[+] %s: Level=[%4.2f] Secs=[%d] Timeout=[%d]' % (label, rms_val, secs, tout), end='\r')

                # Check if transcription is done
                if self.transcription_done.is_set():
                    return self.transcribe_text

    def queueQuiet(self, data):
        self.quiet_idx += 1
        if self.quiet_idx == CUSHION_FRAMES:
            self.quiet_idx = 0

        if len(self.quiet) < CUSHION_FRAMES:
            self.quiet.append(data)
        else:
            self.quiet[self.quiet_idx] = data

    def dequeueQuiet(self, sound):
        if len(self.quiet) == 0:
            return sound

        ret = []

        if len(self.quiet) < CUSHION_FRAMES:
            ret.extend(self.quiet)
            ret.extend(sound)
        else:
            ret.extend(self.quiet[self.quiet_idx + 1:])
            ret.extend(self.quiet[:self.quiet_idx + 1])
            ret.extend(sound)

        return ret

    def inSound(self, data):
        rms = self.rms(data)
        curr = time.time()

        if rms > TRIGGER_RMS:
            self.timeout = curr + TIMEOUT_SECS
            return True

        if curr < self.timeout:
            return True

        self.timeout = 0
        return False

    def save_and_process(self, sound, begin_time):
        sound = self.dequeueQuiet(sound)

        keep_frames = len(sound) - TIMEOUT_FRAMES + CUSHION_FRAMES
        if keep_frames < 0:
            keep_frames = len(sound)
        recording = b''.join(sound[0:keep_frames])

        filename = os.path.join(OUTPUT_DIR, f"recording_{self.file_index}.wav")
        self.file_index += 1

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(recording)

        model = whisper.load_model("base")
        result = model.transcribe(filename)
        self.transcribe_text = result['text']
        self.transcription_done.set()

        try:
            os.remove(filename)
        except OSError as e:
            print(f"Error deleting {filename}: {e}")
