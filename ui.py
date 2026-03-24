"""
ui.py - ĐÃ FIX LAG khi load file
- load_file() async, không block UI
- Hiện "Đang tải..." trong lúc chờ
- Callback on_load_done / on_load_error
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
        self.geometry("1200x780")
        self.minsize(1000, 660)

        self.engine  = AudioEngine()
        self.manager = FileManager()

        # Callbacks
        self.engine.on_save_done     = self._on_record_saved
        self.engine.on_playback_tick = self._on_playback_tick
        self.engine.on_playback_end  = self._on_playback_end
        self.engine.on_load_done     = self._on_load_done    # ← MỚI
        self.engine.on_load_error    = self._on_load_error   # ← MỚI

        self._selected_index = None
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

        ctk.CTkLabel(sb, text="🎙️ AudioLab",
                     font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(24, 2))
        ctk.CTkLabel(sb, text="Ghi âm & Chỉnh sửa âm thanh",
                     font=ctk.CTkFont(size=11), text_color="gray").grid(
            row=1, column=0, padx=20, pady=(0, 12))
        ctk.CTkFrame(sb, height=1, fg_color="#3a3a3a").grid(
            row=2, column=0, sticky="ew", padx=16)

        self.btn_record = ctk.CTkButton(
            sb, text="⏺  Bắt đầu ghi âm", width=220,
            fg_color="#e74c3c", hover_color="#c0392b",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._toggle_record)
        self.btn_record.grid(row=3, column=0, padx=20, pady=10)

        ctk.CTkButton(sb, text="📂  Nhập file âm thanh", width=220,
                      command=self._import_files).grid(row=4, column=0, padx=20, pady=4)

        ctk.CTkLabel(sb, text="📋  Danh sách ghi âm",
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=5, column=0, padx=20, pady=(14, 4), sticky="w")

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
        self._build_bottom_row(main)

    # ── Card phát lại ─────────────────────────
    def _build_playback_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="▶  Phát lại",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=5, padx=16, pady=(12, 6), sticky="w")

        bf = ctk.CTkFrame(card, fg_color="transparent")
        bf.grid(row=1, column=0, padx=12, pady=10)
        ctk.CTkButton(bf, text="▶ Phát", width=88,
                      fg_color="#27ae60", hover_color="#1e8449",
                      command=self._play).grid(row=0, column=0, padx=4)
        ctk.CTkButton(bf, text="⏹ Dừng", width=88,
                      command=self._stop).grid(row=0, column=1, padx=4)

        sf_ = ctk.CTkFrame(card, fg_color="transparent")
        sf_.grid(row=1, column=1, sticky="ew", padx=8)
        sf_.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(sf_, text="⏩ Tua:").grid(row=0, column=0, padx=(0, 6))
        self.seek_slider = ctk.CTkSlider(sf_, from_=0, to=100, command=self._on_seek)
        self.seek_slider.set(0)
        self.seek_slider.grid(row=0, column=1, sticky="ew")
        self.lbl_time = ctk.CTkLabel(sf_, text="0:00 / 0:00", width=110)
        self.lbl_time.grid(row=0, column=2, padx=8)

        vf = ctk.CTkFrame(card, fg_color="transparent")
        vf.grid(row=1, column=2, padx=10)
        ctk.CTkLabel(vf, text="🔊").grid(row=0, column=0)
        self.vol_slider = ctk.CTkSlider(vf, from_=0, to=2, width=120,
                                         command=self._on_volume)
        self.vol_slider.set(1.0)
        self.vol_slider.grid(row=0, column=1, padx=6)
        self.lbl_vol = ctk.CTkLabel(vf, text="100%", width=46)
        self.lbl_vol.grid(row=0, column=2)

        spf = ctk.CTkFrame(card, fg_color="transparent")
        spf.grid(row=1, column=3, padx=10)
        ctk.CTkLabel(spf, text="⚡ Tốc độ:").grid(row=0, column=0, padx=(0, 6))
        self.speed_var = ctk.StringVar(value="1.0x")
        ctk.CTkOptionMenu(spf, variable=self.speed_var, width=90,
                          values=["0.5x", "1.0x", "1.5x", "2.0x"],
                          command=self._on_speed_change).grid(row=0, column=1)

    # ── Card sóng âm ──────────────────────────
    def _build_waveform_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        hf = ctk.CTkFrame(card, fg_color="transparent")
        hf.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        hf.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hf, text="〰️  Sóng âm",
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w")
        ctk.CTkButton(hf, text="🖼️ Xuất PNG", width=110,
                      fg_color="#16a085", hover_color="#0e6655",
                      command=self._export_png).grid(row=0, column=1)

        wf_frame = ctk.CTkFrame(card, fg_color="transparent")
        wf_frame.grid(row=1, column=0, sticky="nsew")
        wf_frame.grid_rowconfigure(0, weight=1)
        wf_frame.grid_columnconfigure(0, weight=1)
        self.waveform = WaveformWidget(wf_frame)

    # ── Hàng dưới ─────────────────────────────
    def _build_bottom_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew")
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(2, weight=1)

        self._build_info_card(row)
        self._build_effects_card(row)
        self._build_edit_card(row)

    def _build_info_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(card, text="ℹ️  Thông tin file",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(10, 6), sticky="w")
        labels = ["📄 Tên file:", "⏱️ Thời lượng:", "🎚️ Sample rate:",
                  "📦 Kích thước:", "🔖 Định dạng:"]
        self._info_vals = {}
        keys = ["filename", "duration", "sample_rate", "filesize", "format"]
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            ctk.CTkLabel(card, text=lbl, font=ctk.CTkFont(size=11),
                         text_color="gray").grid(
                row=i+1, column=0, padx=(14, 4), pady=2, sticky="w")
            val = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=11), anchor="w")
            val.grid(row=i+1, column=1, padx=(0, 14), pady=2, sticky="w")
            self._info_vals[key] = val
        ctk.CTkFrame(card, height=6, fg_color="transparent").grid(row=7, column=0)

    def _build_effects_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(card, text="🎛️  Hiệu ứng",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(10, 10), sticky="w")
        ctk.CTkButton(card, text="🔁 Echo", width=120,
                      fg_color="#8e44ad", hover_color="#6c3483",
                      command=lambda: self._apply_effect("echo")).grid(
            row=1, column=0, padx=14, pady=6)
        ctk.CTkButton(card, text="🌊 Reverb", width=120,
                      fg_color="#2471a3", hover_color="#1a5276",
                      command=lambda: self._apply_effect("reverb")).grid(
            row=2, column=0, padx=14, pady=6)
        ctk.CTkLabel(card, text="Lưu file mới\nbên cạnh file gốc",
                     font=ctk.CTkFont(size=10), text_color="gray").grid(
            row=3, column=0, padx=14, pady=(4, 10))

    def _build_edit_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(card, text="✂️  Cắt đoạn",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(10, 8), sticky="w")
        ctk.CTkLabel(card, text="Từ (s):").grid(row=1, column=0, padx=(14, 4), pady=4, sticky="w")
        self.entry_start = ctk.CTkEntry(card, width=100, placeholder_text="0.0")
        self.entry_start.grid(row=1, column=1, padx=(0, 14), pady=4)
        ctk.CTkLabel(card, text="Đến (s):").grid(row=2, column=0, padx=(14, 4), pady=4, sticky="w")
        self.entry_end = ctk.CTkEntry(card, width=100, placeholder_text="5.0")
        self.entry_end.grid(row=2, column=1, padx=(0, 14), pady=4)
        ctk.CTkButton(card, text="✂️ Cắt & Lưu", width=180,
                      fg_color="#d35400", hover_color="#b7460e",
                      command=self._cut_audio).grid(
            row=3, column=0, columnspan=2, padx=14, pady=(8, 6))
        self.lbl_status = ctk.CTkLabel(card, text="",
                                        font=ctk.CTkFont(size=11),
                                        text_color="#2ecc71", wraplength=180)
        self.lbl_status.grid(row=4, column=0, columnspan=2, padx=14, pady=(0, 10))

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
        # Hiện trạng thái loading ngay — không chờ
        self._set_status("⏳ Đang tải file...", "#f39c12")
        self.lbl_time.configure(text="0:00 / --:--")
        # Load async — KHÔNG block UI
        filepath = self.manager.get_path(self._selected_index)
        self.engine.load_file(filepath)

    def _on_load_done(self):
        """Callback từ audio thread khi load xong — dùng after() để về main thread."""
        self.after(0, self._update_ui_after_load)

    def _update_ui_after_load(self):
        """Cập nhật toàn bộ UI sau khi load file xong."""
        filepath = self.manager.get_path(self._selected_index)
        self.waveform.draw(self.engine.audio_data, self.engine.audio_sr)
        self.seek_slider.set(0)
        dur    = self.engine.duration
        dm, ds = divmod(int(dur), 60)
        self.lbl_time.configure(text=f"0:00 / {dm:02d}:{ds:02d}")
        self._update_info()
        self._set_status(f"✅ {os.path.basename(filepath)}", "#2ecc71")

    def _on_load_error(self, msg: str):
        """Callback khi load file lỗi."""
        self.after(0, lambda: self._set_status(f"❌ Lỗi: {msg}", "#e74c3c"))

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
        self.lbl_time.configure(text="0:00 / 0:00")
        self._clear_info()

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
            sec    = float(value) / 100.0 * self.engine.duration
            self.engine.seek(sec)
            m,  s  = divmod(int(sec), 60)
            dm, ds = divmod(int(self.engine.duration), 60)
            self.lbl_time.configure(text=f"{m:02d}:{s:02d} / {dm:02d}:{ds:02d}")

    def _on_volume(self, value):
        self.engine.set_volume(float(value))
        self.lbl_vol.configure(text=f"{int(float(value)*100)}%")

    def _on_speed_change(self, value):
        self.engine.set_speed(float(value.replace("x", "")))
        self._set_status(f"⚡ Tốc độ: {value}", "#f39c12")

    def _on_playback_tick(self, current: float, total: float):
        pct    = (current / total * 100) if total > 0 else 0
        m,  s  = divmod(int(current), 60)
        dm, ds = divmod(int(total),   60)
        self.after(0, lambda: self.seek_slider.set(pct))
        self.after(0, lambda: self.lbl_time.configure(
            text=f"{m:02d}:{s:02d} / {dm:02d}:{ds:02d}"))
        self.after(0, lambda: self.waveform.set_playhead(current))

    def _on_playback_end(self):
        dm, ds = divmod(int(self.engine.duration), 60)
        self.after(0, lambda: self.seek_slider.set(0))
        self.after(0, lambda: self.lbl_time.configure(
            text=f"0:00 / {dm:02d}:{ds:02d}"))
        self.after(0, lambda: self.waveform.set_playhead(0))

    # ══════════════════════════════════════════
    #  THÔNG TIN FILE
    # ══════════════════════════════════════════
    def _update_info(self):
        info = self.engine.get_file_info()
        for key, widget in self._info_vals.items():
            widget.configure(text=info.get(key, "—"))

    def _clear_info(self):
        for widget in self._info_vals.values():
            widget.configure(text="—")

    # ══════════════════════════════════════════
    #  HIỆU ỨNG
    # ══════════════════════════════════════════
    def _apply_effect(self, effect: str):
        if self.engine.audio_data is None:
            messagebox.showwarning("Chú ý", "Vui lòng chọn file trước!"); return
        try:
            new_path = self.engine.apply_effect(effect)
            self._add_file_to_list(new_path)
            self._set_status(f"✅ {effect}: {os.path.basename(new_path)}", "#2ecc71")
        except Exception as e:
            messagebox.showerror("Lỗi hiệu ứng", str(e))

    # ══════════════════════════════════════════
    #  XUẤT PNG
    # ══════════════════════════════════════════
    def _export_png(self):
        if self.engine.audio_data is None:
            messagebox.showwarning("Chú ý", "Vui lòng chọn file trước!"); return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="waveform.png")
        if not save_path:
            return
        try:
            self.waveform.export_png(save_path)
            self._set_status(f"🖼️ Xuất PNG: {os.path.basename(save_path)}", "#2ecc71")
        except Exception as e:
            messagebox.showerror("Lỗi xuất PNG", str(e))

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
            messagebox.showerror("Lỗi", "Nhập số hợp lệ!"); return
        try:
            orig     = self.manager.get_path(self._selected_index)
            new_path = self.engine.cut_and_save(start, end, orig)
            self._add_file_to_list(new_path)
            self._set_status(f"✅ {os.path.basename(new_path)}", "#2ecc71")
        except Exception as e:
            messagebox.showerror("Lỗi cắt âm thanh", str(e))

    # ══════════════════════════════════════════
    #  TIỆN ÍCH
    # ══════════════════════════════════════════
    def _set_status(self, text: str, color: str = "#2ecc71"):
        self.lbl_status.configure(text=text, text_color=color)