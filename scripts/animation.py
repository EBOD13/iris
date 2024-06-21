import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Viewer")
        self.setGeometry(100, 100, 1000, 600)  # Increased width for demonstration

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.browser = QWebEngineView()
        self.browser.setMaximumWidth(300)
        self.browser.setMaximumHeight(300)# Set a minimum width for the browser
        layout.addWidget(self.browser)

        self.button = QPushButton("Click me")
        layout.addWidget(self.button)

        self.load_youtube_video()

    def load_youtube_video(self):
        url = QUrl("https://www.youtube.com/watch?v=CkkjXTER2KE&t=531s")
        self.browser.setUrl(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# import numpy as np
# import matplotlib.pyplot as plt
# import librosa
# from scipy.signal import find_peaks, find_peaks
#
# # Load your own audio file
# audio_path = 'C:/Users/oleka/OneDrive/Desktop/iris/data/audio/Billie.wav'
# y, sr = librosa.load(audio_path)
#
# # Calculate time axis
# time = np.arange(len(y)) / sr
#
# # Plot the waveform
# plt.figure(figsize=(14, 5))
# plt.plot(time, y)
# plt.title('Waveform')
# plt.xlabel('Time (s)')
# plt.ylabel('Amplitude')
#
# # Find peaks and troughs
# peaks, _ = find_peaks(y, prominence=0.1)  # Adjust prominence as needed
# troughs, _ = find_peaks(-y, prominence=0.1)  # Find troughs by negating and finding peaks
#
# # Plot peaks and troughs
# plt.scatter(time[peaks], y[peaks], color='red', label='Peaks')
# plt.scatter(time[troughs], y[troughs], color='blue', label='Troughs')
# plt.legend()
#
# int_value = y[peaks].astype(int)
# # plt.show()
# print(type(int_value))
# # print(list(zip(time[peaks], y[peaks], y[troughs])))
#
#


# import wave
# import numpy as np
# import scipy.signal
#
# def read_wave_file(filename):
#     with wave.open(filename, 'r') as wav_file:
#         # Extract Raw Audio from Wav File
#         signal = wav_file.readframes(-1)
#         signal = np.frombuffer(signal, dtype=np.int16)
#
#         # Get the frame rate
#         frame_rate = wav_file.getframerate()
#
#         # Check if audio has multiple channels
#         if wav_file.getnchannels() > 1:
#             signal = signal[::wav_file.getnchannels()]
#
#     return signal, frame_rate
#
# def find_peaks_and_troughs(signal):
#     # Find peaks
#     peaks, _ = scipy.signal.find_peaks(signal)
#     # Find troughs
#     troughs, _ = scipy.signal.find_peaks(-signal)
#
#     return peaks, troughs
#
# def pair_peaks_and_troughs(peaks, troughs):
#     pairs = []
#     i, j = 0, 0
#     while i < len(peaks) and j < len(troughs):
#         if peaks[i] < troughs[j]:
#             pairs.append((peaks[i], troughs[j]))
#             i += 1
#         else:
#             pairs.append((troughs[j], peaks[i]))
#             j += 1
#     # If there are remaining peaks or troughs, we can pair them separately or discard them
#     # Here we discard them for simplicity
#     return pairs
#
# # Example usage:
# filename = audio_path
# signal, frame_rate = read_wave_file(filename)
# peaks, troughs = find_peaks_and_troughs(signal)
# pairs = pair_peaks_and_troughs(peaks, troughs)
#
#
