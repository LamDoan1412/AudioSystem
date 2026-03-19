"""
effects.py
────────────────────────────────────────────
Module hiệu ứng âm thanh:
  - Echo
  - Reverb
  - Đổi tốc độ phát (Speed)
"""

import numpy as np


class AudioEffects:

    # ──────────────────────────────────────────
    #  ECHO
    # ──────────────────────────────────────────
    @staticmethod
    def echo(audio: np.ndarray, sample_rate: int,
             delay_sec: float = 0.3, decay: float = 0.5) -> np.ndarray:
        """
        Thêm hiệu ứng Echo vào âm thanh.
        delay_sec : độ trễ (giây) giữa các tiếng vọng
        decay     : hệ số giảm dần (0.0 – 1.0)
        """
        delay_samples = int(delay_sec * sample_rate)
        result = audio.copy()
        # Cộng 3 lần tiếng vọng giảm dần
        for i in range(1, 4):
            shift  = delay_samples * i
            factor = decay ** i
            if shift < len(audio):
                result[shift:] += audio[:-shift] * factor
        # Chuẩn hóa để tránh clipping
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val * 0.95
        return result.astype(np.float32)

    # ──────────────────────────────────────────
    #  REVERB
    # ──────────────────────────────────────────
    @staticmethod
    def reverb(audio: np.ndarray, sample_rate: int,
               room_size: float = 0.5, damping: float = 0.4) -> np.ndarray:
        """
        Thêm hiệu ứng Reverb (mô phỏng âm vang phòng).
        room_size : kích thước phòng (0.1 – 1.0)
        damping   : độ hấp thụ âm thanh (0.0 – 1.0)
        """
        # Tạo nhiều delay ngắn để mô phỏng reverb
        delays_ms = [13, 19, 29, 37, 43, 53]
        result    = audio.copy()

        for d_ms in delays_ms:
            delay  = int(d_ms * room_size * sample_rate / 1000)
            factor = (1.0 - damping) * 0.25
            if delay < len(audio):
                result[delay:] += audio[:-delay] * factor

        # Chuẩn hóa
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val * 0.95
        return result.astype(np.float32)

    # ──────────────────────────────────────────
    #  ĐỔI TỐC ĐỘ PHÁT
    # ──────────────────────────────────────────
    @staticmethod
    def change_speed(audio: np.ndarray, speed: float) -> np.ndarray:
        """
        Thay đổi tốc độ phát bằng cách resample.
        speed : 0.5 = chậm 2x | 1.0 = gốc | 1.5 = nhanh 1.5x | 2.0 = nhanh 2x
        """
        if speed == 1.0:
            return audio
        # Tính số mẫu mới
        new_length = int(len(audio) / speed)
        indices    = np.linspace(0, len(audio) - 1, new_length)
        # Nội suy tuyến tính
        result = np.interp(indices, np.arange(len(audio)), audio)
        return result.astype(np.float32)