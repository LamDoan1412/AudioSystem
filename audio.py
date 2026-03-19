"""
audio.py
────────────────────────────────────────────
Module xử lý âm thanh:
  - Ghi âm từ microphone
  - Phát lại file âm thanh (hỗ trợ đổi tốc độ)
  - Điều chỉnh âm lượng
  - Tua (seek) đến vị trí bất kỳ
  - Cắt đoạn âm thanh và lưu file mới
  - Áp dụng hiệu ứng Echo / Reverb
  - Lấy thông tin file (thời lượng, sample rate, kích thước)
"""

import os
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from effects import AudioEffects

SAMPLE_RATE  = 44100
CHANNELS     = 1
RECORD_DTYPE = "float32"


class AudioEngine:
    def __init__(self):
        self.audio_data        = None
        self.audio_sr          = SAMPLE_RATE
        self.is_recording      = False
        self.is_playing        = False
        self.record_buffer     = []
        self.playback_position = 0.0
        self.volume_factor     = 1.0
        self.speed_factor      = 1.0
        self._current_filepath = None

        self.on_save_done      = None
        self.on_playback_tick  = None
        self.on_playback_end   = None

    # ── GHI ÂM ────────────────────────────────
    def start_recording(self):
        self.is_recording  = True
        self.record_buffer = []
        threading.Thread(target=self._record_worker, daemon=True).start()

    def stop_recording(self):
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
            audio    = np.concatenate(self.record_buffer, axis=0)
            filepath = self._save_wav(audio)
            if self.on_save_done:
                self.on_save_done(filepath)

    def _save_wav(self, audio: np.ndarray) -> str:
        save_dir = os.path.join(os.path.expanduser("~"), "AudioLab_Recordings")
        os.makedirs(save_dir, exist_ok=True)
        idx      = len(os.listdir(save_dir)) + 1
        filepath = os.path.join(save_dir, f"recording_{idx:03d}.wav")
        sf.write(filepath, audio, SAMPLE_RATE)
        return filepath

    # ── TẢI FILE ──────────────────────────────
    def load_file(self, filepath: str):
        data, sr = sf.read(filepath, dtype="float32")
        if data.ndim > 1:
            data = data.mean(axis=1)
        self.audio_data        = data
        self.audio_sr          = sr
        self.playback_position = 0.0
        self._current_filepath = filepath

    @property
    def duration(self) -> float:
        if self.audio_data is None:
            return 0.0
        return len(self.audio_data) / self.audio_sr

    # ── THÔNG TIN FILE ────────────────────────
    def get_file_info(self) -> dict:
        """Trả về dict thông tin file: duration, sample_rate, filesize, format."""
        if self.audio_data is None or self._current_filepath is None:
            return {}
        total_sec  = int(self.duration)
        mins, sec  = divmod(total_sec, 60)
        size_bytes = os.path.getsize(self._current_filepath)
        size_str   = (f"{size_bytes/1024/1024:.2f} MB"
                      if size_bytes >= 1024*1024
                      else f"{size_bytes/1024:.1f} KB")
        return {
            "filename"   : os.path.basename(self._current_filepath),
            "duration"   : f"{mins:02d}:{sec:02d}",
            "sample_rate": f"{self.audio_sr} Hz",
            "samples"    : f"{len(self.audio_data):,}",
            "filesize"   : size_str,
            "format"     : os.path.splitext(self._current_filepath)[1].upper(),
        }

    # ── PHÁT LẠI ──────────────────────────────
    def play(self):
        if self.audio_data is None or self.is_playing:
            return
        self.is_playing = True
        threading.Thread(target=self._play_worker, daemon=True).start()

    def stop(self):
        self.is_playing = False
        sd.stop()

    def set_speed(self, speed: float):
        """Đặt tốc độ phát: 0.5 / 1.0 / 1.5 / 2.0"""
        self.speed_factor = speed

    def _play_worker(self):
        start = int(self.playback_position * self.audio_sr)
        data  = self.audio_data[start:] * self.volume_factor
        if self.speed_factor != 1.0:
            data = AudioEffects.change_speed(data, self.speed_factor)
        effective_sr = int(self.audio_sr * self.speed_factor)
        chunk = 2048
        idx   = 0
        with sd.OutputStream(samplerate=effective_sr, channels=1,
                              dtype="float32") as stream:
            while idx < len(data) and self.is_playing:
                block = data[idx: idx + chunk]
                stream.write(block)
                idx    += chunk
                remain  = self.duration - self.playback_position
                current = self.playback_position + (idx / len(data)) * remain
                if self.on_playback_tick:
                    self.on_playback_tick(min(current, self.duration), self.duration)
        self.is_playing = False
        if self.on_playback_end:
            self.on_playback_end()

    # ── TUA & ÂM LƯỢNG ────────────────────────
    def seek(self, seconds: float):
        self.playback_position = max(0.0, min(seconds, self.duration))

    def set_volume(self, factor: float):
        self.volume_factor = max(0.0, min(factor, 2.0))

    # ── HIỆU ỨNG ──────────────────────────────
    def apply_effect(self, effect: str) -> str:
        """
        Áp dụng hiệu ứng 'echo' hoặc 'reverb' lên audio hiện tại.
        Lưu file mới bên cạnh file gốc, trả về đường dẫn.
        """
        if self.audio_data is None:
            raise ValueError("Chưa tải file âm thanh nào.")
        if effect == "echo":
            processed = AudioEffects.echo(self.audio_data, self.audio_sr)
        elif effect == "reverb":
            processed = AudioEffects.reverb(self.audio_data, self.audio_sr)
        else:
            raise ValueError(f"Hiệu ứng '{effect}' không được hỗ trợ.")
        base      = os.path.splitext(os.path.basename(self._current_filepath))[0]
        save_dir  = os.path.dirname(self._current_filepath)
        save_path = os.path.join(save_dir, f"{base}_{effect}.wav")
        sf.write(save_path, processed, self.audio_sr)
        return save_path

    # ── CẮT ĐOẠN ──────────────────────────────
    def cut_and_save(self, start_sec: float, end_sec: float,
                     original_path: str) -> str:
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
        new_path = os.path.join(save_dir, f"{base}_cut_{start_sec:.1f}-{end_sec:.1f}.wav")
        sf.write(new_path, cut_data, self.audio_sr)
        return new_path