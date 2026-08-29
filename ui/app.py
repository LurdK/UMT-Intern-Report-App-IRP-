import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import webbrowser
from typing import Dict, Any, List, Optional

from backend.storage import (
    load_config,
    save_config,
    load_week_data,
    save_week_data,
    get_default_week_data,
    normalize_attendance_data,
    get_default_attendance
)
from backend.folder_manager import FolderManager
from backend.latex_engine import generate_latex_content, save_latex_file
from backend.compiler import (
    compile_pdf,
    check_latex_environment,
    clean_auxiliary_files,
    MIKTEX_URL,
    TEXLIVE_URL
)
from ui.settings_dialog import SettingsDialog
from ui.date_picker import open_date_picker


# Color Palette (UMT Brand Colors & Modern Slate)
COLOR_PRIMARY = "#00478F"        # UMT Blue
COLOR_PRIMARY_HOVER = "#003366"
COLOR_ACCENT = "#0284C7"         # Light Blue
COLOR_SUCCESS = "#16A34A"        # Green
COLOR_WARNING = "#D97706"        # Amber
COLOR_DANGER = "#DC2626"         # Red
COLOR_BG = "#F1F5F9"             # Soft Slate Background
COLOR_SURFACE = "#FFFFFF"        # Card White
COLOR_BORDER = "#CBD5E1"         # Slate Border
COLOR_TEXT_MAIN = "#0F172A"      # Slate 900
COLOR_TEXT_MUTED = "#64748B"     # Slate 500
COLOR_SIDEBAR_BG = "#0F172A"     # Dark Slate Sidebar
COLOR_SIDEBAR_HOVER = "#1E293B"

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=COLOR_BG)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg=COLOR_BG)

        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_content_configure(self, event):
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=(0, 0, max(bbox[2], self.canvas.winfo_width()), max(bbox[3], self.canvas.winfo_height())))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)
        if self.scrollable_content.winfo_reqheight() <= event.height:
            self.canvas.yview_moveto(0.0)



class CreateWeekDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, default_name: str, default_num: int):
        super().__init__(parent)
        self.title("Create New Week Log")
        self.geometry("440x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg="#F8FAFC")

        self.result_name = None
        self.result_num = None

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 440) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 220) // 2
        self.geometry(f"+{x}+{y}")

        container = tk.Frame(self, bg="#F8FAFC", padx=20, pady=18)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="➕ Create New Report Folder",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_PRIMARY,
            bg="#F8FAFC"
        ).pack(anchor="w", pady=(0, 10))

        form = tk.Frame(container, bg="#FFFFFF", padx=12, pady=10, highlightbackground="#E2E8F0", highlightthickness=1)
        form.pack(fill=tk.X, pady=(0, 14))

        tk.Label(form, text="Folder Name:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_name = ttk.Entry(form, width=28)
        self.entry_name.insert(0, default_name)
        self.entry_name.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))

        tk.Label(form, text="Week Number:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_num = ttk.Entry(form, width=28)
        self.entry_num.insert(0, str(default_num))
        self.entry_num.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))

        form.columnconfigure(1, weight=1)

        btn_row = tk.Frame(container, bg="#F8FAFC")
        btn_row.pack(fill=tk.X)

        btn_create = tk.Button(
            btn_row,
            text="Create Week",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.confirm
        )
        btn_create.pack(side=tk.RIGHT, padx=(6, 0))

        btn_cancel = tk.Button(
            btn_row,
            text="Cancel",
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#E2E8F0",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side=tk.RIGHT)

        self.entry_name.focus_set()
        self.entry_name.select_range(0, tk.END)

    def confirm(self):
        name = self.entry_name.get().strip()
        num_str = self.entry_num.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Please provide a folder name.", parent=self)
            return
        try:
            num = int(num_str) if num_str else 1
        except ValueError:
            num = 1

        self.result_name = name
        self.result_num = num
        self.destroy()


class InternReportApp(tk.Tk):
    def __init__(self, workspace_dir: str):
        super().__init__()
        self.title("UMT Intern Report Manager (IRP)")
        self.geometry("1060x760")
        self.minsize(820, 580)

        self.workspace_dir = os.path.abspath(workspace_dir)
        self.config = load_config(self.workspace_dir)
        self.folder_manager = FolderManager(self.workspace_dir, custom_reports_dir=self.config.get("custom_reports_dir", ""))

        self.current_week_info: Optional[Dict[str, Any]] = None
        self.current_data: Dict[str, Any] = {}
        self.sidebar_items: List[Dict[str, Any]] = []


        # Configure styles
        self.setup_styles()

        # Build UI layout
        self.build_ui()

        # Load initial week
        self.refresh_week_list()

        # Global hotkey
        self.bind_all("<Control-s>", lambda e: self.save_current_data(show_toast=True))

        # Global mousewheel scrolling across all components
        self.bind_all("<MouseWheel>", self._on_global_mousewheel, add="+")
        self.bind_all("<Button-4>", lambda e: self._on_global_mousewheel(e, delta=120), add="+")
        self.bind_all("<Button-5>", lambda e: self._on_global_mousewheel(e, delta=-120), add="+")


    def setup_styles(self):
        self.configure(bg=COLOR_BG)
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MAIN, font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground="#FFFFFF", padding=3)
        style.configure("TCombobox", fieldbackground="#FFFFFF", padding=2)
        style.configure("TCheckbutton", background=COLOR_SURFACE, font=("Segoe UI", 9))
        style.configure("Card.TFrame", background=COLOR_SURFACE)

    def build_ui(self):
        # 1. Status bar packed first at bottom
        self.build_status_bar()

        # 2. Sidebar packed to the LEFT
        self.sidebar_frame = tk.Frame(self, bg=COLOR_SIDEBAR_BG, width=220)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)
        self.build_sidebar()

        # 3. Main workspace packed to the LEFT, filling remaining width
        self.main_content_frame = tk.Frame(self, bg=COLOR_BG)
        self.main_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.build_main_workspace()

    def build_status_bar(self):
        self.status_bar = tk.Frame(self, bg="#E2E8F0", height=24, padx=12)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = tk.Label(
            self.status_bar,
            text="Ready",
            font=("Segoe UI", 8),
            fg="#475569",
            bg="#E2E8F0"
        )
        self.lbl_status.pack(side=tk.LEFT)

        self.lbl_compiler_badge = tk.Label(
            self.status_bar,
            text="Checking LaTeX...",
            font=("Segoe UI", 8, "bold"),
            fg="#64748B",
            bg="#E2E8F0"
        )
        self.lbl_compiler_badge.pack(side=tk.RIGHT)

        self._status_timer = None
        self.update_compiler_badge()

    def set_status(self, text: str, is_error: bool = False, timeout_ms: int = 4000):
        if hasattr(self, "lbl_status"):
            color = COLOR_DANGER if is_error else "#0284C7"
            self.lbl_status.configure(text=text, fg=color)
            if hasattr(self, "_status_timer") and self._status_timer:
                try:
                    self.after_cancel(self._status_timer)
                except Exception:
                    pass
            if timeout_ms > 0 and not is_error:
                self._status_timer = self.after(timeout_ms, lambda: self.lbl_status.configure(text="Ready", fg="#475569"))


    def build_sidebar(self):
        # Header / Branding
        brand_frame = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_BG, padx=14, pady=16)
        brand_frame.pack(fill=tk.X)

        lbl_app_name = tk.Label(
            brand_frame,
            text="UMT e-Logbook",
            font=("Segoe UI", 14, "bold"),
            fg="#38BDF8",
            bg=COLOR_SIDEBAR_BG
        )
        lbl_app_name.pack(anchor="w")

        lbl_subtitle = tk.Label(
            brand_frame,
            text="Industrial Training Manager",
            font=("Segoe UI", 8),
            fg="#94A3B8",
            bg=COLOR_SIDEBAR_BG
        )
        lbl_subtitle.pack(anchor="w")

        # Action: New Week Button
        btn_new_week = tk.Button(
            self.sidebar_frame,
            text="➕  Create New Week",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=8,
            pady=7,
            cursor="hand2",
            command=self.create_new_week_action
        )
        btn_new_week.pack(fill=tk.X, padx=12, pady=(2, 10))

        # Weeks List Section Title
        self.lbl_reports_header = tk.Label(
            self.sidebar_frame,
            text=self.get_reports_header_text(),
            font=("Segoe UI", 8, "bold"),
            fg="#64748B",
            bg=COLOR_SIDEBAR_BG
        )
        self.lbl_reports_header.pack(anchor="w", padx=14, pady=(2, 4))


        # Scrollable Week List
        week_list_container = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_BG)
        week_list_container.pack(fill=tk.BOTH, expand=True, padx=6)

        self.week_canvas = tk.Canvas(week_list_container, bg=COLOR_SIDEBAR_BG, highlightthickness=0, borderwidth=0)
        self.week_scroll = ttk.Scrollbar(week_list_container, orient="vertical", command=self.week_canvas.yview)
        self.week_buttons_frame = tk.Frame(self.week_canvas, bg=COLOR_SIDEBAR_BG)

        def _on_sidebar_content_config(e):
            bbox = self.week_canvas.bbox("all")
            if bbox:
                self.week_canvas.configure(
                    scrollregion=(0, 0, max(bbox[2], self.week_canvas.winfo_width()), max(bbox[3], self.week_canvas.winfo_height()))
                )
            if self.week_buttons_frame.winfo_reqheight() <= self.week_canvas.winfo_height():
                self.week_canvas.yview_moveto(0.0)

        self.week_buttons_frame.bind("<Configure>", _on_sidebar_content_config)
        self.week_canvas_win = self.week_canvas.create_window((0, 0), window=self.week_buttons_frame, anchor="nw")
        self.week_canvas.configure(yscrollcommand=self.week_scroll.set)

        self.week_canvas.bind('<Configure>', lambda e: self.week_canvas.itemconfig(self.week_canvas_win, width=e.width))

        self.week_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.week_scroll.pack(side=tk.RIGHT, fill=tk.Y)


        # Bottom Tools Frame
        bottom_tools = tk.Frame(self.sidebar_frame, bg="#0B1120", padx=10, pady=10)
        bottom_tools.pack(fill=tk.X, side=tk.BOTTOM)

        btn_settings = tk.Button(
            bottom_tools,
            text="⚙️ Settings",
            font=("Segoe UI", 8),
            fg="#CBD5E1",
            bg="#1E293B",
            activebackground="#334155",
            relief=tk.FLAT,
            padx=6,
            pady=4,
            cursor="hand2",
            command=self.open_settings_dialog
        )
        btn_settings.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        btn_refresh = tk.Button(
            bottom_tools,
            text="🔄 Refresh",
            font=("Segoe UI", 8),
            fg="#CBD5E1",
            bg="#1E293B",
            activebackground="#334155",
            relief=tk.FLAT,
            padx=6,
            pady=4,
            cursor="hand2",
            command=self.refresh_week_list
        )
        btn_refresh.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

    def build_main_workspace(self):
        self.scroll_area = ScrollableFrame(self.main_content_frame)
        self.scroll_area.pack(fill=tk.BOTH, expand=True)
        self.content = self.scroll_area.scrollable_content

        # Empty State Placeholder
        self.empty_state_frame = tk.Frame(self.content, bg=COLOR_BG, pady=80)
        tk.Label(
            self.empty_state_frame,
            text="No Report Selected",
            font=("Segoe UI", 16, "bold"),
            fg="#64748B",
            bg=COLOR_BG
        ).pack(pady=(0, 8))
        tk.Label(
            self.empty_state_frame,
            text="Select an existing report folder or click 'Create New Week' to begin.",
            font=("Segoe UI", 10),
            fg="#94A3B8",
            bg=COLOR_BG
        ).pack(pady=(0, 16))

        # Active Editor Container
        self.editor_frame = tk.Frame(self.content, bg=COLOR_BG, padx=14, pady=12)

        # 1. Action Toolbar Card
        self.build_toolbar_card()

        # 2. Metadata Card
        self.build_metadata_card()

        # 3. Attendance Card
        self.build_attendance_card()

        # 4. Weekly Activities Card
        self.build_activities_card()

        # 5. Skills Gained Card
        self.build_skills_card()

        # 6. Problems & Comments Card
        self.build_comments_card()

    def build_toolbar_card(self):
        toolbar_card = tk.Frame(
            self.editor_frame,
            bg=COLOR_SURFACE,
            padx=14,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        toolbar_card.pack(fill=tk.X, pady=(0, 10))

        # Row 1: Week Title + Rename + Actions
        row1 = tk.Frame(toolbar_card, bg=COLOR_SURFACE)
        row1.pack(fill=tk.X)

        title_box = tk.Frame(row1, bg=COLOR_SURFACE)
        title_box.pack(side=tk.LEFT)

        self.lbl_week_title = tk.Label(
            title_box,
            text="Week 1 Log",
            font=("Segoe UI", 13, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        )
        self.lbl_week_title.pack(side=tk.LEFT)

        btn_rename = tk.Button(
            title_box,
            text="✏️ Rename",
            font=("Segoe UI", 8),
            fg="#64748B",
            bg="#F1F5F9",
            activebackground="#E2E8F0",
            relief=tk.FLAT,
            padx=6,
            pady=2,
            cursor="hand2",
            command=self.rename_week_action
        )
        btn_rename.pack(side=tk.LEFT, padx=(8, 0))

        btn_box = tk.Frame(row1, bg=COLOR_SURFACE)
        btn_box.pack(side=tk.RIGHT)

        btn_save = tk.Button(
            btn_box,
            text="💾 Save",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg="#475569",
            activebackground="#334155",
            relief=tk.FLAT,
            padx=7,
            pady=3,
            cursor="hand2",
            command=lambda: self.save_current_data(show_toast=True)
        )
        btn_save.pack(side=tk.LEFT, padx=2)

        btn_gen_tex = tk.Button(
            btn_box,
            text="📝 .tex",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_ACCENT,
            activebackground="#0369A1",
            relief=tk.FLAT,
            padx=7,
            pady=3,
            cursor="hand2",
            command=self.generate_tex_action
        )
        btn_gen_tex.pack(side=tk.LEFT, padx=2)

        self.btn_compile_pdf = tk.Button(
            btn_box,
            text="🚀 Compile PDF",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=9,
            pady=3,
            cursor="hand2",
            command=self.compile_pdf_action
        )
        self.btn_compile_pdf.pack(side=tk.LEFT, padx=2)

        btn_view_pdf = tk.Button(
            btn_box,
            text="👁️ View",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MAIN,
            bg="#E2E8F0",
            activebackground="#CBD5E1",
            relief=tk.FLAT,
            padx=7,
            pady=3,
            cursor="hand2",
            command=self.view_pdf_action
        )
        btn_view_pdf.pack(side=tk.LEFT, padx=2)

        btn_open_folder = tk.Button(
            btn_box,
            text="📂 Folder",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MAIN,
            bg="#E2E8F0",
            activebackground="#CBD5E1",
            relief=tk.FLAT,
            padx=7,
            pady=3,
            cursor="hand2",
            command=self.open_folder_action
        )
        btn_open_folder.pack(side=tk.LEFT, padx=2)

        # Row 2: Subtitle/Path Info
        self.lbl_week_status = tk.Label(
            toolbar_card,
            text="Editing active week",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SURFACE,
            anchor="w"
        )
        self.lbl_week_status.pack(fill=tk.X, pady=(3, 0))

    def build_metadata_card(self):
        meta_card = tk.Frame(
            self.editor_frame,
            bg=COLOR_SURFACE,
            padx=14,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        meta_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            meta_card,
            text="Week Information & Document Details",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        # Week Num
        tk.Label(meta_card, text="Week Number:", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE).grid(row=1, column=0, sticky="w", pady=3)
        self.entry_week_num = ttk.Entry(meta_card)
        self.entry_week_num.grid(row=1, column=1, sticky="ew", pady=3, padx=(6, 14))

        # Matric No
        tk.Label(meta_card, text="Matric Number:", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE).grid(row=1, column=2, sticky="w", pady=3)
        self.entry_matric = ttk.Entry(meta_card)
        self.entry_matric.grid(row=1, column=3, sticky="ew", pady=3, padx=(6, 0))

        # Date From
        tk.Label(meta_card, text="Date From:", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE).grid(row=2, column=0, sticky="w", pady=3)
        df_box = tk.Frame(meta_card, bg=COLOR_SURFACE)
        df_box.grid(row=2, column=1, sticky="ew", pady=3, padx=(6, 14))
        self.entry_date_from = ttk.Entry(df_box)
        self.entry_date_from.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_df_pick = tk.Button(
            df_box, text="📅 Pick", font=("Segoe UI", 8), fg=COLOR_PRIMARY, bg="#F0F9FF",
            activebackground="#E0F2FE", relief=tk.FLAT, padx=4, pady=1, cursor="hand2",
            command=lambda: open_date_picker(self, self.entry_date_from, include_day_name=False)
        )
        btn_df_pick.pack(side=tk.RIGHT, padx=(4, 0))

        # Date To
        tk.Label(meta_card, text="Date To:", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE).grid(row=2, column=2, sticky="w", pady=3)
        dt_box = tk.Frame(meta_card, bg=COLOR_SURFACE)
        dt_box.grid(row=2, column=3, sticky="ew", pady=3, padx=(6, 0))
        self.entry_date_to = ttk.Entry(dt_box)
        self.entry_date_to.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_dt_pick = tk.Button(
            dt_box, text="📅 Pick", font=("Segoe UI", 8), fg=COLOR_PRIMARY, bg="#F0F9FF",
            activebackground="#E0F2FE", relief=tk.FLAT, padx=4, pady=1, cursor="hand2",
            command=lambda: open_date_picker(self, self.entry_date_to, include_day_name=False)
        )
        btn_dt_pick.pack(side=tk.RIGHT, padx=(4, 0))


        # Course Code
        tk.Label(meta_card, text="Course Title:", font=("Segoe UI", 8, "bold"), bg=COLOR_SURFACE).grid(row=3, column=0, sticky="w", pady=3)
        self.entry_course = ttk.Entry(meta_card)
        self.entry_course.grid(row=3, column=1, columnspan=3, sticky="ew", pady=3, padx=(6, 0))

        meta_card.columnconfigure(1, weight=1)
        meta_card.columnconfigure(3, weight=1)

    def build_attendance_card(self):
        self.att_card = tk.Frame(
            self.editor_frame,
            bg=COLOR_SURFACE,
            padx=14,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.att_card.pack(fill=tk.X, pady=(0, 10))

        header_row = tk.Frame(self.att_card, bg=COLOR_SURFACE)
        header_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header_row,
            text="Daily Attendance (Interactive Checkboxes / Status)",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(side=tk.LEFT)

        btn_add_att_day = tk.Button(
            header_row,
            text="➕ Add Day",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.add_attendance_day_slot
        )
        btn_add_att_day.pack(side=tk.RIGHT)

        self.attendance_grid = tk.Frame(self.att_card, bg=COLOR_SURFACE)
        self.attendance_grid.pack(fill=tk.X)

        self.att_day_widgets: List[Dict[str, Any]] = []

    def build_activities_card(self):
        self.act_card = tk.Frame(
            self.editor_frame,
            bg=COLOR_SURFACE,
            padx=14,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.act_card.pack(fill=tk.X, pady=(0, 10))

        header_row = tk.Frame(self.act_card, bg=COLOR_SURFACE)
        header_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header_row,
            text="Weekly Activities (Timeline Days & Tasks)",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(side=tk.LEFT)

        btn_add_day = tk.Button(
            header_row,
            text="➕ Add Day Entry",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.add_activity_day_block
        )
        btn_add_day.pack(side=tk.RIGHT)

        self.days_container = tk.Frame(self.act_card, bg=COLOR_SURFACE)
        self.days_container.pack(fill=tk.X)

        self.activity_day_widgets: List[Dict[str, Any]] = []

    def build_skills_card(self):
        self.skills_card = tk.Frame(
            self.editor_frame,
            bg=COLOR_SURFACE,
            padx=14,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.skills_card.pack(fill=tk.X, pady=(0, 10))

        header_row = tk.Frame(self.skills_card, bg=COLOR_SURFACE)
        header_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header_row,
            text="Knowledge / Skills Gained",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(side=tk.LEFT)

        btn_add_skill = tk.Button(
            header_row,
            text="➕ Add Bullet Point",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.add_skill_bullet
        )
        btn_add_skill.pack(side=tk.RIGHT)

        self.skills_container = tk.Frame(self.skills_card, bg=COLOR_SURFACE)
        self.skills_container.pack(fill=tk.X)

        self.skill_bullet_widgets: List[Dict[str, Any]] = []

    def build_comments_card(self):
        self.comments_card = tk.Frame(
            self.editor_frame,
            bg=COLOR_SURFACE,
            padx=14,
            pady=10,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1
        )
        self.comments_card.pack(fill=tk.X, pady=(0, 10))

        header_row = tk.Frame(self.comments_card, bg=COLOR_SURFACE)
        header_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(
            header_row,
            text="Problems / Comments / Other Info",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(side=tk.LEFT)

        btn_add_comment = tk.Button(
            header_row,
            text="➕ Add Bullet Point",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.add_comment_bullet
        )
        btn_add_comment.pack(side=tk.RIGHT)

        self.comments_container = tk.Frame(self.comments_card, bg=COLOR_SURFACE)
        self.comments_container.pack(fill=tk.X)

        self.comment_bullet_widgets: List[Dict[str, Any]] = []

    def set_status(self, text: str, is_error: bool = False):
        self.lbl_status.configure(
            text=text,
            fg=COLOR_DANGER if is_error else "#334155"
        )

    def update_compiler_badge(self):
        diag = check_latex_environment(self.config.get("custom_pdflatex_path", ""))
        if diag["available"]:
            self.lbl_compiler_badge.configure(text="✅ pdflatex Ready", fg=COLOR_SUCCESS)
        else:
            self.lbl_compiler_badge.configure(text="⚠️ pdflatex Missing (Click to setup)", fg=COLOR_DANGER, cursor="hand2")
            self.lbl_compiler_badge.bind("<Button-1>", lambda e: self.open_settings_dialog())

    def _safe_scroll_canvas(self, canvas: tk.Canvas, content_frame: tk.Frame, units: int):
        req_h = content_frame.winfo_reqheight()
        canvas_h = canvas.winfo_height()
        if req_h <= canvas_h or canvas_h <= 1:
            canvas.yview_moveto(0.0)
            return

        # If already at top and scrolling up
        if units < 0 and canvas.canvasy(0) <= 0:
            canvas.yview_moveto(0.0)
            return

        # If already at bottom and scrolling down
        top, bottom = canvas.yview()
        if units > 0 and bottom >= 1.0:
            return

        canvas.yview_scroll(units, "units")
        if canvas.canvasy(0) < 0:
            canvas.yview_moveto(0.0)

    def _on_global_mousewheel(self, event, delta: Optional[int] = None):
        """
        Global handler allowing scrolling from anywhere in the window with bounds clamping.
        """
        # If a popup modal dialog is open and focused, skip parent scrolling
        try:
            toplevel = event.widget.winfo_toplevel()
            if toplevel != self:
                return
        except Exception:
            pass

        d = delta if delta is not None else getattr(event, "delta", 0)
        if d == 0:
            return
        units = int(-1 * (d / 120))
        if units == 0:
            units = -1 if d > 0 else 1

        # Check if cursor is over the sidebar
        try:
            sb_x = self.sidebar_frame.winfo_rootx()
            sb_w = self.sidebar_frame.winfo_width()
            sb_y = self.sidebar_frame.winfo_rooty()
            sb_h = self.sidebar_frame.winfo_height()

            if sb_x <= event.x_root <= (sb_x + sb_w) and sb_y <= event.y_root <= (sb_y + sb_h):
                self._safe_scroll_canvas(self.week_canvas, self.week_buttons_frame, units)
                return
        except Exception:
            pass

        # Otherwise scroll main scrollable frame
        try:
            self._safe_scroll_canvas(self.scroll_area.canvas, self.scroll_area.scrollable_content, units)
        except Exception:
            pass


    # ==========================================
    # WEEK LIST & NAVIGATION
    # ==========================================

    def update_sidebar_active_state(self, active_path: Optional[str]):
        """
        Visually highlights the currently active week in the sidebar.
        """
        for item in self.sidebar_items:
            is_active = (item["path"] == active_path)
            btn_bg = "#1E293B" if is_active else "#0F172A"
            btn_fg = "#38BDF8" if is_active else "#E2E8F0"
            border_color = "#0284C7" if is_active else "#1E293B"

            item["row"].configure(bg=btn_bg, highlightbackground=border_color)
            item["btn"].configure(
                bg=btn_bg,
                fg=btn_fg,
                font=("Segoe UI", 8, "bold" if is_active else "normal"),
                activebackground="#334155",
                activeforeground="#FFFFFF"
            )
            item["badge"].configure(bg=btn_bg)

    def refresh_week_list(self):
        for widget in self.week_buttons_frame.winfo_children():
            widget.destroy()
        self.sidebar_items.clear()

        weeks = self.folder_manager.list_week_folders()

        if not weeks:
            lbl_empty = tk.Label(
                self.week_buttons_frame,
                text="No reports found.\nClick '+ Create New Week'",
                font=("Segoe UI", 8),
                fg="#64748B",
                bg=COLOR_SIDEBAR_BG,
                justify="center",
                pady=14
            )
            lbl_empty.pack(fill=tk.X)
            self.show_empty_state()
            return

        active_path = self.current_week_info["path"] if self.current_week_info else None
        target_week_to_select = None

        for w in weeks:
            badge = "📄 PDF" if w["has_pdf"] else "✏️ Draft"
            badge_color = "#10B981" if w["has_pdf"] else "#F59E0B"

            row = tk.Frame(self.week_buttons_frame, bg="#0F172A", highlightbackground="#1E293B", highlightthickness=1)
            row.pack(fill=tk.X, pady=2)

            btn = tk.Button(
                row,
                text=f"{w['name']}",
                font=("Segoe UI", 8),
                fg="#E2E8F0",
                bg="#0F172A",
                activebackground="#334155",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                anchor="w",
                padx=6,
                pady=5,
                cursor="hand2",
                command=lambda item=w: self.select_week(item)
            )
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

            lbl_badge = tk.Label(
                row,
                text=badge,
                font=("Segoe UI", 7, "bold"),
                fg=badge_color,
                bg="#0F172A",
                padx=4
            )
            lbl_badge.pack(side=tk.RIGHT)

            self.sidebar_items.append({
                "path": w["path"],
                "row": row,
                "btn": btn,
                "badge": lbl_badge
            })

            if w["path"] == active_path:
                target_week_to_select = w

        if target_week_to_select:
            self.select_week(target_week_to_select)
        elif weeks:
            self.select_week(weeks[-1])

    def show_empty_state(self):
        self.editor_frame.pack_forget()
        self.empty_state_frame.pack(fill=tk.BOTH, expand=True)
        self.current_week_info = None

    def select_week(self, week_info: Dict[str, Any]):
        if self.current_week_info and self.current_week_info["path"] != week_info["path"]:
            self.save_current_data(show_toast=False)

        self.current_week_info = week_info
        self.update_sidebar_active_state(week_info["path"])

        self.empty_state_frame.pack_forget()
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        data = load_week_data(week_info["path"], default_matric=self.config.get("matric_no", "S70012"))
        self.current_data = data

        self.populate_form(data)

        self.lbl_week_title.configure(text=week_info["name"])
        pdf_path = self.folder_manager.get_pdf_path(week_info["path"])
        has_pdf = os.path.exists(pdf_path)
        self.lbl_week_status.configure(
            text=f"Report: {week_info['name']}  |  Status: {'PDF Ready ✅' if has_pdf else 'Draft 📝'}"
        )
        self.set_status(f"Loaded {week_info['name']}")


    def create_new_week_action(self):
        next_num = self.folder_manager.get_next_week_number()
        default_folder_name = f"Week {next_num} Log"
        
        dialog = CreateWeekDialog(self, default_name=default_folder_name, default_num=next_num)
        self.wait_window(dialog)

        if dialog.result_name:
            folder_name = dialog.result_name
            week_num = dialog.result_num
            try:
                new_path = self.folder_manager.create_week_folder(folder_name=folder_name, week_num=week_num)

                initial_data = get_default_week_data(default_matric=self.config.get("matric_no", "S70012"))
                initial_data["week_num"] = str(week_num)
                initial_data["course_code"] = self.config.get("course_code", "CSF4992 / CSF49712 INDUSTRIAL TRAINING")
                save_week_data(new_path, initial_data)
                save_latex_file(new_path, initial_data)

                self.refresh_week_list()
                for w in self.folder_manager.list_week_folders():
                    if w["path"] == new_path:
                        self.select_week(w)
                        break

                messagebox.showinfo("Week Created", f"Successfully created '{folder_name}' in Report folder!", parent=self)
            except Exception as e:
                messagebox.showerror("Error Creating Week", str(e), parent=self)

    def rename_week_action(self):
        if not self.current_week_info:
            return
        current_name = self.current_week_info["name"]
        current_path = self.current_week_info["path"]

        new_name = simpledialog.askstring(
            "Rename Report Folder",
            "Enter new name for this report folder:",
            initialvalue=current_name,
            parent=self
        )

        if new_name and new_name.strip() and new_name.strip() != current_name:
            try:
                # Save draft first
                self.save_current_data(show_toast=False)
                new_path = self.folder_manager.rename_week_folder(current_path, new_name.strip())
                self.current_week_info["name"] = new_name.strip()
                self.current_week_info["path"] = new_path
                self.lbl_week_title.configure(text=new_name.strip())
                self.refresh_week_list()
                for w in self.folder_manager.list_week_folders():
                    if w["path"] == new_path:
                        self.select_week(w)
                        break
                messagebox.showinfo("Renamed", f"Folder and files renamed to '{new_name.strip()}'.", parent=self)
            except Exception as e:
                messagebox.showerror("Error Renaming", str(e), parent=self)

    # ==========================================
    # FORM POPULATION & EXTRACTION
    # ==========================================

    def populate_form(self, data: Dict[str, Any]):
        # Metadata
        self.entry_week_num.delete(0, tk.END)
        self.entry_week_num.insert(0, str(data.get("week_num", "1")))

        self.entry_date_from.delete(0, tk.END)
        self.entry_date_from.insert(0, str(data.get("date_from", "")))

        self.entry_date_to.delete(0, tk.END)
        self.entry_date_to.insert(0, str(data.get("date_to", "")))

        self.entry_matric.delete(0, tk.END)
        self.entry_matric.insert(0, str(data.get("matric_no", self.config.get("matric_no", "S70012"))))

        self.entry_course.delete(0, tk.END)
        self.entry_course.insert(0, str(data.get("course_code", self.config.get("course_code", "CSF4992 / CSF49712 INDUSTRIAL TRAINING"))))

        # Attendance
        for item in self.att_day_widgets:
            item["frame"].destroy()
        self.att_day_widgets.clear()

        att_list = normalize_attendance_data(data.get("attendance"))
        for day_att in att_list:
            self.add_attendance_day_slot(
                label=day_att.get("label", ""),
                status=day_att.get("status", "present"),
                checked=day_att.get("checked", True)
            )

        # Weekly Activities
        for item in self.activity_day_widgets:
            item["frame"].destroy()
        self.activity_day_widgets.clear()

        activities = data.get("daily_activities", [])
        for act in activities:
            self.add_activity_day_block(
                date_label=act.get("date_label", ""),
                items=act.get("items", [])
            )

        # Skills
        for item in self.skill_bullet_widgets:
            item["frame"].destroy()
        self.skill_bullet_widgets.clear()

        for skill in data.get("skills_gained", []):
            self.add_skill_bullet(text=skill)

        # Comments
        for item in self.comment_bullet_widgets:
            item["frame"].destroy()
        self.comment_bullet_widgets.clear()

        for comment in data.get("problems_comments", []):
            self.add_comment_bullet(text=comment)

    def extract_form_data(self) -> Dict[str, Any]:
        data = {
            "week_num": self.entry_week_num.get().strip(),
            "date_from": self.entry_date_from.get().strip(),
            "date_to": self.entry_date_to.get().strip(),
            "matric_no": self.entry_matric.get().strip(),
            "course_code": self.entry_course.get().strip(),
            "attendance": [],
            "daily_activities": [],
            "skills_gained": [],
            "problems_comments": []
        }

        # Attendance extraction
        for item in self.att_day_widgets:
            label = item["label_entry"].get().strip() or f"Day {len(data['attendance'])+1}"
            checked = item["check_var"].get()
            status_val = item["status_var"].get()

            status_map = {
                "Present": "present",
                "MC": "mc",
                "Public Holiday": "holiday",
                "Leave": "leave",
                "Absent": "absent"
            }
            clean_status = status_map.get(status_val, "present" if checked else "absent")
            if checked:
                clean_status = "present"

            data["attendance"].append({
                "label": label,
                "status": clean_status,
                "checked": checked
            })

        # Activities extraction
        for day_block in self.activity_day_widgets:
            date_label = day_block["entry_date"].get().strip()
            items = []
            for item_w in day_block["items"]:
                txt = item_w["entry"].get().strip()
                if txt:
                    items.append(txt)
            data["daily_activities"].append({
                "date_label": date_label,
                "items": items
            })

        # Skills extraction
        for skill_w in self.skill_bullet_widgets:
            txt = skill_w["entry"].get().strip()
            if txt:
                data["skills_gained"].append(txt)

        # Comments extraction
        for comm_w in self.comment_bullet_widgets:
            txt = comm_w["entry"].get().strip()
            if txt:
                data["problems_comments"].append(txt)

        return data

    # ==========================================
    # DYNAMIC ATTENDANCE TILES
    # ==========================================

    def add_attendance_day_slot(self, label: str = "", status: str = "present", checked: bool = True):
        idx = len(self.att_day_widgets) + 1
        if not label:
            label = f"Day {idx}"

        tile_frame = tk.Frame(
            self.attendance_grid,
            bg="#F8FAFC",
            padx=6,
            pady=5,
            highlightbackground="#CBD5E1",
            highlightthickness=1
        )
        
        row_pos = (idx - 1) // 5
        col_pos = (idx - 1) % 5
        tile_frame.grid(row=row_pos, column=col_pos, padx=3, pady=3, sticky="nsew")
        self.attendance_grid.columnconfigure(col_pos, weight=1)

        top_bar = tk.Frame(tile_frame, bg="#F8FAFC")
        top_bar.pack(fill=tk.X, pady=(0, 2))

        label_entry = ttk.Entry(top_bar, font=("Segoe UI", 8, "bold"), width=6)
        label_entry.insert(0, label)
        label_entry.pack(side=tk.LEFT)

        btn_del = tk.Button(
            top_bar,
            text="✕",
            font=("Segoe UI", 7, "bold"),
            fg="#94A3B8",
            bg="#F8FAFC",
            activeforeground=COLOR_DANGER,
            relief=tk.FLAT,
            padx=2,
            cursor="hand2"
        )
        btn_del.pack(side=tk.RIGHT)

        check_var = tk.BooleanVar(value=checked)
        status_options = ["Present", "MC", "Public Holiday", "Leave", "Absent"]
        
        status_reverse = {
            "present": "Present",
            "mc": "MC",
            "holiday": "Public Holiday",
            "leave": "Leave",
            "absent": "Absent"
        }
        initial_status = status_reverse.get(status.lower(), "Present" if checked else "Absent")
        status_var = tk.StringVar(value=initial_status)

        cb = ttk.Checkbutton(
            tile_frame,
            text="Present",
            variable=check_var
        )
        cb.pack(anchor="w", pady=(1, 1))

        status_combo = ttk.Combobox(
            tile_frame,
            values=status_options,
            textvariable=status_var,
            state="readonly",
            width=9,
            font=("Segoe UI", 8)
        )
        status_combo.pack(fill=tk.X, pady=(1, 0))

        def on_check_toggled():
            if check_var.get():
                status_var.set("Present")
            else:
                if status_var.get() == "Present":
                    status_var.set("Absent")

        cb.configure(command=on_check_toggled)

        def on_status_selected(event):
            sel = status_var.get()
            if sel == "Present":
                check_var.set(True)
            else:
                check_var.set(False)

        status_combo.bind("<<ComboboxSelected>>", on_status_selected)

        day_dict = {
            "frame": tile_frame,
            "label_entry": label_entry,
            "check_var": check_var,
            "status_var": status_var
        }

        btn_del.configure(command=lambda: self.remove_attendance_day_slot(day_dict))
        self.att_day_widgets.append(day_dict)

    def remove_attendance_day_slot(self, day_dict: Dict[str, Any]):
        if len(self.att_day_widgets) <= 1:
            messagebox.showwarning("Warning", "At least one attendance day is required.", parent=self)
            return
        day_dict["frame"].destroy()
        if day_dict in self.att_day_widgets:
            self.att_day_widgets.remove(day_dict)
        self.regrid_attendance_tiles()

    def regrid_attendance_tiles(self):
        for i, item in enumerate(self.att_day_widgets):
            row_pos = i // 5
            col_pos = i % 5
            item["frame"].grid(row=row_pos, column=col_pos, padx=3, pady=3, sticky="nsew")
            self.attendance_grid.columnconfigure(col_pos, weight=1)

    # ==========================================
    # DYNAMIC ACTIVITIES & BULLETS
    # ==========================================

    def add_activity_day_block(self, date_label: str = "", items: Optional[List[str]] = None):
        day_frame = tk.Frame(
            self.days_container,
            bg="#F8FAFC",
            padx=10,
            pady=8,
            highlightbackground="#CBD5E1",
            highlightthickness=1
        )
        day_frame.pack(fill=tk.X, pady=4)

        top_row = tk.Frame(day_frame, bg="#F8FAFC")
        top_row.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            top_row,
            text="📅 Date / Day Label:",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_PRIMARY,
            bg="#F8FAFC"
        ).pack(side=tk.LEFT, padx=(0, 6))

        entry_date = ttk.Entry(top_row)
        entry_date.insert(0, date_label or "DD/MM/YYYY (Day)")
        entry_date.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_pick_date = tk.Button(
            top_row,
            text="📅 Pick Date",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_PRIMARY,
            bg="#E0F2FE",
            activebackground="#BAE6FD",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: open_date_picker(self, entry_date, include_day_name=True)
        )
        btn_pick_date.pack(side=tk.LEFT, padx=(0, 8))


        day_dict = {
            "frame": day_frame,
            "entry_date": entry_date,
            "items_container": None,
            "items": []
        }

        btn_delete_day = tk.Button(
            top_row,
            text="🗑️ Delete Day",
            font=("Segoe UI", 8),
            fg=COLOR_DANGER,
            bg="#FEE2E2",
            activebackground="#FECACA",
            relief=tk.FLAT,
            padx=6,
            pady=2,
            cursor="hand2",
            command=lambda: self.remove_activity_day_block(day_dict)
        )
        btn_delete_day.pack(side=tk.RIGHT)

        items_container = tk.Frame(day_frame, bg="#F8FAFC")
        items_container.pack(fill=tk.X, padx=10, pady=(2, 4))
        day_dict["items_container"] = items_container

        if items:
            for it in items:
                self.add_activity_task_item(day_dict, text=it)
        else:
            self.add_activity_task_item(day_dict, text="")

        btn_add_task = tk.Button(
            day_frame,
            text="➕ Add Task Item",
            font=("Segoe UI", 8),
            fg="#0284C7",
            bg="#F0F9FF",
            activebackground="#E0F2FE",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self.add_activity_task_item(day_dict, text="")
        )
        btn_add_task.pack(anchor="w", padx=10)

        self.activity_day_widgets.append(day_dict)


    def remove_activity_day_block(self, day_dict: Dict[str, Any]):
        if len(self.activity_day_widgets) <= 1:
            messagebox.showwarning("Warning", "At least one day entry is recommended.", parent=self)
        day_dict["frame"].destroy()
        if day_dict in self.activity_day_widgets:
            self.activity_day_widgets.remove(day_dict)

    def add_activity_task_item(self, day_dict: Dict[str, Any], text: str = ""):
        container = day_dict["items_container"]
        row = tk.Frame(container, bg="#F8FAFC")
        row.pack(fill=tk.X, pady=2)

        tk.Label(row, text="•", font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, bg="#F8FAFC").pack(side=tk.LEFT, padx=(0, 4))

        entry = ttk.Entry(row)
        entry.insert(0, text)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        item_dict = {"frame": row, "entry": entry}

        btn_del = tk.Button(
            row,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            fg="#94A3B8",
            bg="#F8FAFC",
            activeforeground=COLOR_DANGER,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.remove_activity_task_item(day_dict, item_dict)
        )
        btn_del.pack(side=tk.RIGHT)

        day_dict["items"].append(item_dict)

    def remove_activity_task_item(self, day_dict: Dict[str, Any], item_dict: Dict[str, Any]):
        item_dict["frame"].destroy()
        if item_dict in day_dict["items"]:
            day_dict["items"].remove(item_dict)

    def add_skill_bullet(self, text: str = ""):
        row = tk.Frame(self.skills_container, bg=COLOR_SURFACE)
        row.pack(fill=tk.X, pady=2)

        tk.Label(row, text="•", font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, bg=COLOR_SURFACE).pack(side=tk.LEFT, padx=(0, 4))

        entry = ttk.Entry(row)
        entry.insert(0, text)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        item_dict = {"frame": row, "entry": entry}

        btn_del = tk.Button(
            row,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            fg="#94A3B8",
            bg=COLOR_SURFACE,
            activeforeground=COLOR_DANGER,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.remove_skill_bullet(item_dict)
        )
        btn_del.pack(side=tk.RIGHT)

        self.skill_bullet_widgets.append(item_dict)

    def remove_skill_bullet(self, item_dict: Dict[str, Any]):
        item_dict["frame"].destroy()
        if item_dict in self.skill_bullet_widgets:
            self.skill_bullet_widgets.remove(item_dict)

    def add_comment_bullet(self, text: str = ""):
        row = tk.Frame(self.comments_container, bg=COLOR_SURFACE)
        row.pack(fill=tk.X, pady=2)

        tk.Label(row, text="•", font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARY, bg=COLOR_SURFACE).pack(side=tk.LEFT, padx=(0, 4))

        entry = ttk.Entry(row)
        entry.insert(0, text)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        item_dict = {"frame": row, "entry": entry}

        btn_del = tk.Button(
            row,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            fg="#94A3B8",
            bg=COLOR_SURFACE,
            activeforeground=COLOR_DANGER,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.remove_comment_bullet(item_dict)
        )
        btn_del.pack(side=tk.RIGHT)

        self.comment_bullet_widgets.append(item_dict)

    def remove_comment_bullet(self, item_dict: Dict[str, Any]):
        item_dict["frame"].destroy()
        if item_dict in self.comment_bullet_widgets:
            self.comment_bullet_widgets.remove(item_dict)

    # ==========================================
    # ACTIONS: SAVE, GENERATE, COMPILE, VIEW
    # ==========================================

    def save_current_data(self, show_toast: bool = False):
        if not self.current_week_info:
            return
        data = self.extract_form_data()
        self.current_data = data
        week_path = self.current_week_info["path"]
        save_week_data(week_path, data)
        if show_toast:
            self.set_status(f"Saved changes to {self.current_week_info['name']}")

    def generate_tex_action(self):
        if not self.current_week_info:
            return
        self.save_current_data(show_toast=False)
        week_path = self.current_week_info["path"]
        tex_path = save_latex_file(week_path, self.current_data)
        tex_filename = os.path.basename(tex_path)
        self.set_status(f"Generated {tex_filename} in {self.current_week_info['name']}")
        messagebox.showinfo(
            "LaTeX Generated",
            f"Successfully created {tex_filename} at:\n{tex_path}",
            parent=self
        )

    def compile_pdf_action(self):
        if not self.current_week_info:
            return

        custom_path = self.config.get("custom_pdflatex_path", "")
        diag = check_latex_environment(custom_path)
        if not diag["available"]:
            self.show_missing_compiler_dialog()
            return

        self.save_current_data(show_toast=False)
        week_path = self.current_week_info["path"]
        save_latex_file(week_path, self.current_data)

        self.btn_compile_pdf.configure(state="disabled", text="⏳ Compiling...")
        self.set_status("Compiling LaTeX to PDF, please wait...")

        def run_compilation():
            clean_aux = self.config.get("auto_clean_aux", True)
            success, message, pdf_path = compile_pdf(week_path, custom_path=custom_path, clean_aux=clean_aux)
            self.after(0, lambda: self.on_compilation_finished(success, message, pdf_path))

        threading.Thread(target=run_compilation, daemon=True).start()

    def on_compilation_finished(self, success: bool, message: str, pdf_path: str):
        self.btn_compile_pdf.configure(state="normal", text="🚀 Compile PDF")
        if success:
            self.set_status("PDF compiled successfully! ✅")
            self.refresh_week_list()
            pdf_name = os.path.basename(pdf_path)
            ans = messagebox.askyesno(
                "Compilation Successful",
                f"{pdf_name} was generated successfully!\n\nWould you like to open the PDF now?",
                parent=self
            )
            if ans and pdf_path:
                FolderManager.open_file_default(pdf_path)
        else:
            self.set_status("Compilation failed with errors ❌", is_error=True)
            messagebox.showerror("Compilation Error", message, parent=self)

    def view_pdf_action(self):
        if not self.current_week_info:
            return
        pdf_path = self.folder_manager.get_pdf_path(self.current_week_info["path"])
        if os.path.exists(pdf_path):
            FolderManager.open_file_default(pdf_path)
        else:
            pdf_name = f"{self.current_week_info['name']}.pdf"
            messagebox.showinfo(
                "PDF Not Found",
                f"{pdf_name} has not been compiled yet.\nClick '🚀 Compile PDF' to generate it.",
                parent=self
            )

    def open_folder_action(self):
        if not self.current_week_info:
            FolderManager.open_in_explorer(self.folder_manager.reports_dir)
        else:
            FolderManager.open_in_explorer(self.current_week_info["path"])

    def get_reports_header_text(self) -> str:
        rep_dir = self.folder_manager.reports_dir
        try:
            rel = os.path.relpath(rep_dir, self.workspace_dir)
            if not rel.startswith(".."):
                return f"REPORTS ({rel}/)"
        except Exception:
            pass
        folder_base = os.path.basename(rep_dir) or rep_dir
        return f"REPORTS ({folder_base}/)"

    def open_settings_dialog(self):
        def on_saved(new_config):
            self.config = new_config
            self.folder_manager.set_reports_dir(self.config.get("custom_reports_dir", ""))
            self.lbl_reports_header.configure(text=self.get_reports_header_text())
            self.update_compiler_badge()
            self.refresh_week_list()
            self.set_status("Settings saved. Reports directory updated.")

        SettingsDialog(self, self.workspace_dir, self.config, on_save_callback=on_saved)


    def show_missing_compiler_dialog(self):
        msg_win = tk.Toplevel(self)
        msg_win.title("LaTeX Compiler Required")
        msg_win.geometry("540x330")
        msg_win.resizable(False, False)
        msg_win.transient(self)
        msg_win.grab_set()
        msg_win.configure(bg="#FFFFFF")

        msg_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 540) // 2
        y = self.winfo_y() + (self.winfo_height() - 330) // 2
        msg_win.geometry(f"+{x}+{y}")

        pad = tk.Frame(msg_win, bg="#FFFFFF", padx=20, pady=18)
        pad.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            pad,
            text="⚠️  pdflatex Compiler Not Found",
            font=("Segoe UI", 13, "bold"),
            fg=COLOR_DANGER,
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            pad,
            text="To compile your reports into PDF, you need a LaTeX compiler (such as MiKTeX or TeX Live). You can install one or browse for an existing pdflatex executable:",
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#FFFFFF",
            wraplength=490,
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        # Action Buttons
        btn_row1 = tk.Frame(pad, bg="#FFFFFF")
        btn_row1.pack(anchor="w", pady=(0, 8))

        def browse_custom_compiler():
            chosen_file = filedialog.askopenfilename(
                title="Select pdflatex Executable",
                filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")],
                parent=msg_win
            )
            if chosen_file:
                diag = check_latex_environment(chosen_file)
                if diag["available"]:
                    self.config["custom_pdflatex_path"] = chosen_file
                    save_config(self.workspace_dir, self.config)
                    self.update_compiler_badge()
                    self.set_status("Custom pdflatex compiler configured! ✅")
                    messagebox.showinfo(
                        "Compiler Configured",
                        f"✅ Successfully configured custom pdflatex!\n\nVersion: {diag['version']}\nPath: {chosen_file}",
                        parent=msg_win
                    )
                    msg_win.destroy()
                else:
                    messagebox.showerror(
                        "Invalid Compiler",
                        f"❌ The selected executable is not a working pdflatex compiler:\n{chosen_file}",
                        parent=msg_win
                    )

        tk.Button(
            btn_row1,
            text="📁 Browse Custom pdflatex.exe...",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg="#0F766E",
            activebackground="#115E59",
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=browse_custom_compiler
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row1,
            text="⚙️ Open Full Settings",
            font=("Segoe UI", 9),
            fg="#334155",
            bg="#F1F5F9",
            activebackground="#E2E8F0",
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2",
            command=lambda: [msg_win.destroy(), self.open_settings_dialog()]
        ).pack(side=tk.LEFT)

        btn_row2 = tk.Frame(pad, bg="#FFFFFF")
        btn_row2.pack(anchor="w", pady=(0, 12))

        tk.Button(
            btn_row2,
            text="📥 Download MiKTeX (Recommended)",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY_HOVER,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: webbrowser.open(MIKTEX_URL)
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_row2,
            text="📥 Download TeX Live",
            font=("Segoe UI", 8, "bold"),
            fg="#FFFFFF",
            bg=COLOR_ACCENT,
            activebackground="#0369A1",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: webbrowser.open(TEXLIVE_URL)
        ).pack(side=tk.LEFT)

        tk.Label(
            pad,
            text="Note: You can still edit and generate the LaTeX files without a compiler.",
            font=("Segoe UI", 8, "italic"),
            fg="#64748B",
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        tk.Button(
            pad,
            text="Close",
            font=("Segoe UI", 9),
            fg="#475569",
            bg="#E2E8F0",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=msg_win.destroy
        ).pack(side=tk.RIGHT)

