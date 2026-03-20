# ThonburianTTS — Quick Start

Thai Text-to-Speech API · powered by F5-TTS & Thonburian Whisper

---

## 1. Setup (ครั้งแรกครั้งเดียว)

```bash
conda activate thonburian
cd /home/tan/thonburian-tts
pip install -e .
```

---

## 2. Start the Server

```bash
cd /home/tan/thonburian-tts
uvicorn tts_api:app --host 0.0.0.0 --port 8000
```

> **หมายเหตุ:** ครั้งแรกจะดาวน์โหลด model อัตโนมัติ (~2–5 GB) ใช้เวลาสักครู่  
> รอจนเห็น `Warmup complete — ready to serve` แล้วค่อยเรียกใช้

---

## 3. Generate Speech

### วิธีที่ 1 — Python client (stream + เล่นเสียงเลย)

```bash
python tts_client.py "สวัสดีครับ วันนี้อากาศดีมาก"
```

### วิธีที่ 2 — curl (บันทึกเป็นไฟล์)

```bash
python tts_curl.py "ยินดีต้อนรับสู่ระบบสังเคราะห์เสียงภาษาไทย"
```

ไฟล์เสียงจะถูกบันทึกที่ `outputs_f5/output.wav`

### วิธีที่ 3 — Test อัตโนมัติ

```bash
python tts_Test.py
```

---

## 4. ปรับแต่งเสียง

เพิ่ม `--speed` เพื่อเปลี่ยนความเร็ว:

| ค่า speed | ผล                       |
| --------- | ------------------------ |
| `0.8`     | ช้าลง เหมาะกับ narration |
| `1.0`     | ปกติ (default)           |
| `1.2`     | เร็วขึ้นเล็กน้อย         |

```bash
python tts_client.py "ข้อความที่ต้องการ" --speed 0.8
```

---

## 5. เช็คสถานะ Server

```bash
curl http://localhost:8000/health
```

ผลลัพธ์ที่ถูกต้อง:

```json
{ "status": "ok", "device": "cuda" }
```

---

## Troubleshooting

| ปัญหา                       | วิธีแก้                                            |
| --------------------------- | -------------------------------------------------- |
| `Connection refused`        | รัน server ก่อน (ข้อ 2)                            |
| `Attribute "app" not found` | ต้อง `cd /home/tan/thonburian-tts` ก่อนรัน uvicorn |
| เสียงไม่ออก                 | เช็ค `outputs_f5/output.wav` ว่ามีไฟล์ไหม          |
| Server ช้ามากครั้งแรก       | กำลังดาวน์โหลด model — รอได้เลย                    |
| ตัวเลขอ่านผิด               | เขียนเป็นคำ เช่น `สาม` แทน `3`                     |
