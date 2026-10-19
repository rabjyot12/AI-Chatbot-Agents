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

import shutil
import subprocess
import tempfile
from pathlib import Path

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
    """Generate WAV audio using eSpeak on Linux or pyttsx3 on Windows."""

    text = text.strip()
    if not text:
        raise ValueError("Cannot generate speech from empty text.")

    # Streamlit Cloud: use eSpeak directly, avoiding pyttsx3 voice selection.
    espeak_path = shutil.which("espeak")

    if espeak_path:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "speech.wav"

            result = subprocess.run(
                [
                    espeak_path,
                    "-v", "en-us",
                    "-s", "155",
                    "-w", str(output_path),
                    text,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0 or not output_path.exists():
                raise RuntimeError(
                    f"eSpeak failed: {result.stderr or 'No audio file generated'}"
                )

            audio_bytes = output_path.read_bytes()

            if not audio_bytes:
                raise RuntimeError("eSpeak generated an empty audio file.")

            return audio_bytes

    # Local Windows fallback: preserve the existing pyttsx3 approach.
    import pyttsx3

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "speech.wav"
        engine = pyttsx3.init()
        try:
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
        finally:
            engine.stop()

        if not output_path.exists():
            raise RuntimeError("pyttsx3 did not generate an audio file.")

        return output_path.read_bytes()

