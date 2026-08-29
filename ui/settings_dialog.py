import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from typing import Dict, Any, Callable
from backend.storage import save_config, DEFAULT_CONFIG
from backend.compiler import check_latex_environment, MIKTEX_URL, TEXLIVE_URL
from backend.i18n import t, set_language, get_language

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, base_dir: str, config: Dict[str, Any], on_save_callback: Callable[[Dict[str, Any]], None]):
        super().__init__(parent)
        self.base_dir = base_dir
        self.config = config.copy()
        self.on_save_callback = on_save_callback

        self.title(t("settings_title"))
        self.geometry("580x570")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Window styling
        self.configure(bg="#F8FAFC")

        # Center on parent
        self.center_window(parent)

        self.build_ui()

    def center_window(self, parent: tk.Tk):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = 580
        h = 570
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        container = tk.Frame(self, bg="#F8FAFC", padx=24, pady=18)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_lbl = tk.Label(
            container,
            text=t("settings_header"),
            font=("Segoe UI", 14, "bold"),
            fg="#00478F",
            bg="#F8FAFC"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            container,
            text=t("settings_sub"),
            font=("Segoe UI", 8),
            fg="#64748B",
            bg="#F8FAFC"
        )
        sub_lbl.pack(anchor="w", pady=(2, 12))

        # Fields frame
        form_frame = tk.Frame(container, bg="#FFFFFF", padx=16, pady=14, highlightbackground="#E2E8F0", highlightthickness=1)
        form_frame.pack(fill=tk.X, pady=(0, 14))

        # 0. Language Selector
        tk.Label(form_frame, text=t("settings_language"), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w", pady=5)
        self.lang_combo = ttk.Combobox(form_frame, values=["English (EN)", "Bahasa Melayu (BM)"], state="readonly", width=33)
        current_lang = self.config.get("language", "en")
        self.lang_combo.set("Bahasa Melayu (BM)" if current_lang == "ms" else "English (EN)")
        self.lang_combo.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 1. Matric Number
        tk.Label(form_frame, text=t("settings_default_matric"), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=1, column=0, sticky="w", pady=5)
        self.matric_entry = ttk.Entry(form_frame, width=35)
        self.matric_entry.insert(0, self.config.get("matric_no", "S70012"))
        self.matric_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 2. Course Code & Title
        tk.Label(form_frame, text=t("settings_course_code"), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=2, column=0, sticky="w", pady=5)
        self.course_entry = ttk.Entry(form_frame, width=35)
        self.course_entry.insert(0, self.config.get("course_code", "CSF4992 / CSF49712 INDUSTRIAL TRAINING"))
        self.course_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 3. Student Name (Optional)
        tk.Label(form_frame, text=t("settings_student_name"), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=3, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, width=35)
        self.name_entry.insert(0, self.config.get("student_name", ""))
        self.name_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))

        # 4. Custom Reports Output Directory
        tk.Label(form_frame, text=t("settings_reports_dir"), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=4, column=0, sticky="w", pady=5)
        rep_box = tk.Frame(form_frame, bg="#FFFFFF")
        rep_box.grid(row=4, column=1, sticky="ew", pady=5, padx=(10, 0))

        self.reports_dir_entry = ttk.Entry(rep_box)
        default_rep_display = self.config.get("custom_reports_dir", "")
        self.reports_dir_entry.insert(0, default_rep_display)
        self.reports_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_rep_btn = ttk.Button(rep_box, text=t("settings_browse"), width=10, command=self.browse_reports_dir)
        browse_rep_btn.pack(side=tk.LEFT, padx=(6, 2))

        open_rep_btn = ttk.Button(rep_box, text=t("settings_open"), width=7, command=self.open_reports_dir)
        open_rep_btn.pack(side=tk.LEFT, padx=(2, 2))

        clear_rep_btn = ttk.Button(rep_box, text=t("settings_reset"), width=3, command=self.clear_reports_dir)
        clear_rep_btn.pack(side=tk.LEFT, padx=(2, 0))

        # 5. Custom pdflatex path
        tk.Label(form_frame, text=t("settings_compiler_path"), font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=5, column=0, sticky="w", pady=5)
        path_box = tk.Frame(form_frame, bg="#FFFFFF")
        path_box.grid(row=5, column=1, sticky="ew", pady=5, padx=(10, 0))

        self.pdflatex_entry = ttk.Entry(path_box)
        self.pdflatex_entry.insert(0, self.config.get("custom_pdflatex_path", ""))
        self.pdflatex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(path_box, text=t("settings_browse"), width=10, command=self.browse_pdflatex)
        browse_btn.pack(side=tk.LEFT, padx=(6, 2))

        test_btn = ttk.Button(path_box, text=t("settings_test"), width=7, command=self.test_pdflatex_path)
        test_btn.pack(side=tk.LEFT, padx=(2, 2))

        clear_btn = ttk.Button(path_box, text=t("settings_reset"), width=3, command=self.clear_pdflatex_path)
        clear_btn.pack(side=tk.LEFT, padx=(2, 0))

        # 6. Clean auxiliary files checkbox
        self.clean_aux_var = tk.BooleanVar(value=self.config.get("auto_clean_aux", True))
        clean_cb = ttk.Checkbutton(form_frame, text=t("settings_clean_aux"), variable=self.clean_aux_var)
        clean_cb.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))

        form_frame.columnconfigure(1, weight=1)

        # LaTeX Detection Status Card
        self.status_frame = tk.Frame(container, bg="#FFFFFF", padx=14, pady=10, highlightbackground="#E2E8F0", highlightthickness=1)
        self.status_frame.pack(fill=tk.X, pady=(0, 14))

        self.lbl_status_title = tk.Label(self.status_frame, text="", font=("Segoe UI", 9, "bold"), bg="#FFFFFF")
        self.lbl_status_title.pack(anchor="w")

        self.lbl_status_desc = tk.Label(self.status_frame, text="", font=("Segoe UI", 8), fg="#64748B", bg="#FFFFFF", justify="left")
        self.lbl_status_desc.pack(anchor="w", pady=(2, 4))

        self.link_box = tk.Frame(self.status_frame, bg="#FFFFFF")
        self.link_box.pack(anchor="w", pady=(4, 0))

        btn_miktex = tk.Button(
            self.link_box,
            text="📥 Download MiKTeX",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg="#0284C7",
            activebackground="#0369A1",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: webbrowser.open(MIKTEX_URL)
        )
        btn_miktex.pack(side=tk.LEFT, padx=(0, 8))

        btn_texlive = tk.Button(
            self.link_box,
            text="📥 Download TeX Live",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg="#0284C7",
            activebackground="#0369A1",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: webbrowser.open(TEXLIVE_URL)
        )
        btn_texlive.pack(side=tk.LEFT)

        # Initial live status update
        self.refresh_compiler_status()

        # Bind live typing
        self.pdflatex_entry.bind("<KeyRelease>", lambda e: self.refresh_compiler_status())

        # Buttons (Save / Cancel)
        btn_bar = tk.Frame(container, bg="#F8FAFC")
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)

        save_btn = tk.Button(
            btn_bar,
            text=t("settings_btn_save"),
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#00478F",
            activebackground="#003366",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.save
        )
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))

        cancel_btn = tk.Button(
            btn_bar,
            text=t("settings_btn_cancel"),
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#E2E8F0",
            activebackground="#CBD5E1",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        cancel_btn.pack(side=tk.RIGHT)

    def refresh_compiler_status(self):
        current_path = self.pdflatex_entry.get().strip() if hasattr(self, "pdflatex_entry") else self.config.get("custom_pdflatex_path", "")
        diag = check_latex_environment(current_path)

        if diag["available"]:
            self.lbl_status_title.configure(text=t("compiler_detected"), fg="#16A34A")
            path_source = "Custom Path" if current_path else "Auto-detected"
            self.lbl_status_desc.configure(text=f"{diag['version']}\nSource ({path_source}): {diag['path']}")
            self.link_box.pack_forget()
        else:
            self.lbl_status_title.configure(text=t("compiler_not_detected"), fg="#DC2626")
            self.lbl_status_desc.configure(text=t("compiler_not_detected_desc"))
            self.link_box.pack(anchor="w", pady=(4, 0))

    def browse_reports_dir(self):
        folder = filedialog.askdirectory(
            title=t("settings_reports_dir"),
            initialdir=self.reports_dir_entry.get().strip() or self.base_dir,
            parent=self
        )
        if folder:
            self.reports_dir_entry.delete(0, tk.END)
            self.reports_dir_entry.insert(0, folder)

    def open_reports_dir(self):
        target = self.reports_dir_entry.get().strip() or os.path.join(self.base_dir, "Report")
        if not os.path.exists(target):
            try:
                os.makedirs(target, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder:\n{e}", parent=self)
                return
        import subprocess
        if sys.platform == "win32":
            subprocess.Popen(f'explorer "{os.path.abspath(target)}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", os.path.abspath(target)])
        else:
            subprocess.Popen(["xdg-open", os.path.abspath(target)])

    def clear_reports_dir(self):
        self.reports_dir_entry.delete(0, tk.END)

    def browse_pdflatex(self):
        filename = filedialog.askopenfilename(
            title="Select pdflatex Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")],
            parent=self
        )
        if filename:
            self.pdflatex_entry.delete(0, tk.END)
            self.pdflatex_entry.insert(0, filename)
            self.refresh_compiler_status()

    def test_pdflatex_path(self):
        current_path = self.pdflatex_entry.get().strip()
        diag = check_latex_environment(current_path)
        if diag["available"]:
            messagebox.showinfo(
                t("compiler_verified_title"),
                t("compiler_verified_msg", version=diag['version'], path=diag['path']),
                parent=self
            )
        else:
            messagebox.showerror(
                t("compiler_failed_title"),
                t("compiler_failed_msg", path=current_path or '(empty)'),
                parent=self
            )
        self.refresh_compiler_status()

    def clear_pdflatex_path(self):
        self.pdflatex_entry.delete(0, tk.END)
        self.refresh_compiler_status()

    def save(self):
        old_custom = self.config.get("custom_reports_dir", "").strip()
        new_custom = self.reports_dir_entry.get().strip()

        old_dir = os.path.abspath(old_custom) if old_custom else os.path.abspath(os.path.join(self.base_dir, "Report"))
        new_dir = os.path.abspath(new_custom) if new_custom else os.path.abspath(os.path.join(self.base_dir, "Report"))

        transfer_msg = ""
        if os.path.normpath(old_dir).lower() != os.path.normpath(new_dir).lower() and os.path.exists(old_dir):
            existing_items = [e for e in os.listdir(old_dir) if not e.startswith(".") and e not in ("build", "dist", ".git", ".agents", "__pycache__", "Intern Report App")]
            if existing_items:
                ans = messagebox.askyesno(
                    t("transfer_title"),
                    t("transfer_prompt", old_dir=old_dir, new_dir=new_dir, count=len(existing_items)),
                    parent=self
                )
                if ans:
                    from backend.folder_manager import FolderManager
                    f_count, fl_count = FolderManager.transfer_reports(old_dir, new_dir)
                    transfer_msg = t("transfer_success", folders=f_count, files=fl_count)

        # Set selected language
        chosen_lang = "ms" if "Bahasa Melayu" in self.lang_combo.get() else "en"
        self.config["language"] = chosen_lang
        set_language(chosen_lang)

        self.config["matric_no"] = self.matric_entry.get().strip() or "S70012"
        self.config["course_code"] = self.course_entry.get().strip() or "CSF4992 / CSF49712 INDUSTRIAL TRAINING"
        self.config["student_name"] = self.name_entry.get().strip()
        self.config["custom_reports_dir"] = self.reports_dir_entry.get().strip()
        self.config["custom_pdflatex_path"] = self.pdflatex_entry.get().strip()
        self.config["auto_clean_aux"] = self.clean_aux_var.get()

        save_config(self.base_dir, self.config)
        try:
            self.on_save_callback(self.config)
        except Exception as e:
            print(f"Error updating main window on save: {e}")

        parent_win = self.master
        self.destroy()
        messagebox.showinfo(
            t("settings_title"),
            t("settings_saved_msg", transfer_msg=transfer_msg),
            parent=parent_win
        )
