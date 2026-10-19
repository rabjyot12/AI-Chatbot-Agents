"""Free local speech-to-text and text-to-speech helpers for the prototype.

STT: faster-whisper (runs locally on CPU).
TTS: pyttsx3 (uses an installed operating-system voice).
No paid speech API is used by this module.
"""

import os
import tempfile
from functools import lru_cache

import pyttsx3
from faster_whisper import WhisperModel

import ctypes.util
import shutil

def check_speech_engine():
    return {
        "espeak_executable": shutil.which("espeak"),
        "espeak_library": ctypes.util.find_library("espeak"),
    }


@lru_cache(maxsize=1)
def _get_whisper_model():
    # Small enough for CPU inference on a normal laptop; first run downloads model files.
    model_name = os.getenv("WHISPER_MODEL", "base")
    return WhisperModel(model_name, device="cpu", compute_type="int8")


def transcribe_audio(audio_bytes: bytes, audio_format: str = "wav") -> str:
    """Transcribe microphone audio bytes to text using local Whisper inference."""
    if not audio_bytes:
        return ""

    suffix = ".wav" if audio_format.lower() == "wav" else ".webm"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        segments, _info = _get_whisper_model().transcribe(
            temp_path,
            beam_size=3,
            vad_filter=True,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return text
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def synthesize_speech(text: str) -> bytes:
    """Generate WAV speech using a local installed system voice and return its bytes."""
    text = (text or "").strip()
    if not text:
        return b""

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name

        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        engine.stop()

        with open(temp_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        if not audio_bytes:
            raise RuntimeError("The local TTS engine produced an empty audio file.")
        return audio_bytes
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
