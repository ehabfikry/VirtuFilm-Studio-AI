"""
Cindy AI Director — Local Neural Voice Engine (Kokoro-82M & Piper TTS)
=============================================================================
Provides 100% free, offline, commercial-safe text-to-speech for:
1. Cindy's interactive director voice (English: Kokoro, Arabic: Piper / Edge)
2. Character Dubbing & Dialogue Studio (Male, Female, Narrator, Accents)
=============================================================================
"""

import os
import sys
import io
import re
import wave
import numpy as np
import soundfile as sf

KOKORO_DIR = r"D:\CindyAI\models\tts\kokoro"
PIPER_DIR = r"D:\CindyAI\models\tts\piper"

KOKORO_MODEL_PATH = os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx")
KOKORO_VOICES_PATH = os.path.join(KOKORO_DIR, "voices-v1.0.bin")
if not os.path.exists(KOKORO_VOICES_PATH):
    KOKORO_VOICES_PATH = os.path.join(KOKORO_DIR, "voices.json")

PIPER_AR_MODEL_PATH = os.path.join(PIPER_DIR, "ar_JO-kareem-medium.onnx")
PIPER_AR_CONFIG_PATH = os.path.join(PIPER_DIR, "ar_JO-kareem-medium.onnx.json")

PIPER_EN_MODEL_PATH = os.path.join(PIPER_DIR, "en_US-lessac-medium.onnx")
PIPER_EN_CONFIG_PATH = os.path.join(PIPER_DIR, "en_US-lessac-medium.onnx.json")

_kokoro_instance = None
_piper_ar_instance = None
_piper_en_instance = None

VOICE_CATALOG = [
    {
        "id": "af_sarah",
        "name": "Cindy Director (Sarah)",
        "engine": "kokoro",
        "lang": "en",
        "gender": "Female",
        "style": "Expressive, Natural Studio Assistant"
    },
    {
        "id": "af_bella",
        "name": "Cinema Narrative (Bella)",
        "engine": "kokoro",
        "lang": "en",
        "gender": "Female",
        "style": "Warm, Emotional Dramatic Storyteller"
    },
    {
        "id": "am_adam",
        "name": "Blockbuster Trailer (Adam)",
        "engine": "kokoro",
        "lang": "en",
        "gender": "Male",
        "style": "Deep, Cinematic, Action Trailer Voice"
    },
    {
        "id": "am_michael",
        "name": "Classic Hollywood Narrator (Michael)",
        "engine": "kokoro",
        "lang": "en",
        "gender": "Male",
        "style": "Authoritative, Film Noir Detective"
    },
    {
        "id": "bf_emma",
        "name": "British Dramatic (Emma)",
        "engine": "kokoro",
        "lang": "en",
        "gender": "Female",
        "style": "Sophisticated British Period Cinema"
    },
    {
        "id": "bm_george",
        "name": "British Authority (George)",
        "engine": "kokoro",
        "lang": "en",
        "gender": "Male",
        "style": "Crisp British Character Acting"
    },
    {
        "id": "piper_ar_kareem",
        "name": "الأداء العربي العصبي (كريم)",
        "engine": "piper",
        "lang": "ar",
        "gender": "Male",
        "style": "أداء صوتي عربي واضح وفوري"
    }
]

def get_kokoro():
    global _kokoro_instance
    if _kokoro_instance is None:
        if os.path.exists(KOKORO_MODEL_PATH) and os.path.exists(KOKORO_VOICES_PATH):
            from kokoro_onnx import Kokoro
            print("[TTS Engine] Loading Kokoro-82M ONNX model...")
            _kokoro_instance = Kokoro(KOKORO_MODEL_PATH, KOKORO_VOICES_PATH)
            print("[TTS Engine] Kokoro-82M loaded successfully!")
        else:
            print(f"[TTS Engine] Kokoro files not ready: {KOKORO_MODEL_PATH}")
    return _kokoro_instance

def get_piper_arabic():
    global _piper_ar_instance
    if _piper_ar_instance is None:
        if os.path.exists(PIPER_AR_MODEL_PATH):
            from piper import PiperVoice
            print("[TTS Engine] Loading Piper Arabic voice (Kareem)...")
            _piper_ar_instance = PiperVoice.load(PIPER_AR_MODEL_PATH, PIPER_AR_CONFIG_PATH)
            print("[TTS Engine] Piper Arabic loaded successfully!")
        else:
            print(f"[TTS Engine] Piper Arabic files not ready: {PIPER_AR_MODEL_PATH}")
    return _piper_ar_instance

def is_arabic_text(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))

def _split_into_sentences(text: str, max_chars: int = 150):
    sentences = re.split(r'([.!?;\n]+)', text)
    chunks = []
    curr = ""
    for part in sentences:
        if not part:
            continue
        if len(curr) + len(part) < max_chars:
            curr += part
        else:
            if curr.strip():
                chunks.append(curr.strip())
            curr = part
    if curr.strip():
        chunks.append(curr.strip())
    return chunks if chunks else [text]

def synthesize(text: str, voice_id: str = "auto", speed: float = 1.0) -> bytes:
    """
    Synthesize text into WAV audio bytes using local Kokoro or Piper.
    Falls back gracefully to Edge TTS if needed.
    """
    clean = re.sub(r'[*#_`]', '', text).strip()
    if not clean:
        return b""

    is_ar = is_arabic_text(clean)

    # 1. Arabic Synthesis via Piper Neural
    if is_ar or voice_id in ["piper_ar_kareem", "kareem", "piper_ar"]:
        piper_ar = get_piper_arabic()
        if piper_ar:
            try:
                buf = io.BytesIO()
                with wave.open(buf, "wb") as wav_file:
                    first = True
                    for chunk in piper_ar.synthesize(clean):
                        if first:
                            wav_file.setnchannels(chunk.sample_channels)
                            wav_file.setsampwidth(chunk.sample_width)
                            wav_file.setframerate(chunk.sample_rate)
                            first = False
                        wav_file.writeframes(chunk.audio_int16_bytes)
                wav_bytes = buf.getvalue()
                if len(wav_bytes) > 500:
                    return wav_bytes
            except Exception as e:
                print(f"[TTS Piper Error] {e}")

    # 2. English / International Synthesis via Kokoro-82M
    selected_voice = voice_id if voice_id not in ["auto", "piper_ar_kareem"] else "af_sarah"
    kokoro = get_kokoro()
    if kokoro:
        try:
            chunks = _split_into_sentences(clean, max_chars=140)
            all_samples = []
            sample_rate = 24000
            for c in chunks:
                if not c.strip():
                    continue
                samples, sr = kokoro.create(c.strip(), voice=selected_voice, speed=speed, lang="en-us")
                all_samples.append(samples)
                sample_rate = sr
                # Short silence gap between sentences (0.15s)
                silence = np.zeros(int(sample_rate * 0.15), dtype=np.float32)
                all_samples.append(silence)

            if all_samples:
                final_samples = np.concatenate(all_samples)
                buf = io.BytesIO()
                sf.write(buf, final_samples, sample_rate, format='WAV')
                return buf.getvalue()
        except Exception as e:
            print(f"[TTS Kokoro Error] {e}")

    # 3. Fallback: Edge TTS if local ONNX is still loading
    try:
        import edge_tts
        import asyncio
        edge_voice = 'ar-EG-SalmaNeural' if is_ar else 'en-US-JennyNeural'
        async def _run():
            comm = edge_tts.Communicate(clean[:350], edge_voice)
            out_b = io.BytesIO()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    out_b.write(chunk["data"])
            return out_b.getvalue()
        return asyncio.run(_run())
    except Exception as e:
        print(f"[TTS Fallback Error] {e}")
        return b""

def list_voices():
    return VOICE_CATALOG
