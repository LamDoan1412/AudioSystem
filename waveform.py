"""
waveform.py - FIX LAG khi vẽ waveform
- draw() chạy trong thread riêng, không block UI
- Hiển thị "Đang tải..." trong lúc chờ
- canvas.draw_idle() thay vì canvas.draw() để nhẹ hơn
"""

import threading
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WaveformWidget:
    COLOR_BG        = "#1e1e2e"
    COLOR_WAVE_FILL = "#3498db"
    COLOR_WAVE_LINE = "#5dade2"
    COLOR_PLAYHEAD  = "#e74c3c"
    COLOR_AXIS      = "#3a3a5c"
    COLOR_TEXT      = "#555577"
    COLOR_TICK      = "gray"

    def __init__(self, parent):
        self._duration  = 0.0
        self._playhead  = None
        self._parent    = parent   # giữ ref để gọi after()

        self.fig = Figure(figsize=(8, 2.8), dpi=96, facecolor=self.COLOR_BG)
        self.ax  = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        widget = self.canvas.get_tk_widget()
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        widget.grid(row=0, column=0, sticky="nsew", padx=12, pady=(0, 12))

        self.reset()

    # ── VẼ WAVEFORM (ASYNC - không lag UI) ───
    def draw(self, audio_data: np.ndarray, sample_rate: int):
        """
        Vẽ sóng âm trong thread riêng.
        Hiển thị 'Đang tải...' ngay lập tức, vẽ xong mới cập nhật.
        """
        # Hiện loading ngay lập tức — không chờ
        self._show_loading()

        # Vẽ trong thread riêng
        threading.Thread(
            target=self._draw_worker,
            args=(audio_data, sample_rate),
            daemon=True
        ).start()

    def _show_loading(self):
        """Hiển thị thông báo đang tải ngay lập tức."""
        self.ax.clear()
        self.ax.text(0.5, 0.5, "⏳ Đang tải sóng âm...",
                     ha="center", va="center",
                     color="#f39c12", fontsize=12,
                     transform=self.ax.transAxes)
        self._apply_style()
        self.canvas.draw_idle()   # nhẹ hơn canvas.draw()

    def _draw_worker(self, audio_data: np.ndarray, sample_rate: int):
        """Tính toán waveform trong thread nền."""
        self._duration = len(audio_data) / sample_rate
        self._playhead = None

        # Downsample để vẽ nhanh
        max_pts = 6000   # giảm từ 8000 → 6000 cho nhẹ hơn
        step    = max(1, len(audio_data) // max_pts)
        samples = audio_data[::step]
        times   = np.linspace(0, self._duration, len(samples))

        # Cập nhật UI trong main thread
        self._parent.after(0, lambda: self._render(times, samples))

    def _render(self, times, samples):
        """Render waveform trên main thread sau khi tính toán xong."""
        self.ax.clear()
        self.ax.fill_between(times, samples, alpha=0.55, color=self.COLOR_WAVE_FILL)
        self.ax.plot(times, samples, color=self.COLOR_WAVE_LINE,
                     linewidth=0.6, alpha=0.85)
        self._apply_style()
        self.ax.set_xlim(0, self._duration)
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw_idle()   # ✅ nhẹ hơn canvas.draw()

    # ── PLAYHEAD ──────────────────────────────
    def set_playhead(self, current_sec: float):
        if self._duration <= 0:
            return
        if self._playhead is not None:
            try:
                self._playhead.remove()
            except Exception:
                pass
        self._playhead = self.ax.axvline(
            x=current_sec, color=self.COLOR_PLAYHEAD,
            linewidth=1.5, alpha=0.85)
        self.canvas.draw_idle()

    # ── RESET ─────────────────────────────────
    def reset(self):
        self._duration = 0.0
        self._playhead = None
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Chọn file để hiển thị sóng âm",
                     ha="center", va="center",
                     color=self.COLOR_TEXT, fontsize=12,
                     transform=self.ax.transAxes)
        self._apply_style()
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw_idle()

    # ── XUẤT PNG ──────────────────────────────
    def export_png(self, save_path: str):
        if self._duration <= 0:
            raise ValueError("Chưa có sóng âm để xuất!")
        self.fig.savefig(save_path, dpi=150, bbox_inches="tight",
                         facecolor=self.COLOR_BG)
        return save_path

    # ── NỘI BỘ ────────────────────────────────
    def _apply_style(self):
        self.ax.set_facecolor(self.COLOR_BG)
        self.ax.tick_params(colors=self.COLOR_TICK, labelsize=8)
        self.ax.set_xlabel("Thời gian (s)", color=self.COLOR_TICK, fontsize=9)
        self.ax.set_ylabel("Biên độ",       color=self.COLOR_TICK, fontsize=9)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(self.COLOR_AXIS)