# 🎧 AudioSystem

AudioSystem là một ứng dụng xử lý âm thanh được xây dựng bằng Python, cung cấp các chức năng ghi âm, chỉnh sửa và trực quan hóa tín hiệu âm thanh. Dự án được phát triển nhằm hỗ trợ sinh viên và người học trong việc tìm hiểu về xử lý tín hiệu số (DSP) cũng như các kỹ thuật thao tác với dữ liệu âm thanh trong thực tế.

Ứng dụng cho phép người dùng ghi âm trực tiếp từ microphone, lưu trữ và quản lý các file âm thanh một cách thuận tiện. Bên cạnh đó, hệ thống hỗ trợ chỉnh sửa cơ bản như cắt đoạn âm thanh, thay đổi âm lượng và phát lại với các thao tác tua nhanh hoặc tua chậm. Một điểm nổi bật của dự án là khả năng hiển thị dạng sóng (waveform), giúp người dùng dễ dàng quan sát và phân tích tín hiệu âm thanh một cách trực quan.

AudioSystem được xây dựng dựa trên các thư viện phổ biến trong Python như NumPy và SciPy để xử lý dữ liệu số, Matplotlib để trực quan hóa dạng sóng, cùng với PyAudio hoặc sounddevice để thực hiện ghi và phát âm thanh. Nhờ đó, hệ thống vừa đảm bảo tính đơn giản trong triển khai, vừa đủ mạnh để phục vụ mục đích học tập và nghiên cứu.

## ⚙️ Cài đặt và sử dụng

Để cài đặt và sử dụng ứng dụng, trước tiên bạn cần clone repository về máy bằng lệnh:
git clone https://github.com/LamDoan1412/AudioSystem.git

Sau đó di chuyển vào thư mục dự án và cài đặt các thư viện cần thiết:
pip install -r requirements.txt

Cuối cùng, chạy chương trình:
python main.py

## 📁 Cấu trúc thư mục

Dự án được tổ chức theo cấu trúc rõ ràng như sau:

```
AudioSystem/
│── main.py                 # File chạy chính
│── requirements.txt        # Danh sách thư viện cần cài
│── README.md               # Tài liệu mô tả dự án
│
├── audio/                  # Chứa dữ liệu âm thanh
│   ├── input/              # File đầu vào (ghi âm)
│   └── output/             # File sau khi xử lý
│
├── utils/                  # Các module xử lý
│   ├── audio_processing.py # Xử lý âm thanh (cắt, volume,...)
│   └── visualization.py    # Hiển thị waveform
│
└── assets/                 # (Tuỳ chọn) hình ảnh, demo
```

Cấu trúc này giúp dễ dàng mở rộng và quản lý các thành phần của hệ thống, đặc biệt khi phát triển thêm các tính năng mới.

## 🚀 Định hướng phát triển

Trong tương lai, dự án có thể được mở rộng với:

* Xây dựng giao diện người dùng (GUI) bằng Tkinter hoặc PyQt
* Thêm các hiệu ứng âm thanh như reverb, echo
* Tích hợp AI để lọc nhiễu
* Hỗ trợ nhiều định dạng file âm thanh hơn

## 👨‍💻 Tác giả

Lâm họ Đoàn

## 📄 License

Dự án phục vụ mục đích học tập và nghiên cứu.

