"""
main.py
────────────────────────────────────────────
Entry point của ứng dụng AudioLab.
Chỉ cần chạy file này để khởi động toàn bộ app.

Cách chạy:
    python main.py
"""

from ui import AudioLabApp


def main():
    app = AudioLabApp()
    app.mainloop()


if __name__ == "__main__":
    main()