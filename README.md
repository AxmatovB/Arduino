# 🖐 Hand Panel

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.13-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-00897B?style=for-the-badge&logo=google&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-UNO-00979D?style=for-the-badge&logo=arduino&logoColor=white)
![TFT](https://img.shields.io/badge/TFT-ST7789_240x240-E91E63?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-F7B731?style=for-the-badge)

**Kamera orqali barmoqlarni aniqlash → Arduino → TFT displey boshqarish tizimi**

[🔌 Ulanish sxemalari](#-ulanish-sxemalari) · [📦 O'rnatish](#-ornatish) · [🚀 Ishga tushirish](#-ishga-tushirish) · [⚙️ Sozlamalar](#%EF%B8%8F-sozlamalar) · [🤖 Auto-Run](#-auto-run-udev--systemd)

</div>

---

## ✨ Xususiyatlar

| 🎯 Funksiya | 📋 Tavsif |
|---|---|
| 🖐 Barmoq aniqlash | MediaPipe orqali real-time hand tracking |
| 🔢 1–5 signal | Barmoqlar soni Arduino'ga serial orqali yuboriladi |
| 🖥️ TFT displey | Arduino ST7789 240×240 ekranda raqam ko'rsatadi |
| 📷 Kamera flip | Oyna ko'rinishi (selfie-friendly) |
| ⚡ Stabilizatsiya | 6 kadr davomida barqaror signal talab qilinadi |
| 🔌 Auto-detect | Arduino porti avtomatik topiladi |
| 🛡️ Uzilish xavfsizligi | Qurilma uzilsa ilova o'zi yopiladi |

---

## 🗺️ Umumiy arxitektura

```
             USB (Serial 115200 baud)
[Arduino UNO] <══════════════════════> [Linux PC (Python app.py)]
      │                                          │
      │ SPI                                      │ V4L2
      ▼                                          ▼
[TFT ST7789]                               [Webcam 📷]
(qora fon,                             (barmoq 1..5 aniqlanadi)
 yashil raqam)
```

---

## 🔌 Ulanish sxemalari

### 1. Arduino UNO ↔ Linux PC

```
┌─────────────────┐        USB kabel        ┌──────────────────┐
│   Arduino UNO   │ ══════════════════════> │    Linux PC      │
│                 │                          │                  │
│  USB (COM port) │ <──── Serial data ─────  │  /dev/ttyACM0   │
│                 │       (PC yuboradi:       │  115200 baud     │
│                 │        "0".."5\n")        │                  │
└─────────────────┘                          └──────────────────┘
```

> **Eslatma:** Linux'da Arduino odatda `/dev/ttyACM0` yoki `/dev/ttyUSB0` sifatida ko'rinadi.
> Portni tekshirish: `ls /dev/ttyACM* /dev/ttyUSB*`

---

### 📸 Haqiqiy ulanish ko'rinishi

> Quyida loyihaning yig'ilgan holati ko'rsatilgan (Arduino UNO + Breadboard + TFT ST7789):

![Wiring Photo](img/wiring_photo.jpg)

---

### 2. Arduino UNO ↔ TFT ST7789 (240×240, SPI)

```
┌──────────────────────────────────────────────────────────┐
│                   SPI ULANISH JADVALI                    │
├─────────────────┬──────────────┬─────────────────────────┤
│  TFT ST7789     │    Kabel     │  Arduino UNO             │
│  (pin nomi)     │              │  (pin nomi)              │
├─────────────────┼──────────────┼─────────────────────────┤
│  SCK            │ ──────────>  │  D13  (SPI SCK)          │
│  SDA / MOSI     │ ──────────>  │  D11  (SPI MOSI)         │
│  RES / RST      │ ──────────>  │  D8                      │
│  DC             │ ──────────>  │  D9                      │
│  VCC            │ ──────────>  │  3.3V  ⚠️ (5V emas!)    │
│  BLK (backlight)│ ──────────>  │  3.3V                    │
│  GND            │ ──────────>  │  GND                     │
└─────────────────┴──────────────┴─────────────────────────┘
```

> ⚠️ **Muhim:** ST7789 **3.3V** bilan ishlaydi. 5V ulasangiz displey shikastlanishi mumkin!

**Vizual sxema:**

```
Arduino UNO                        TFT ST7789
   ┌──────┐                        ┌─────────┐
   │  D13 │━━━━━━━━━━━━━━━━━━━━━━▶│ SCK     │
   │  D11 │━━━━━━━━━━━━━━━━━━━━━━▶│ SDA     │
   │   D8 │━━━━━━━━━━━━━━━━━━━━━━▶│ RES     │
   │   D9 │━━━━━━━━━━━━━━━━━━━━━━▶│ DC      │
   │ 3.3V │━━━━━━━━━━━━━━━━━━━━━━▶│ VCC     │
   │ 3.3V │━━━━━━━━━━━━━━━━━━━━━━▶│ BLK     │
   │  GND │━━━━━━━━━━━━━━━━━━━━━━▶│ GND     │
   └──────┘                        └─────────┘
```

---

## 🔄 Ish jarayoni (Flow Diagrams)

### 2.1 Arduino ulanganda — avtomatik ishga tushish

```
      [Arduino UNO USB portga ulanadi]
                    │
                    ▼
      [Linux kernel /dev/ttyACM0 yaratadi]
                    │
                    ▼
      [udev: 99-hand-panel.rules ishlaydi]
                    │
                    ▼
      [systemd --user hand-panel.service START]
                    │
                    ▼
          [Python app.py ishga tushadi]
                    │
                    ▼
      [Kamera ochiladi + GUI oynasi chiqadi]
                    │
                    ▼
         [Barmoqlarni kuzatish boshlaydi 👁️]
```

---

### 2.2 Kamera barmoqni ko'radi (1..5)

```
          [Kamera frame 📷]
                 │
                 ▼
     [MediaPipe Hand Tracking 🧠]
                 │
                 ▼
       [Barmoq soni: 1..5 yoki 0]
                 │
         ┌───────┴────────────┐
         │                    │
         ▼                    ▼
  [PC oynada               [Serial orqali
   indikator]               Arduino'ga]
   (1..5 doira,              yuboradi:
    qizil rang)              "1\n" .. "5\n"
                              yoki "0\n"
```

---

### 2.3 Arduino raqamni TFT'da ko'rsatadi

```
     [Arduino Serial portdan o'qiydi]
                 │
         ┌───────┴──────────────┐
         │                      │
         ▼                      ▼
   ['1'..'5' keldi]         ['0' keldi]
         │                      │
         ▼                      ▼
   [TFT: qora fon +        [TFT: qora fon
    yashil katta             (tozalaydi,
    raqam chiqadi]            hech narsa yo'q)]
```

---

### 2.4 Qo'l ko'rinmasa (hech narsa aniqlanmadi)

```
    [MediaPipe: qo'l topilmadi 🤷]
                 │
                 ▼
           [active = 0]
                 │
                 ▼
     [Python → Arduino: "0\n"]
                 │
                 ▼
       [TFT: qora fon (bo'sh)]
```

---

### 2.5 Arduino uzilsa — ilova o'zi yopiladi

```
     [Arduino USB kabeldan uzildi 🔌]
                 │
                 ▼
     [Linux: /dev/ttyACM0 yo'qoldi]
                 │
                 ▼
     [Python: os.path.exists(port) → False]
                 │
                 ▼
         [Python: STOP signali]
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
  [Kamera yopiladi]  [GUI oyna yopiladi]
         │                │
         └───────┬────────┘
                 ▼
          [Ilova tugadi ✅]
```

---

### 2.6 To'liq blok diagramma

```
┌──────────────────────────────────────────────────────────────┐
│                        LINUX PC                              │
│                                                              │
│   ┌──────────┐    ┌───────────────┐    ┌─────────────────┐  │
│   │  Webcam  │───▶│   MediaPipe   │───▶│  Stabilizer     │  │
│   │  📷      │    │  Hand Track   │    │  (6 frames)     │  │
│   └──────────┘    └───────────────┘    └────────┬────────┘  │
│                                                  │           │
│                   ┌──────────────────────────────┘           │
│                   │                                          │
│          ┌────────┴────────┐                                 │
│          │                 │                                 │
│          ▼                 ▼                                 │
│   ┌─────────────┐   ┌─────────────────┐                     │
│   │  GUI oyna   │   │  Serial Writer  │                     │
│   │  (indikator)│   │  "N\n" → port   │                     │
│   └─────────────┘   └────────┬────────┘                     │
└────────────────────────────  │  ────────────────────────────┘
                                │ USB
                                ▼
              ┌─────────────────────────────┐
              │         Arduino UNO         │
              │                             │
              │   Serial.read() → raqam     │
              │          │                  │
              │          ▼                  │
              │   ┌─────────────┐           │
              │   │  TFT ST7789 │           │
              │   │  240×240    │           │
              │   │  (SPI)      │           │
              │   └─────────────┘           │
              └─────────────────────────────┘
```

---

## 📦 O'rnatish

### Talablar

- 🐍 **Python 3.11**
- 📷 **Veb-kamera** (USB yoki ichki)
- 🔌 **Arduino UNO** (USB orqali ulangan)
- 🖥️ **TFT ST7789** 240×240 displey
- 🐧 **Linux** (Ubuntu/Debian tavsiya etiladi)

---

### 🔧 Bosqichma-bosqich o'rnatish

**1. Reponi klonlash**

```bash
git clone https://github.com/username/hand-panel.git
cd hand-panel
```

**2. Python 3.11 mavjudligini tekshirish**

```bash
python3.11 -V
```

> Yo'q bo'lsa:
> ```bash
> sudo apt install -y python3.11 python3.11-venv
> ```

**3. Virtual muhit yaratish**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**4. Paketlarni o'rnatish**

```bash
pip install -r requirements.txt
```

> ⏳ MediaPipe va OpenCV yuklanishi bir oz vaqt olishi mumkin — sabr qiling!

---

## 🚀 Ishga tushirish

Arduino'ni ulang va:

```bash
source .venv/bin/activate
python app.py
```

Chiqish uchun kamera oynasida **`Q`** tugmasini bosing.

---

## ⚙️ Sozlamalar

`app.py` faylining boshida barcha sozlamalar joylashgan:

```python
CAMERA_INDEX           = 0      # Kamera raqami (0, 1, 2...)
SER_BAUD               = 115200 # Serial tezlik (Arduino bilan bir xil bo'lishi shart)
STABLE_FRAMES_REQUIRED = 6      # Barqarorlik uchun kadr soni
SEND_COOLDOWN_SEC      = 0.12   # Signallar orasidagi minimal vaqt (soniya)
```

> 💡 Agar kamera ochilmasa, `CAMERA_INDEX`ni `1` yoki `2` qilib ko'ring.

---

## 🤖 Auto-Run (udev + systemd)

Arduino ulanganda ilova **avtomatik** ishga tushishi uchun:

### Qadam 1 — Arduino ID sini aniqlash

```bash
lsusb
# Misol: Bus 001 Device 005: ID 2341:0043 Arduino SA Uno R3
#                               ^^^^ ^^^^
#                            idVendor idProduct
```

`99-hand-panel.rules` faylini oching va o'z qiymatlaringizni kiriting:

```
ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", ...
```

### Qadam 2 — udev rule o'rnatish

```bash
sudo cp 99-hand-panel.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Qadam 3 — systemd user service o'rnatish

```bash
mkdir -p ~/.config/systemd/user
cp hand-panel.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable hand-panel.service
```

### Qadam 4 — Tekshirish

```bash
# Service holati
systemctl --user status hand-panel.service

# Real-time log
journalctl --user -u hand-panel.service -f
```

---

## 📁 Loyiha tuzilishi

```
hand-panel/
├── app.py                  # Asosiy dastur (Python)
├── requirements.txt        # Python paketlari ro'yxati
├── hand-panel.service      # systemd user service fayli
├── 99-hand-panel.rules     # udev avtomatik ishga tushirish qoidasi
├── img/
│   └── wiring_photo.jpg    # Yig'ilgan sxema rasmi
└── README.md               # Shu fayl
```

---

## 🛠️ Muammolar va yechimlar

<details>
<summary>❌ <b>Arduino topilmadi — "Arduino topilmadi (/dev/ttyACM*)"</b></summary>

```bash
# Portni tekshiring
ls /dev/ttyACM* /dev/ttyUSB*

# Ruxsat bering (keyin tizimdan chiqib qayta kiring)
sudo usermod -aG dialout $USER

# Portni qo'lda ko'rsatish uchun app.py ni o'zgartiring:
# ser = serial.Serial("/dev/ttyACM0", SER_BAUD, timeout=0.1)
```
</details>

<details>
<summary>❌ <b>Kamera ochilmadi</b></summary>

```bash
# Mavjud kameralarni ko'ring
ls /dev/video*

# app.py da CAMERA_INDEX ni o'zgartiring: 0, 1, 2...
```
</details>

<details>
<summary>❌ <b>TFT ekranda hech narsa ko'rinmaydi</b></summary>

- VCC va BLK pinlari **3.3V**ga ulangan-mi tekshiring (5V emas!)
- DC va RST pinlari to'g'ri ulanganmi tekshiring (D9, D8)
- Arduino sketch'da `TFT_DC` va `TFT_RST` pin raqamlari mos kelishi shart
</details>

<details>
<summary>❌ <b>MediaPipe o'rnatilmadi / xato beradi</b></summary>

```bash
pip install --upgrade pip setuptools wheel
pip install mediapipe==0.10.14
```
</details>

<details>
<summary>❌ <b>Permission denied (serial port)</b></summary>

```bash
sudo usermod -aG dialout $USER
# Tizimdan chiqib qayta kiring yoki:
newgrp dialout
```
</details>

<details>
<summary>❌ <b>systemd service ishlamayapti</b></summary>

```bash
# Xato loglarini ko'ring
journalctl --user -u hand-panel.service -n 50

# Service ni restart qiling
systemctl --user restart hand-panel.service

# hand-panel.service ichidagi yo'llar to'g'riligini tekshiring
# ExecStart= da to'liq yo'l bo'lishi shart, masalan:
# ExecStart=/home/user/hand-panel/.venv/bin/python /home/user/hand-panel/app.py
```
</details>

---

## 🤝 Hissa qo'shish

Pull request'lar qabul qilinadi! Katta o'zgarishlar uchun avval `Issue` oching.

1. Reponi fork qiling
2. Branch yarating: `git checkout -b feature/yangi-funksiya`
3. O'zgarishlarni commit qiling: `git commit -m "Yangi funksiya qo'shildi"`
4. Push qiling: `git push origin feature/yangi-funksiya`
5. Pull Request yuboring

---

## 📄 Litsenziya

MIT © 2025 — Erkin foydalaning, o'zgartiring, tarqating.

---

<div align="center">

**⭐ Foydali bo'lsa, yulduzcha bosishni unutmang!**

Made with ❤️ + 🖐 + ⚡

</div>
