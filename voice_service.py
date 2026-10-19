"""Free local speech-to-text and text-to-speech helpers for the prototype.

STT: faster-whisper (runs locally on CPU).
TTS: pyttsx3 (uses an installed operating-system voice).
No paid speech API is used by this module.
"""
import json
import os
import tempfile
from functools import lru_cache
import urllib.error
import urllib.request
import streamlit as st

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
    """Generate natural speech using the ElevenLabs API."""

    text = text.strip()
    if not text:
        raise ValueError("Cannot generate speech from empty text.")

    # Read the API key securely from Streamlit Secrets or environment.
    api_key = os.getenv("ELEVENLABS_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets.get("ELEVENLABS_API_KEY")
        except Exception:
            api_key = None

    if not api_key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY is missing. Add it to Streamlit Cloud Secrets."
        )

    try:
        voice_id = st.secrets.get(
            "ELEVENLABS_VOICE_ID",
            os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb"),
        )
    except Exception:
        voice_id = os.getenv(
            "ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb"
        )

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/"
        f"{voice_id}?output_format=mp3_44100_128"
    )

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.2,
            "use_speaker_boost": True,
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            audio_bytes = response.read()

        if not audio_bytes:
            raise RuntimeError("ElevenLabs returned empty audio.")

        return audio_bytes

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"ElevenLabs API error ({exc.code}): {error_body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not connect to ElevenLabs: {exc.reason}"
        ) from exc


