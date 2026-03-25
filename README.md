# 🎙️ AudioLab – Ứng dụng Ghi âm & Chỉnh sửa Âm thanh

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> Ứng dụng xử lý âm thanh được xây dựng bằng Python, hỗ trợ ghi âm, chỉnh sửa, thêm hiệu ứng và trực quan hóa tín hiệu âm thanh thông qua giao diện đồ họa hiện đại.

---

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| ⏺ **Ghi âm** | Ghi âm trực tiếp từ microphone, tự động normalize và lưu file `.wav` |
| 📂 **Nhập file** | Hỗ trợ `.wav`, `.mp3`, `.ogg`, `.flac` |
| 📋 **Quản lý danh sách** | Xem, chọn, đổi tên, xóa file |
| ▶ **Phát lại** | Phát file với normalize tự động, đảm bảo nghe rõ |
| ⚡ **Đổi tốc độ** | Phát ở tốc độ `0.5x / 1.0x / 1.5x / 2.0x` |
| 🔊 **Âm lượng** | Điều chỉnh từ `0%` đến `200%` |
| ⏩ **Tua** | Kéo thanh trượt đến vị trí bất kỳ |
| 〰️ **Sóng âm** | Hiển thị waveform async khi chọn file |
| 🖼️ **Xuất PNG** | Lưu ảnh sóng âm ra file `.png` |
| 🔁 **Hiệu ứng Echo** | Thêm tiếng vọng lại, tự lưu file mới |
| 🌊 **Hiệu ứng Reverb** | Mô phỏng âm vang trong phòng, tự lưu file mới |
| ✂️ **Cắt đoạn** | Cắt theo thời gian bắt đầu/kết thúc, lưu file mới |
| ℹ️ **Thông tin file** | Hiển thị tên, thời lượng, sample rate, kích thước, định dạng |

---

## 🗂️ Cấu trúc dự án

```
AudioSystem/
│
├── main.py            ← Khởi chạy ứng dụng
├── ui.py              ← Giao diện chính (CustomTkinter)
├── audio.py           ← Xử lý âm thanh (ghi, phát, cắt, tua, normalize)
├── effects.py         ← Hiệu ứng âm thanh (Echo, Reverb, Speed)
├── file_manager.py    ← Quản lý danh sách file
├── waveform.py        ← Vẽ sóng âm async và xuất PNG
├── requirements.txt   ← Danh sách thư viện
└── README.md          ← Tài liệu dự án
```

---

## ⚙️ Cài đặt và chạy

### Yêu cầu
- Python **3.9** trở lên
- PyCharm hoặc VS Code

### Bước 1 — Clone repo
```bash
git clone https://github.com/LamDoan1412/AudioSystem.git
cd AudioSystem
```

### Bước 2 — Cài thư viện
```bash
pip install -r requirements.txt
```

### Bước 3 — Chạy ứng dụng
```bash
python main.py
```

---

## 📦 Thư viện sử dụng

| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| `customtkinter` | ≥ 5.2.0 | Giao diện đồ họa hiện đại |
| `sounddevice` | ≥ 0.4.6 | Ghi âm và phát âm thanh |
| `soundfile` | ≥ 0.12.1 | Đọc/ghi file âm thanh |
| `numpy` | ≥ 1.24.0 | Xử lý mảng tín hiệu số, normalize |
| `matplotlib` | ≥ 3.7.0 | Vẽ sóng âm (waveform) |
| `pydub` | ≥ 0.25.1 | Xử lý định dạng âm thanh |

---

## 🏗️ Kiến trúc hệ thống

```
main.py
  └── ui.py  (AudioLabApp)
        ├── audio.py        (AudioEngine)
        │     └── effects.py   (AudioEffects)
        ├── file_manager.py  (FileManager)
        └── waveform.py     (WaveformWidget)
```

Mỗi module hoạt động **độc lập**, `ui.py` kết nối tất cả thông qua callback.

---

## 💾 File ghi âm lưu tại

```
~/AudioLab_Recordings/
```
_(Tự tạo khi ghi âm lần đầu, file được normalize tự động trước khi lưu)_

---

## 👨‍💻 Nhóm phát triển

| Thành viên   | Vai trò |
|--------------|---|
| Lâm họ Đoàn  | Nhóm trưởng – Kiến trúc hệ thống, `main.py` |
| ParkDayChun  | `audio.py` – Ghi âm |
| MinhEdras    | `audio.py` – Phát lại, cắt đoạn |
| NMH          | `ui.py` – Giao diện |
| Nguyen Khoin | `waveform.py`, `file_manager.py`, `effects.py` |


---

🔗 Repository: [github.com/LamDoan1412/AudioSystem](https://github.com/LamDoan1412/AudioSystem)