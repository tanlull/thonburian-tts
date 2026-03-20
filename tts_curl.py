import sys
import requests
from pathlib import Path

def save_tts_to_file(text: str, output_path: str = "outputs_f5/output.wav", speed: float = 1.0):
    print(f"กำลังสังเคราะห์เสียง: '{text}'...")
    response = requests.post(
        "http://localhost:8000/tts",
        json={"text": text, "speed": speed},
        stream=True,
    )
    response.raise_for_status()

    # สร้างโฟลเดอร์ถ้ายังไม่มี
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
                
    print(f"บันทึกไฟล์เสียงสำเร็จที่: {output_path}")

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "ยินดีต้อนรับสู่ระบบสังเคราะห์เสียงภาษาไทย"
    save_tts_to_file(text)