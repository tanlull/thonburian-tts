# ThonburianTTS — Quick Start Guide

This guide walks you through connecting **VoiceBotUI** to **ThonburianTTS**, a local Thai text-to-speech engine powered by the F5-TTS model. Once set up, the bot will speak Thai using a natural-sounding voice — entirely offline, no API key needed.

---

## Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended) or CPU (slower)
- Node.js 18+ (for VoiceBotUI)
- The `thonburian-tts` repository cloned alongside VoiceBotUI

---

## 1. Install ThonburianTTS Dependencies

```bash
cd thonburian-tts
pip install fastapi uvicorn torch transformers cached-path numpy
pip install flowtts   # or install from the repo if not on PyPI
```

> If you are using a virtual environment (recommended):
> ```bash
> python -m venv .venv
> source .venv/bin/activate   # Linux / macOS
> # .venv\Scripts\activate    # Windows
> pip install -r requirements.txt
> ```

---

## 2. Start the TTS Server

```bash
cd thonburian-tts
uvicorn tts_api:app --host 0.0.0.0 --port 8000
```

On first launch the server will:
1. Download the **F5-TTS Thai** model checkpoint (~1.5 GB)
2. Download the **Whisper Thai** ASR model (used for reference audio transcription)
3. Download the default reference audio sample

Once you see `Warmup complete — ready to serve`, the server is ready.

### Verify the Server

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "device": "cuda"}
```

You can also test TTS directly:

```bash
curl -X POST http://localhost:8000/tts/base64 \
  -H "Content-Type: application/json" \
  -d '{"text": "สวัสดีครับ วันนี้อากาศดีมาก"}' \
  | python -m json.tool | head -5
```

Expected response:
```json
{
    "audioBase64": "UklGR...",
    "contentType": "audio/wav"
}
```

---

## 3. Start VoiceBotUI

In a separate terminal:

```bash
cd VoiceBotUI
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Connect VoiceBotUI to ThonburianTTS

1. Navigate to the **Admin Panel** at [http://localhost:3000/admin](http://localhost:3000/admin)
2. Under **TTS Engine**, select **Custom API**
3. Set the **Custom TTS Endpoint** to:
   ```
   http://localhost:8000/tts/base64
   ```
4. Leave the **API Key** field **blank** (ThonburianTTS does not require authentication)
5. Click **Test Connection** to verify

That's it! Go back to the chat page and send a message — the bot's reply will now be spoken using ThonburianTTS.

---

## API Reference

### `POST /tts/base64`

Generates Thai speech and returns base64-encoded WAV audio. This endpoint is designed to be compatible with VoiceBotUI's Custom API spec.

**Request:**
```json
{
  "text": "ข้อความที่ต้องการแปลงเป็นเสียง",
  "speed": 1.0
}
```

| Field   | Type   | Required | Default | Description                    |
|---------|--------|----------|---------|--------------------------------|
| `text`  | string | Yes      | —       | Thai text to synthesize (1–500 chars) |
| `speed` | float  | No       | `1.0`   | Playback speed (0.5–2.0)      |

**Response:**
```json
{
  "audioBase64": "UklGR...",
  "contentType": "audio/wav"
}
```

| Field         | Type   | Description                          |
|---------------|--------|--------------------------------------|
| `audioBase64` | string | Base64-encoded WAV audio data        |
| `contentType` | string | MIME type of the audio (`audio/wav`) |

### `POST /tts` (Streaming)

The original streaming endpoint — returns raw WAV bytes as a chunked response. Useful for server-to-server integrations or custom audio pipelines.

### `GET /health`

Returns server status and device info.

---

## Architecture Overview

```
┌──────────────────────┐         ┌──────────────────────────┐
│     VoiceBotUI       │         │    ThonburianTTS Server   │
│   (Next.js :3000)    │         │     (FastAPI :8000)       │
│                      │         │                          │
│  User clicks 🔊      │  POST   │  /tts/base64             │
│  ChatMessage.tsx ────────────► │    ↓                     │
│                      │         │  F5-TTS Thai Model       │
│  ◄──────────────────────────── │    ↓                     │
│  plays audio/wav     │  JSON   │  base64 WAV response     │
│  via <Audio> element │         │                          │
└──────────────────────┘         └──────────────────────────┘
```

---

## Troubleshooting

**CORS errors in browser console**
The TTS server includes CORS middleware that allows all origins by default. If you still see CORS errors, make sure you are accessing VoiceBotUI via `http://localhost:3000` (not `127.0.0.1` or a different port).

**First request is slow**
The first TTS request after server startup may take a few extra seconds while models are loaded into GPU memory. Subsequent requests will be much faster.

**Out of memory (OOM)**
The F5-TTS model and Whisper ASR model together require roughly 4–6 GB of VRAM. If you run out of GPU memory, try setting `DEVICE = "cpu"` in `tts_api.py` (inference will be slower).

**Audio doesn't play in VoiceBotUI**
Make sure the TTS engine is set to "Custom API" (not "Google" or "Browser") and that the endpoint URL includes the `/tts/base64` path — not just `http://localhost:8000`.

---

## Production Notes

- Tighten the CORS `allow_origins` in `tts_api.py` to your actual domain instead of `"*"`
- Consider adding authentication (API key) if exposing the TTS server to the internet
- For high-traffic deployments, run multiple workers: `uvicorn tts_api:app --workers 2`
- Monitor GPU utilization with `nvidia-smi` to ensure the model fits in memory
