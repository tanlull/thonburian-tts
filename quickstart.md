pip install git+https://github.com/biodatlab/thonburian-tts.git

# or clone and install

git clone https://github.com/biodatlab/thonburian-tts.git
cd thonburian-tts
pip install -e .

# Start TTS API Server

uvicorn tts_api:app --host 0.0.0.0 --port 8000

# Health check

curl http://localhost:8000/health

# Test TTS

curl -X POST http://localhost:8000/tts/base64 \
  -H "Content-Type: application/json" \
  -d '{"text": "สวัสดีครับ วันนี้อากาศดีมาก"}'

# Gradio Demo

python gradio_app.py
