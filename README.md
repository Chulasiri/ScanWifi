# WiFi & Network Scanner

โปรแกรมสแกน WiFi และตรวจสอบคุณภาพอินเทอร์เน็ต รองรับ Windows และ Linux

## ความต้องการของระบบ

- Python 3.8+
- Windows 10/11 หรือ Linux (Ubuntu, Debian, CentOS, etc.)

## การติดตั้ง

### 1. ติดตั้ง Python

**Windows:**
- ดาวน์โหลด Python จาก https://www.python.org/
- ตอนติดตั้งให้เลือก "Add Python to PATH"

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

## วิธีการรันโปรแกรม

### Windows
ดับเบิลคลิกไฟล์ `run.bat` หรือรันคำสั่ง:
```bash
python app.py
```

### Linux
```bash
chmod +x run.sh
./run.sh
```
หรือรันคำสั่ง:
```bash
python3 app.py
```

## การเปิดใช้งาน

1. เปิด Browser ไปที่ http://localhost:5000
2. กดปุ่ม "Scan WiFi" เพื่อสแกนเครือข่าย WiFi
3. ดูข้อมูล Network และ IP

## หมายเหตุ

- การสแกน WiFi ต้องรันด้วยสิทธิ์ Administrator (Windows) หรือ Root (Linux)
- คำสั่งที่ใช้: `netsh wlan` (Windows) หรือ `nmcli` (Linux)
- ถ้าไม่สามารถสแกนได้ ลองรันด้วยสิทธิ์ Admin

## ไฟล์ในโปรเจกต์

- `app.py` - โปรแกรมหลัก (Flask Web Server)
- `requirements.txt` - Python dependencies
- `run.bat` - Script รันสำหรับ Windows
- `run.sh` - Script รันสำหรับ Linux
- `ScanWifi.html` - ไฟล์ HTML (เดิม)
- `wifi_api.php` - PHP API (เดิม)
- `wifi_scanner.py` - Python scanner (เดิม)
