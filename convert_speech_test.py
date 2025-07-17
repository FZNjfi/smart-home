import sounddevice as sd
import numpy as np
import webrtcvad
import scipy.io.wavfile as wav
import queue
import whisper
import torch
import noisereduce as nr
from agent import SmartAgent
from together import Together
from together.types import ChatCompletionResponse, ChatCompletionChunk
from together.types.chat_completions import ChatCompletionMessage


class Speech:
    def __init__(self, sample_rate=32000, frame_duration=30, sensitivity_level=2, max_silent_chunks=30):
        self.sample_rate=sample_rate
        self.frame_duration=frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(sensitivity_level)
        self.max_silent_chunks=max_silent_chunks
        self.audio_queue = queue.Queue()

        self.speech_to_text_model = whisper.load_model("large")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.speech_to_text_model = self.speech_to_text_model.to(device)

        self.client = Together(api_key="1aff76ce049d22e115f4b8c7eedabcc6bc5e7d082cbbaeb1bbca72f907971234")

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
        wav.write("speech/output.wav", self.sample_rate, audio.astype(np.int16))

    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy())

    def convert_speech_to_text(self):
        result = self.speech_to_text_model.transcribe("speech/output.wav", language="fa")
        lang=result['language']
        if lang == 'fa':
            text=self.correction_text(result['text'])
        else:
            text=result['text']
        return text

    def correction_text(self, text):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Persian spelling corrector. "
                    "You receive a Persian text with many errors and should return only the corrected text."
                )
            },
            {"role": "user", "content": text}
        ]
        response = self.client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages= messages
        )
        return response.choices[0].message.content


speech=Speech()
speech.audio_record()
message=speech.convert_speech_to_text()
print(message)
smart_agent=SmartAgent()
print(smart_agent.agent_loop(message))
