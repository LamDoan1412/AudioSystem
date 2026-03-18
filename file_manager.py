"""
file_manager.py
────────────────────────────────────────────
Module quản lý danh sách file ghi âm:
  - Thêm file vào danh sách
  - Xóa file khỏi danh sách
  - Đổi tên file trên ổ đĩa
  - Lấy tên hiển thị, đường dẫn theo index
"""

import os


class FileManager:
    def __init__(self):
        self._files = []   # danh sách đường dẫn tuyệt đối

    # ──────────────────────────────────────────
    #  THÊM FILE
    # ──────────────────────────────────────────
    def add(self, filepath: str):
        """Thêm một đường dẫn vào danh sách (nếu chưa có)."""
        filepath = os.path.abspath(filepath)
        if filepath not in self._files:
            self._files.append(filepath)

    def add_many(self, filepaths):
        """Thêm nhiều file cùng lúc."""
        for fp in filepaths:
            self.add(fp)

    # ──────────────────────────────────────────
    #  XÓA FILE
    # ──────────────────────────────────────────
    def remove(self, index: int):
        """Xóa file khỏi danh sách theo index (KHÔNG xóa file trên ổ đĩa)."""
        if not self._valid(index):
            raise IndexError(f"Index {index} không hợp lệ.")
        self._files.pop(index)

    # ──────────────────────────────────────────
    #  ĐỔI TÊN
    # ──────────────────────────────────────────
    def rename(self, index: int, new_name: str) -> str:
        """
        Đổi tên file trên ổ đĩa và cập nhật danh sách.
        new_name: tên mới KHÔNG có phần mở rộng.
        Trả về đường dẫn mới.
        """
        if not self._valid(index):
            raise IndexError(f"Index {index} không hợp lệ.")
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Tên file không được để trống.")

        old_path = self._files[index]
        ext      = os.path.splitext(old_path)[1]
        new_path = os.path.join(os.path.dirname(old_path), new_name + ext)

        if os.path.exists(new_path) and new_path != old_path:
            raise FileExistsError(f"File '{new_name + ext}' đã tồn tại.")

        os.rename(old_path, new_path)
        self._files[index] = new_path
        return new_path

    # ──────────────────────────────────────────
    #  TRUY XUẤT
    # ──────────────────────────────────────────
    def get_path(self, index: int) -> str:
        """Lấy đường dẫn đầy đủ theo index."""
        if not self._valid(index):
            raise IndexError(f"Index {index} không hợp lệ.")
        return self._files[index]

    def get_display_name(self, index: int) -> str:
        """Lấy tên file (chỉ tên, không đường dẫn) để hiển thị."""
        return os.path.basename(self.get_path(index))

    def all_display_names(self) -> list:
        """Trả về danh sách tên hiển thị của tất cả file."""
        return [os.path.basename(fp) for fp in self._files]

    def count(self) -> int:
        """Số lượng file trong danh sách."""
        return len(self._files)

    def is_empty(self) -> bool:
        return len(self._files) == 0

    # ──────────────────────────────────────────
    #  NỘI BỘ
    # ──────────────────────────────────────────
    def _valid(self, index: int) -> bool:
        return 0 <= index < len(self._files)