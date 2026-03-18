"""
waveform.py
────────────────────────────────────────────
Module hiển thị sơ đồ sóng âm (waveform):
  - Vẽ waveform từ numpy array
  - Vẽ đường chỉ vị trí phát hiện tại
  - Reset về trạng thái rỗng
  - Tích hợp vào khung CTkFrame bất kỳ
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WaveformWidget:
    """
    Widget sóng âm nhúng vào một CTkFrame.

    Cách dùng:
        wf = WaveformWidget(parent_frame)
        wf.draw(audio_data, sample_rate)
        wf.set_playhead(current_sec)
        wf.reset()
    """

    # Màu sắc
    COLOR_BG        = "#1e1e2e"
    COLOR_WAVE_FILL = "#3498db"
    COLOR_WAVE_LINE = "#5dade2"
    COLOR_PLAYHEAD  = "#e74c3c"
    COLOR_AXIS      = "#3a3a5c"
    COLOR_TEXT      = "#555577"
    COLOR_TICK      = "gray"

    def __init__(self, parent):
        self._duration    = 0.0
        self._playhead    = None   # đối tượng Line2D

        # Tạo Figure & Axes
        self.fig = Figure(figsize=(8, 2.8), dpi=96, facecolor=self.COLOR_BG)
        self.ax  = self.fig.add_subplot(111)

        # Nhúng vào tkinter (dùng grid để đồng nhất với ui.py)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        widget = self.canvas.get_tk_widget()
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        widget.grid(row=0, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.reset()

    # ──────────────────────────────────────────
    #  VẼ WAVEFORM
    # ──────────────────────────────────────────
    def draw(self, audio_data: np.ndarray, sample_rate: int):
        """Vẽ sóng âm từ mảng audio_data (mono, float32)."""
        self._duration = len(audio_data) / sample_rate
        self.ax.clear()
        self._playhead = None

        # Downsample để vẽ nhanh
        max_pts = 8000
        step    = max(1, len(audio_data) // max_pts)
        samples = audio_data[::step]
        times   = np.linspace(0, self._duration, len(samples))

        self.ax.fill_between(times, samples, alpha=0.55, color=self.COLOR_WAVE_FILL)
        self.ax.plot(times, samples, color=self.COLOR_WAVE_LINE,
                     linewidth=0.6, alpha=0.85)

        self._apply_style()
        self.ax.set_xlim(0, self._duration)
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw()

    # ──────────────────────────────────────────
    #  VẼ ĐƯỜNG PLAYHEAD
    # ──────────────────────────────────────────
    def set_playhead(self, current_sec: float):
        """Cập nhật vị trí đường chỉ phát (màu đỏ)."""
        if self._duration <= 0:
            return

        # Xóa playhead cũ
        if self._playhead is not None:
            try:
                self._playhead.remove()
            except Exception:
                pass

        self._playhead = self.ax.axvline(
            x=current_sec, color=self.COLOR_PLAYHEAD,
            linewidth=1.5, alpha=0.85)
        self.canvas.draw_idle()

    # ──────────────────────────────────────────
    #  RESET
    # ──────────────────────────────────────────
    def reset(self):
        """Xóa sóng âm, hiển thị thông báo rỗng."""
        self._duration = 0.0
        self._playhead = None
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Chọn file để hiển thị sóng âm",
                     ha="center", va="center",
                     color=self.COLOR_TEXT, fontsize=12,
                     transform=self.ax.transAxes)
        self._apply_style()
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw()

    # ──────────────────────────────────────────
    #  NỘI BỘ
    # ──────────────────────────────────────────
    def _apply_style(self):
        """Áp dụng màu nền, trục, nhãn chung."""
        self.ax.set_facecolor(self.COLOR_BG)
        self.ax.tick_params(colors=self.COLOR_TICK, labelsize=8)
        self.ax.set_xlabel("Thời gian (s)", color=self.COLOR_TICK, fontsize=9)
        self.ax.set_ylabel("Biên độ",       color=self.COLOR_TICK, fontsize=9)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(self.COLOR_AXIS)