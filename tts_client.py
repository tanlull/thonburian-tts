# Python client — เล่นเสียงแบบ stream
import requests
import pyaudio

import sys

def stream_tts(text: str, speed: float = 1.0):
    response = requests.post(
        "http://localhost:8000/tts",
        json={"text": text, "speed": speed},
        stream=True,   # <-- สำคัญ
    )
    response.raise_for_status()

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    for chunk in response.iter_content(chunk_size=4096):
        if chunk:
            stream.write(chunk)

    stream.stop_stream()
    stream.close()
    pa.terminate()

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "สวัสดีครับ วันนี้อากาศดีมากเลยนะครับ"
    stream_tts(text)


