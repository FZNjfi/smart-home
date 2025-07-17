import sounddevice as sd
import numpy as np
import webrtcvad
import scipy.io.wavfile as wav
import queue
import whisper
import torch
import asyncio
import edge_tts
import noisereduce as nr
from agent import SmartAgent


class Speech:
    def __init__(self, sample_rate=32000, frame_duration=30, sensitivity_level=2, max_silent_chunks=30):
        self.sample_rate=sample_rate
        self.frame_duration=frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(sensitivity_level)
        self.max_silent_chunks=max_silent_chunks
        self.audio_queue = queue.Queue()
        self.speech_to_text_model = whisper.load_model("large")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.speech_to_text_model = self.speech_to_text_model.to(device)
        self.voiceFA = "fa-IR-FaridNeural"
        self.voiceEN = "en-US-AriaNeural"

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
        audio = np.concatenate(recorded_frames, axis=0).flatten()
        audio= nr.reduce_noise(y=audio.astype(np.float32), sr=self.sample_rate)
        wav.write("speech/input.wav", self.sample_rate, audio.astype(np.int16))

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy())

    def convert_speech_to_text(self):
        result = self.speech_to_text_model.transcribe("speech/input.wav")
        return result['text']

    async def convert_text_to_speech(self, text):
        try:
            voice = self.voiceEN
            if self.is_persian(text):
                voice = self.voiceFA
            communicator = edge_tts.Communicate(text, voice)
            await communicator.save("speech/output.wav")
            print("Audio saved.")
        except Exception as e:
            print(f"Error: {e}")

    def is_persian(self, text):
        return any('\u0600' <= c <= '\u06FF' for c in text)



speech=Speech()
speech.audio_record()
message=speech.convert_speech_to_text()
print(message)
smart_agent=SmartAgent()
response=smart_agent.agent_loop(message)
print(response)
asyncio.run(speech.convert_text_to_speech(response))

