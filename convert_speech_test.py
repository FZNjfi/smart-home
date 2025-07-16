import sounddevice as sd
import numpy as np
import webrtcvad
import scipy.io.wavfile as wav
import queue

class Speech:
    def __init__(self, sample_rate=16000, frame_duration=30, sensitivity_level=2, max_silent_chunks=20):
        self.sample_rate=sample_rate
        self.frame_duration=frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(sensitivity_level)
        self.max_silent_chunks=max_silent_chunks
        self.audio_queue = queue.Queue()

    def audio_record(self):
        recorded_frames = []
        silent_chunks = 0
        print("start recording...")
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='int16',
                            blocksize=self.frame_size,
                            callback=self.audio_callback):
            while True:
                audio_chunk = self.audio_queue.get()
                raw = audio_chunk.tobytes()
                is_speech = self.vad.is_speech(raw, self.sample_rate)
                recorded_frames.append(audio_chunk)

                if not is_speech:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks >= self.max_silent_chunks:
                    break
        print("finish recording...")
        all_audio = np.concatenate(recorded_frames, axis=0)
        wav.write("speech/output.wav", self.sample_rate, all_audio)

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy())


speech=Speech()
speech.audio_record()
