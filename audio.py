"""
audio.py
────────────────────────────────────────────
Module xử lý âm thanh:
  - Ghi âm từ microphone
  - Phát lại file âm thanh
  - Điều chỉnh âm lượng
  - Tua (seek) đến vị trí bất kỳ
  - Cắt đoạn âm thanh và lưu file mới
"""

import os
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE  = 44100
CHANNELS     = 1
RECORD_DTYPE = "float32"


class AudioEngine:
    def __init__(self):
        self.audio_data        = None   # numpy array dữ liệu âm thanh hiện tại
        self.audio_sr          = SAMPLE_RATE
        self.is_recording      = False
        self.is_playing        = False
        self.record_buffer     = []
        self.playback_position = 0.0    # vị trí hiện tại (giây)
        self.volume_factor     = 1.0    # hệ số âm lượng (0.0 – 2.0)

        # Callback gọi lên UI khi có sự kiện
        self.on_save_done      = None   # fn(filepath)
        self.on_playback_tick  = None   # fn(current_sec, total_sec)
        self.on_playback_end   = None   # fn()

    # ──────────────────────────────────────────
    #  GHI ÂM
    # ──────────────────────────────────────────
    def start_recording(self):
        """Bắt đầu ghi âm từ microphone trong luồng nền."""
        self.is_recording  = True
        self.record_buffer = []
        threading.Thread(target=self._record_worker, daemon=True).start()

    def stop_recording(self):
        """Dừng ghi âm."""
        self.is_recording = False

    def _record_worker(self):
        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.record_buffer.append(indata.copy())

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                            dtype=RECORD_DTYPE, callback=callback):
            while self.is_recording:
                sd.sleep(100)

        if self.record_buffer:
            audio = np.concatenate(self.record_buffer, axis=0)
            filepath = self._save_wav(audio)
            if self.on_save_done:
                self.on_save_done(filepath)

    def _save_wav(self, audio: np.ndarray) -> str:
        """Lưu mảng numpy thành file .wav, trả về đường dẫn."""
        save_dir = os.path.join(os.path.expanduser("~"), "AudioLab_Recordings")
        os.makedirs(save_dir, exist_ok=True)
        idx      = len(os.listdir(save_dir)) + 1
        filepath = os.path.join(save_dir, f"recording_{idx:03d}.wav")
        sf.write(filepath, audio, SAMPLE_RATE)
        return filepath

    # ──────────────────────────────────────────
    #  TẢI FILE
    # ──────────────────────────────────────────
    def load_file(self, filepath: str):
        """Đọc file âm thanh vào bộ nhớ."""
        data, sr = sf.read(filepath, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)   # chuyển về mono
        self.audio_data        = data
        self.audio_sr          = sr
        self.playback_position = 0.0

    @property
    def duration(self) -> float:
        """Thời lượng (giây) của file đang tải."""
        if self.audio_data is None:
            return 0.0
        return len(self.audio_data) / self.audio_sr

    # ──────────────────────────────────────────
    #  PHÁT LẠI
    # ──────────────────────────────────────────
    def play(self):
        """Phát từ vị trí playback_position."""
        if self.audio_data is None or self.is_playing:
            return
        self.is_playing = True
        threading.Thread(target=self._play_worker, daemon=True).start()

    def stop(self):
        """Dừng phát."""
        self.is_playing = False
        sd.stop()

    def _play_worker(self):
        start  = int(self.playback_position * self.audio_sr)
        data   = self.audio_data[start:] * self.volume_factor
        chunk  = 2048
        idx    = 0

        with sd.OutputStream(samplerate=self.audio_sr, channels=1,
                              dtype="float32") as stream:
            while idx < len(data) and self.is_playing:
                block = data[idx: idx + chunk]
                stream.write(block)
                idx  += chunk
                current = self.playback_position + idx / self.audio_sr
                if self.on_playback_tick:
                    self.on_playback_tick(min(current, self.duration), self.duration)

        self.is_playing = False
        if self.on_playback_end:
            self.on_playback_end()

    # ──────────────────────────────────────────
    #  TUA & ÂM LƯỢNG
    # ──────────────────────────────────────────
    def seek(self, seconds: float):
        """Tua đến vị trí (giây)."""
        self.playback_position = max(0.0, min(seconds, self.duration))

    def set_volume(self, factor: float):
        """Đặt hệ số âm lượng (0.0 = tắt, 1.0 = gốc, 2.0 = gấp đôi)."""
        self.volume_factor = max(0.0, min(factor, 2.0))

    # ──────────────────────────────────────────
    #  CẮT ĐOẠN
    # ──────────────────────────────────────────
    def cut_and_save(self, start_sec: float, end_sec: float,
                     original_path: str) -> str:
        """
        Cắt đoạn [start_sec, end_sec] của audio hiện tại
        và lưu thành file mới bên cạnh file gốc.
        Trả về đường dẫn file mới.
        """
        if self.audio_data is None:
            raise ValueError("Chưa tải file âm thanh nào.")
        if not (0 <= start_sec < end_sec <= self.duration):
            raise ValueError(
                f"Thời gian không hợp lệ! (0 ≤ start < end ≤ {self.duration:.1f}s)")

        s_idx    = int(start_sec * self.audio_sr)
        e_idx    = int(end_sec   * self.audio_sr)
        cut_data = self.audio_data[s_idx:e_idx]

        base     = os.path.splitext(os.path.basename(original_path))[0]
        save_dir = os.path.dirname(original_path)
        new_path = os.path.join(
            save_dir, f"{base}_cut_{start_sec:.1f}-{end_sec:.1f}.wav")
        sf.write(new_path, cut_data, self.audio_sr)
        return new_path