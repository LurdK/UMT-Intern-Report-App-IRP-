import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from typing import Dict, Any, Callable
from backend.storage import save_config, DEFAULT_CONFIG
from backend.compiler import check_latex_environment, MIKTEX_URL, TEXLIVE_URL

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, base_dir: str, config: Dict[str, Any], on_save_callback: Callable[[Dict[str, Any]], None]):
        super().__init__(parent)
        self.title("Settings & Configuration")
        self.geometry("560x520")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.base_dir = base_dir
        self.config = config.copy()
        self.on_save_callback = on_save_callback

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
        w = 560
        h = 520
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def build_ui(self):
        container = tk.Frame(self, bg="#F8FAFC", padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_lbl = tk.Label(
            container,
            text="Application Settings",
            font=("Segoe UI", 14, "bold"),
            fg="#00478F",
            bg="#F8FAFC"
        )
        title_lbl.pack(anchor="w", pady=(0, 16))

        # Fields frame
        form_frame = tk.Frame(container, bg="#FFFFFF", padx=16, pady=16, highlightbackground="#E2E8F0", highlightthickness=1)
        form_frame.pack(fill=tk.X, pady=(0, 16))

        # 1. Matric Number
        tk.Label(form_frame, text="Default Matric Number:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w", pady=6)
        self.matric_entry = ttk.Entry(form_frame, width=35)
        self.matric_entry.insert(0, self.config.get("matric_no", "S70012"))
        self.matric_entry.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 2. Course Code & Title
        tk.Label(form_frame, text="Course Code / Title:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=1, column=0, sticky="w", pady=6)
        self.course_entry = ttk.Entry(form_frame, width=35)
        self.course_entry.insert(0, self.config.get("course_code", "CSF4992 / CSF49712 INDUSTRIAL TRAINING"))
        self.course_entry.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 3. Student Name (Optional)
        tk.Label(form_frame, text="Student Name (Optional):", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=2, column=0, sticky="w", pady=6)
        self.name_entry = ttk.Entry(form_frame, width=35)
        self.name_entry.insert(0, self.config.get("student_name", ""))
        self.name_entry.grid(row=2, column=1, sticky="ew", pady=6, padx=(10, 0))

        # 4. Custom pdflatex path
        # 4. Custom pdflatex path
        tk.Label(form_frame, text="Custom pdflatex Path:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").grid(row=3, column=0, sticky="w", pady=6)
        path_box = tk.Frame(form_frame, bg="#FFFFFF")
        path_box.grid(row=3, column=1, sticky="ew", pady=6, padx=(10, 0))

        self.pdflatex_entry = ttk.Entry(path_box)
        self.pdflatex_entry.insert(0, self.config.get("custom_pdflatex_path", ""))
        self.pdflatex_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(path_box, text="📁 Browse...", width=10, command=self.browse_pdflatex)
        browse_btn.pack(side=tk.LEFT, padx=(6, 2))

        test_btn = ttk.Button(path_box, text="🔍 Test", width=7, command=self.test_pdflatex_path)
        test_btn.pack(side=tk.LEFT, padx=(2, 2))

        clear_btn = ttk.Button(path_box, text="✕", width=3, command=self.clear_pdflatex_path)
        clear_btn.pack(side=tk.LEFT, padx=(2, 0))

        # 5. Clean auxiliary files checkbox
        self.clean_aux_var = tk.BooleanVar(value=self.config.get("auto_clean_aux", True))
        clean_cb = ttk.Checkbutton(form_frame, text="Automatically clean auxiliary files (.aux, .log) after compile", variable=self.clean_aux_var)
        clean_cb.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        form_frame.columnconfigure(1, weight=1)

        # LaTeX Detection Status Card
        self.status_frame = tk.Frame(container, bg="#FFFFFF", padx=14, pady=12, highlightbackground="#E2E8F0", highlightthickness=1)
        self.status_frame.pack(fill=tk.X, pady=(0, 16))

        self.lbl_status_title = tk.Label(self.status_frame, text="", font=("Segoe UI", 10, "bold"), bg="#FFFFFF")
        self.lbl_status_title.pack(anchor="w")

        self.lbl_status_desc = tk.Label(self.status_frame, text="", font=("Segoe UI", 8), fg="#64748B", bg="#FFFFFF", justify="left")
        self.lbl_status_desc.pack(anchor="w", pady=(2, 6))

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
            text="Save Settings",
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
            text="Cancel",
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
            self.lbl_status_title.configure(text="✅ LaTeX Compiler Detected & Working", fg="#16A34A")
            path_source = "Custom Path" if current_path else "Auto-detected"
            self.lbl_status_desc.configure(text=f"{diag['version']}\nSource ({path_source}): {diag['path']}")
            self.link_box.pack_forget()
        else:
            self.lbl_status_title.configure(text="⚠️ LaTeX Compiler Not Detected", fg="#DC2626")
            self.lbl_status_desc.configure(text="pdflatex was not found. Please browse for your custom pdflatex.exe or download a TeX distribution:")
            self.link_box.pack(anchor="w", pady=(4, 0))

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
                "Compiler Verified",
                f"✅ pdflatex was successfully verified!\n\nVersion: {diag['version']}\nPath: {diag['path']}",
                parent=self
            )
        else:
            messagebox.showerror(
                "Compiler Test Failed",
                f"❌ Unable to run pdflatex at this location:\n{current_path or '(empty)'}\n\nPlease check the path and make sure it points to pdflatex.exe.",
                parent=self
            )
        self.refresh_compiler_status()

    def clear_pdflatex_path(self):
        self.pdflatex_entry.delete(0, tk.END)
        self.refresh_compiler_status()


    def save(self):
        self.config["matric_no"] = self.matric_entry.get().strip() or "S70012"
        self.config["course_code"] = self.course_entry.get().strip() or "CSF4992 / CSF49712 INDUSTRIAL TRAINING"
        self.config["student_name"] = self.name_entry.get().strip()
        self.config["custom_pdflatex_path"] = self.pdflatex_entry.get().strip()
        self.config["auto_clean_aux"] = self.clean_aux_var.get()

        save_config(self.base_dir, self.config)
        self.on_save_callback(self.config)
        messagebox.showinfo("Settings Saved", "Configuration has been updated successfully!", parent=self)
        self.destroy()
