"""
ui.py
────────────────────────────────────────────
Giao diện chính của AudioLab (CustomTkinter).
Kết nối AudioEngine + FileManager + WaveformWidget.

Lớp:   AudioLabApp(ctk.CTk)
Dùng:  from ui import AudioLabApp
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import customtkinter as ctk

from audio        import AudioEngine
from file_manager import FileManager
from waveform     import WaveformWidget

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AudioLabApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎙️ AudioLab – Ghi âm & Chỉnh sửa")
        self.geometry("1150x720")
        self.minsize(960, 640)

        # Khởi tạo các module
        self.engine  = AudioEngine()
        self.manager = FileManager()

        # Đăng ký callback từ AudioEngine
        self.engine.on_save_done     = self._on_record_saved
        self.engine.on_playback_tick = self._on_playback_tick
        self.engine.on_playback_end  = self._on_playback_end

        self._selected_index = None   # index file đang chọn trong danh sách

        self._build_ui()

    # ══════════════════════════════════════════
    #  XÂY DỰNG GIAO DIỆN
    # ══════════════════════════════════════════
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

    # ── Sidebar ───────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=260, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_rowconfigure(6, weight=1)

        # Tiêu đề
        ctk.CTkLabel(sb, text="🎙️ AudioLab",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(24, 2))
        ctk.CTkLabel(sb, text="Ghi âm & Chỉnh sửa âm thanh",
                     font=ctk.CTkFont(size=11), text_color="gray").grid(
            row=1, column=0, padx=20, pady=(0, 12))
        ctk.CTkFrame(sb, height=1, fg_color="#3a3a3a").grid(
            row=2, column=0, sticky="ew", padx=16)

        # Nút ghi âm
        self.btn_record = ctk.CTkButton(
            sb, text="⏺  Bắt đầu ghi âm", width=220,
            fg_color="#e74c3c", hover_color="#c0392b",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._toggle_record)
        self.btn_record.grid(row=3, column=0, padx=20, pady=10)

        # Nút nhập file
        ctk.CTkButton(
            sb, text="📂  Nhập file âm thanh", width=220,
            command=self._import_files).grid(row=4, column=0, padx=20, pady=4)

        # Label danh sách
        ctk.CTkLabel(sb, text="📋  Danh sách ghi âm",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=5, column=0, padx=20, pady=(14, 4), sticky="w")

        # Listbox + scrollbar
        lf = ctk.CTkFrame(sb, fg_color="transparent")
        lf.grid(row=6, column=0, sticky="nsew", padx=12)
        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            lf, bg="#2b2b2b", fg="white", selectbackground="#1f6aa5",
            activestyle="none", borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 11), relief="flat")
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self._on_list_select)

        scr = ctk.CTkScrollbar(lf, command=self.listbox.yview)
        scr.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scr.set)

        # Nút đổi tên / xóa
        mf = ctk.CTkFrame(sb, fg_color="transparent")
        mf.grid(row=7, column=0, padx=12, pady=10)
        ctk.CTkButton(mf, text="✏️ Đổi tên", width=104,
                      command=self._rename_file).grid(row=0, column=0, padx=4)
        ctk.CTkButton(mf, text="🗑️ Xóa", width=104,
                      fg_color="#c0392b", hover_color="#a93226",
                      command=self._delete_file).grid(row=0, column=1, padx=4)

    # ── Panel chính ───────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self._build_playback_card(main)
        self._build_waveform_card(main)
        self._build_edit_card(main)

    # ── Card phát lại ─────────────────────────
    def _build_playback_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="▶  Phát lại",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=4, padx=16, pady=(12, 6), sticky="w")

        # Nút Play / Stop
        bf = ctk.CTkFrame(card, fg_color="transparent")
        bf.grid(row=1, column=0, padx=12, pady=10)
        self.btn_play = ctk.CTkButton(
            bf, text="▶ Phát", width=90,
            fg_color="#27ae60", hover_color="#1e8449",
            command=self._play)
        self.btn_play.grid(row=0, column=0, padx=4)
        ctk.CTkButton(bf, text="⏹ Dừng", width=90,
                      command=self._stop).grid(row=0, column=1, padx=4)

        # Thanh tua
        sf_ = ctk.CTkFrame(card, fg_color="transparent")
        sf_.grid(row=1, column=1, sticky="ew", padx=8)
        sf_.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sf_, text="⏩ Tua:").grid(row=0, column=0, padx=(0, 6))
        self.seek_slider = ctk.CTkSlider(sf_, from_=0, to=100,
                                          command=self._on_seek)
        self.seek_slider.set(0)
        self.seek_slider.grid(row=0, column=1, sticky="ew")
        self.lbl_time = ctk.CTkLabel(sf_, text="0.0s / 0.0s", width=110)
        self.lbl_time.grid(row=0, column=2, padx=8)

        # Âm lượng
        vf = ctk.CTkFrame(card, fg_color="transparent")
        vf.grid(row=1, column=2, padx=16, pady=10)
        ctk.CTkLabel(vf, text="🔊").grid(row=0, column=0)
        self.vol_slider = ctk.CTkSlider(vf, from_=0, to=2, width=130,
                                         command=self._on_volume)
        self.vol_slider.set(1.0)
        self.vol_slider.grid(row=0, column=1, padx=6)
        self.lbl_vol = ctk.CTkLabel(vf, text="100%", width=46)
        self.lbl_vol.grid(row=0, column=2)

    # ── Card sóng âm ──────────────────────────
    def _build_waveform_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="〰️  Sơ đồ sóng âm",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        self.waveform = WaveformWidget(card)

    # ── Card cắt đoạn ─────────────────────────
    def _build_edit_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=2, column=0, sticky="ew")

        ctk.CTkLabel(card, text="✂️  Cắt đoạn âm thanh",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=6, padx=16, pady=(12, 6), sticky="w")

        ctk.CTkLabel(card, text="Từ (s):").grid(row=1, column=0, padx=(16, 4), pady=10)
        self.entry_start = ctk.CTkEntry(card, width=80, placeholder_text="0.0")
        self.entry_start.grid(row=1, column=1, padx=4)

        ctk.CTkLabel(card, text="Đến (s):").grid(row=1, column=2, padx=4)
        self.entry_end = ctk.CTkEntry(card, width=80, placeholder_text="5.0")
        self.entry_end.grid(row=1, column=3, padx=4)

        ctk.CTkButton(card, text="✂️ Cắt & Lưu", width=130,
                      fg_color="#8e44ad", hover_color="#6c3483",
                      command=self._cut_audio).grid(row=1, column=4, padx=16)

        self.lbl_status = ctk.CTkLabel(card, text="",
                                        font=ctk.CTkFont(size=12),
                                        text_color="#2ecc71")
        self.lbl_status.grid(row=1, column=5, padx=8)

    # ══════════════════════════════════════════
    #  GHI ÂM
    # ══════════════════════════════════════════
    def _toggle_record(self):
        if not self.engine.is_recording:
            self.engine.start_recording()
            self.btn_record.configure(text="⏹  Dừng ghi âm",
                                       fg_color="#e67e22", hover_color="#ca6f1e")
            self._set_status("🔴 Đang ghi âm...", "#e74c3c")
        else:
            self.engine.stop_recording()
            self.btn_record.configure(text="⏺  Bắt đầu ghi âm",
                                       fg_color="#e74c3c", hover_color="#c0392b")

    def _on_record_saved(self, filepath: str):
        """Callback khi file ghi âm lưu xong."""
        self.after(0, lambda: self._add_file_to_list(filepath))
        self.after(0, lambda: self._set_status(
            f"✅ Đã lưu: {os.path.basename(filepath)}", "#2ecc71"))

    # ══════════════════════════════════════════
    #  QUẢN LÝ FILE
    # ══════════════════════════════════════════
    def _import_files(self):
        paths = filedialog.askopenfilenames(
            title="Chọn file âm thanh",
            filetypes=[("Audio files", "*.wav *.mp3 *.ogg *.flac"), ("All", "*.*")])
        for p in paths:
            self._add_file_to_list(p)

    def _add_file_to_list(self, filepath: str):
        self.manager.add(filepath)
        self.listbox.insert(tk.END, "  " + os.path.basename(filepath))

    def _on_list_select(self, _event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self._selected_index = sel[0]
        filepath = self.manager.get_path(self._selected_index)
        try:
            self.engine.load_file(filepath)
            self.waveform.draw(self.engine.audio_data, self.engine.audio_sr)
            self.seek_slider.set(0)
            self.lbl_time.configure(
                text=f"0.0s / {self.engine.duration:.1f}s")
            self._set_status(f"📂 {os.path.basename(filepath)}", "#3498db")
        except Exception as e:
            messagebox.showerror("Lỗi tải file", str(e))

    def _rename_file(self):
        if self._selected_index is None:
            messagebox.showwarning("Chú ý", "Vui lòng chọn file trước!"); return
        old = os.path.splitext(self.manager.get_display_name(self._selected_index))[0]
        new = simpledialog.askstring("Đổi tên", "Tên mới:", initialvalue=old)
        if not new:
            return
        try:
            self.manager.rename(self._selected_index, new)
            self.listbox.delete(self._selected_index)
            self.listbox.insert(self._selected_index,
                                "  " + self.manager.get_display_name(self._selected_index))
            self.listbox.selection_set(self._selected_index)
            self._set_status("✅ Đổi tên thành công", "#2ecc71")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def _delete_file(self):
        if self._selected_index is None:
            messagebox.showwarning("Chú ý", "Vui lòng chọn file trước!"); return
        name = self.manager.get_display_name(self._selected_index)
        if not messagebox.askyesno("Xác nhận", f"Xóa '{name}' khỏi danh sách?"):
            return
        self.manager.remove(self._selected_index)
        self.listbox.delete(self._selected_index)
        self._selected_index = None
        self.engine.audio_data = None
        self.waveform.reset()
        self.lbl_time.configure(text="0.0s / 0.0s")

    # ══════════════════════════════════════════
    #  PHÁT LẠI
    # ══════════════════════════════════════════
    def _play(self):
        if self.engine.audio_data is None:
            messagebox.showwarning("Chú ý", "Chưa chọn file!"); return
        self.engine.play()

    def _stop(self):
        self.engine.stop()

    def _on_seek(self, value):
        if self.engine.duration > 0:
            sec = float(value) / 100.0 * self.engine.duration
            self.engine.seek(sec)
            self.lbl_time.configure(
                text=f"{sec:.1f}s / {self.engine.duration:.1f}s")

    def _on_volume(self, value):
        self.engine.set_volume(float(value))
        self.lbl_vol.configure(text=f"{int(float(value) * 100)}%")

    def _on_playback_tick(self, current: float, total: float):
        pct = (current / total * 100) if total > 0 else 0
        self.after(0, lambda: self.seek_slider.set(pct))
        self.after(0, lambda: self.lbl_time.configure(
            text=f"{current:.1f}s / {total:.1f}s"))
        self.after(0, lambda: self.waveform.set_playhead(current))

    def _on_playback_end(self):
        self.after(0, lambda: self.seek_slider.set(0))
        self.after(0, lambda: self.lbl_time.configure(
            text=f"0.0s / {self.engine.duration:.1f}s"))
        self.after(0, lambda: self.waveform.set_playhead(0))

    # ══════════════════════════════════════════
    #  CẮT ĐOẠN
    # ══════════════════════════════════════════
    def _cut_audio(self):
        if self._selected_index is None or self.engine.audio_data is None:
            messagebox.showwarning("Chú ý", "Vui lòng chọn file trước!"); return
        try:
            start = float(self.entry_start.get() or 0)
            end   = float(self.entry_end.get()   or 0)
        except ValueError:
            messagebox.showerror("Lỗi", "Nhập số hợp lệ vào ô Từ / Đến!"); return
        try:
            orig     = self.manager.get_path(self._selected_index)
            new_path = self.engine.cut_and_save(start, end, orig)
            self._add_file_to_list(new_path)
            self._set_status(
                f"✅ Đã lưu: {os.path.basename(new_path)}", "#2ecc71")
        except Exception as e:
            messagebox.showerror("Lỗi cắt âm thanh", str(e))

    # ══════════════════════════════════════════
    #  TIỆN ÍCH
    # ══════════════════════════════════════════
    def _set_status(self, text: str, color: str = "#2ecc71"):
        self.lbl_status.configure(text=text, text_color=color)