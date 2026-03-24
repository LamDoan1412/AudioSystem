"""
audio.py - FIX LAG khi load file
- load_file() chạy trong thread riêng, không block UI
- _play_worker() không normalize toàn bộ mảng trước khi phát
- Thêm callback on_load_done để UI biết khi nào load xong
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

        # Callbacks
        self.on_save_done      = None   # fn(filepath)
        self.on_load_done      = None   # fn()  ← MỚI: báo load xong
        self.on_load_error     = None   # fn(msg) ← MỚI: báo lỗi load
        self.on_playback_tick  = None   # fn(current, total)
        self.on_playback_end   = None   # fn()

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
                # Convert về mono ngay trong callback
                chunk = indata.copy()
                if chunk.ndim > 1:
                    chunk = chunk.mean(axis=1, keepdims=True)
                self.record_buffer.append(chunk)

        # Lấy số channel thực của mic để tránh lỗi trên Windows
        try:
            device_info = sd.query_devices(kind="input")
            in_channels = min(int(device_info["max_input_channels"]), 2)
        except Exception:
            in_channels = 1

        with sd.InputStream(samplerate=SAMPLE_RATE,
                            channels=in_channels,
                            dtype=RECORD_DTYPE,
                            callback=callback):
            while self.is_recording:
                sd.sleep(100)

        if self.record_buffer:
            audio = np.concatenate(self.record_buffer, axis=0)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            audio = audio.astype(np.float32)
            filepath = self._save_wav(audio)
            if self.on_save_done:
                self.on_save_done(filepath)

    def _save_wav(self, audio: np.ndarray) -> str:
        save_dir = os.path.join(os.path.expanduser("~"), "AudioLab_Recordings")
        os.makedirs(save_dir, exist_ok=True)
        idx      = len(os.listdir(save_dir)) + 1
        filepath = os.path.join(save_dir, f"recording_{idx:03d}.wav")
        # Lưu mono rõ ràng dạng PCM_16
        sf.write(filepath, audio.flatten(), SAMPLE_RATE, subtype="PCM_16")
        print(f"[AudioEngine] Đã lưu: {filepath}")
        return filepath

    # ── TẢI FILE (ASYNC - không lag UI) ───────
    def load_file(self, filepath: str):
        """
        Load file trong thread riêng — KHÔNG block UI.
        Kết quả trả về qua:
            on_load_done()        khi xong
            on_load_error(msg)    khi lỗi
        """
        threading.Thread(
            target=self._load_worker,
            args=(filepath,),
            daemon=True
        ).start()

    def _load_worker(self, filepath: str):
        try:
            data, sr = sf.read(filepath, dtype="float32")
            if data.ndim > 1:
                data = data.mean(axis=1)   # stereo → mono

            # Lưu vào engine
            self.audio_data        = data
            self.audio_sr          = sr
            self.playback_position = 0.0
            self._current_filepath = filepath

            print(f"[AudioEngine] Load xong: {os.path.basename(filepath)} "
                  f"| {self.duration:.1f}s | {sr}Hz")

            if self.on_load_done:
                self.on_load_done()

        except Exception as e:
            print(f"[AudioEngine] Lỗi load: {e}")
            if self.on_load_error:
                self.on_load_error(str(e))

    @property
    def duration(self) -> float:
        if self.audio_data is None:
            return 0.0
        return len(self.audio_data) / self.audio_sr

    # ── THÔNG TIN FILE ────────────────────────
    def get_file_info(self) -> dict:
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
        self.speed_factor = speed

    def _play_worker(self):
        start = int(self.playback_position * self.audio_sr)
        # Lấy slice — KHÔNG copy toàn bộ mảng
        data  = self.audio_data[start:]

        # Áp dụng volume và clip theo từng chunk thay vì toàn bộ
        if self.speed_factor != 1.0:
            data = AudioEffects.change_speed(data, self.speed_factor)

        effective_sr = int(self.audio_sr * self.speed_factor)
        chunk        = 4096   # tăng chunk size để giảm overhead
        idx          = 0
        total        = len(data)

        with sd.OutputStream(samplerate=effective_sr, channels=1,
                              dtype="float32") as stream:
            while idx < total and self.is_playing:
                block = data[idx: idx + chunk].copy()

                # ✅ Xử lý volume THEO TỪNG CHUNK — không lag
                block = block * self.volume_factor
                np.clip(block, -1.0, 1.0, out=block)

                stream.write(block)
                idx += chunk

                remain  = self.duration - self.playback_position
                current = self.playback_position + (idx / total) * remain
                if self.on_playback_tick:
                    self.on_playback_tick(min(current, self.duration), self.duration)

        self.is_playing = False
        if self.on_playback_end:
            self.on_playback_end()

    # ── TUA & ÂM LƯỢNG ────────────────────────
    def seek(self, seconds: float):
        self.playback_position = max(0.0, min(seconds, self.duration))

    def set_volume(self, factor: float):
        self.volume_factor = max(0.0, min(factor, 5.0))

    # ── HIỆU ỨNG ──────────────────────────────
    def apply_effect(self, effect: str) -> str:
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
        new_path = os.path.join(save_dir,
                                f"{base}_cut_{start_sec:.1f}-{end_sec:.1f}.wav")
        sf.write(new_path, cut_data, self.audio_sr)
        return new_path