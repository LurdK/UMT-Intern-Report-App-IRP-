import tkinter as tk
from tkinter import ttk
import webbrowser

class AboutDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("About - UMT Intern Report Manager")
        self.geometry("460x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#F8FAFC")

        # Center on parent window
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        w = 460
        h = 380
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.build_ui()

    def build_ui(self):
        # Header Banner
        header = tk.Frame(self, bg="#0F172A", padx=20, pady=18)
        header.pack(fill=tk.X)

        lbl_app = tk.Label(
            header,
            text="UMT Intern Report Manager",
            font=("Segoe UI", 13, "bold"),
            fg="#F8FAFC",
            bg="#0F172A"
        )
        lbl_app.pack(anchor="w")

        lbl_sub = tk.Label(
            header,
            text="Industrial Training e-Logbook Desktop Manager",
            font=("Segoe UI", 9),
            fg="#94A3B8",
            bg="#0F172A"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Body Container
        body = tk.Frame(self, bg="#F8FAFC", padx=20, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        # Info Card
        card = tk.Frame(body, bg="#FFFFFF", padx=16, pady=14, highlightbackground="#E2E8F0", highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 14))

        # Version
        r1 = tk.Frame(card, bg="#FFFFFF")
        r1.pack(fill=tk.X, pady=3)
        tk.Label(r1, text="Version:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF", width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(r1, text="v1.0.0 (2026)", font=("Segoe UI", 9), fg="#0F172A", bg="#FFFFFF").pack(side=tk.LEFT)

        # Developer
        r2 = tk.Frame(card, bg="#FFFFFF")
        r2.pack(fill=tk.X, pady=3)
        tk.Label(r2, text="Developer:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF", width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(r2, text="LurdK", font=("Segoe UI", 9, "bold"), fg="#0284C7", bg="#FFFFFF").pack(side=tk.LEFT)

        # GitHub Profile
        r3 = tk.Frame(card, bg="#FFFFFF")
        r3.pack(fill=tk.X, pady=3)
        tk.Label(r3, text="GitHub:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF", width=14, anchor="w").pack(side=tk.LEFT)
        lbl_github = tk.Label(
            r3,
            text="github.com/LurdK",
            font=("Segoe UI", 9, "underline"),
            fg="#2563EB",
            bg="#FFFFFF",
            cursor="hand2"
        )
        lbl_github.pack(side=tk.LEFT)
        lbl_github.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/LurdK"))

        # Repository
        r4 = tk.Frame(card, bg="#FFFFFF")
        r4.pack(fill=tk.X, pady=3)
        tk.Label(r4, text="Repository:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF", width=14, anchor="w").pack(side=tk.LEFT)
        lbl_repo = tk.Label(
            r4,
            text="UMT-Intern-Report-App-IRP-",
            font=("Segoe UI", 9, "underline"),
            fg="#2563EB",
            bg="#FFFFFF",
            cursor="hand2"
        )
        lbl_repo.pack(side=tk.LEFT)
        lbl_repo.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/LurdK/UMT-Intern-Report-App-IRP-"))

        # License
        r5 = tk.Frame(card, bg="#FFFFFF")
        r5.pack(fill=tk.X, pady=3)
        tk.Label(r5, text="License:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#FFFFFF", width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(r5, text="MIT Open Source License", font=("Segoe UI", 9), fg="#64748B", bg="#FFFFFF").pack(side=tk.LEFT)

        # Footer Button
        btn_close = tk.Button(
            body,
            text="Close",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#0284C7",
            activebackground="#0369A1",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        btn_close.pack(side=tk.RIGHT)
