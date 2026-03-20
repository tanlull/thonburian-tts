"""
ThonburianTTS Streaming API
POST /tts  →  streams audio as WAV bytes
"""
import io
import logging
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from cached_path import cached_path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from flowtts.inference import FlowTTSPipeline, ModelConfig, AudioConfig
from transformers import pipeline as hf_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

DEVICE           = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_CHECKPOINT = "hf://ThuraAung1601/E2-F5-TTS/F5_Thai/mega_f5_last.safetensors"
VOCAB_FILE       = "hf://ThuraAung1601/E2-F5-TTS/F5_Thai/mega_vocab.txt"
REF_AUDIO_URL    = "hf://ThuraAung1601/E2-F5-TTS/ref_samples/ref_sample.wav"
ASR_MODEL        = "biodatlab/whisper-th-medium-combined"
SAMPLE_RATE      = 24000
CHUNK_SIZE       = 4096   # bytes per stream chunk

# ─── Singletons ───────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_asr_pipeline():
    logger.info("Loading ASR on %s", DEVICE)
    return hf_pipeline(
        task="automatic-speech-recognition",
        model=ASR_MODEL,
        chunk_length_s=30,
        device=0 if DEVICE == "cuda" else "cpu",
    )

@lru_cache(maxsize=1)
def get_tts_pipeline():
    logger.info("Loading TTS on %s", DEVICE)
    model_config = ModelConfig(
        language="th", model_type="F5",
        checkpoint=MODEL_CHECKPOINT, vocab_file=VOCAB_FILE,
        ode_method="euler", use_ema=True, vocoder="vocos", device=DEVICE,
    )
    audio_config = AudioConfig(
        silence_threshold=-45, max_audio_length=20000,
        cfg_strength=2.5, nfe_step=32, target_rms=0.1,
        cross_fade_duration=0.15, speed=1.0,
        min_silence_len=500, keep_silence=200, seek_step=10,
    )
    return FlowTTSPipeline(
        model_config=model_config,
        audio_config=audio_config,
        temp_dir="temp_f5",
    )

@lru_cache(maxsize=1)
def get_ref_audio():
    logger.info("Downloading reference audio...")
    ref_path = str(cached_path(REF_AUDIO_URL))
    asr = get_asr_pipeline()
    ref_text = asr(
        ref_path,
        generate_kwargs={"language": "<|th|>", "task": "transcribe"},
        batch_size=16,
    )["text"]
    logger.info("Ref text: %s", ref_text)
    return ref_path, ref_text

# ─── Audio helpers ────────────────────────────────────────────────────────────

def numpy_to_wav_bytes(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Convert numpy float32 array → WAV bytes in memory."""
    pcm = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()

def stream_wav_chunks(wav_bytes: bytes, chunk_size: int = CHUNK_SIZE):
    """Yield WAV bytes in fixed-size chunks."""
    for i in range(0, len(wav_bytes), chunk_size):
        yield wav_bytes[i : i + chunk_size]

# ─── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="ThonburianTTS API",
    description="Thai TTS streaming API — POST /tts returns audio/wav stream",
    version="1.0.0",
)

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, example="สวัสดีครับ วันนี้อากาศดีมาก")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)

@app.on_event("startup")
async def warmup():
    """Pre-load all models at startup so first request is fast."""
    logger.info("Warming up models...")
    get_tts_pipeline()
    get_asr_pipeline()
    get_ref_audio()
    logger.info("Warmup complete — ready to serve")

@app.post("/tts", response_class=StreamingResponse)
async def text_to_speech(req: TTSRequest):
    """
    Generate Thai speech and stream back as WAV.

    Returns chunked audio/wav stream.
    """
    try:
        tts = get_tts_pipeline()
        ref_path, ref_text = get_ref_audio()

        # Run inference (synchronous — heavy GPU work)
        logger.info("Generating: %s", req.text)
        output_path = tts(
            text=req.text,
            ref_voice=ref_path,
            ref_text=ref_text,
            output_file="temp_f5/stream_out.wav",
            speed=req.speed,
            check_duration=True,
        )

        # Read generated WAV and stream back
        wav_bytes = Path(output_path).read_bytes()

        return StreamingResponse(
            content=stream_wav_chunks(wav_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="output.wav"',
                "X-Sample-Rate": str(SAMPLE_RATE),
            },
        )

    except Exception as e:
        logger.error("TTS failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "device": DEVICE}