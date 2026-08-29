import calendar
import datetime
import re
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

COLOR_PRIMARY = "#00478F"
COLOR_PRIMARY_HOVER = "#003366"
COLOR_ACCENT = "#0284C7"
COLOR_SELECTED = "#00478F"
COLOR_TODAY = "#0284C7"
COLOR_HOVER = "#E0F2FE"
COLOR_SURFACE = "#FFFFFF"
COLOR_BG = "#F8FAFC"

def parse_date_string(date_str: str) -> Optional[datetime.date]:
    """
    Attempts to parse date strings like 'DD/MM/YYYY', 'DD/MM/YYYY (Day)', 'YYYY-MM-DD'.
    """
    if not date_str:
        return None
    
    # 1. Match DD/MM/YYYY
    match_dmy = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", date_str)
    if match_dmy:
        try:
            d, m, y = map(int, match_dmy.groups())
            return datetime.date(y, m, d)
        except ValueError:
            pass

    # 2. Match YYYY-MM-DD
    match_ymd = re.search(r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})", date_str)
    if match_ymd:
        try:
            y, m, d = map(int, match_ymd.groups())
            return datetime.date(y, m, d)
        except ValueError:
            pass

    return None

class DatePickerDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, initial_date: Optional[datetime.date] = None, include_day_name: bool = True, on_selected: Optional[Callable[[str], None]] = None):
        super().__init__(parent)
        self.title("Select Date")
        self.geometry("320x330")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=COLOR_BG)

        self.include_day_name = include_day_name
        self.on_selected = on_selected
        self.selected_date = initial_date or datetime.date.today()
        self.current_year = self.selected_date.year
        self.current_month = self.selected_date.month

        # Position dialog near parent
        self.update_idletasks()
        x = parent.winfo_pointerx() - 160
        y = parent.winfo_pointery() - 100
        # Ensure within screen bounds
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(10, min(x, screen_w - 330))
        y = max(10, min(y, screen_h - 340))
        self.geometry(f"+{x}+{y}")

        self.build_ui()

    def build_ui(self):
        container = tk.Frame(self, bg=COLOR_BG, padx=12, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Month / Year Header with < > Buttons
        nav_frame = tk.Frame(container, bg=COLOR_BG)
        nav_frame.pack(fill=tk.X, pady=(0, 8))

        btn_prev = tk.Button(
            nav_frame,
            text="◀",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_PRIMARY,
            bg="#E2E8F0",
            activebackground="#CBD5E1",
            relief=tk.FLAT,
            padx=6,
            pady=2,
            cursor="hand2",
            command=self.prev_month
        )
        btn_prev.pack(side=tk.LEFT)

        self.lbl_month_year = tk.Label(
            nav_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_BG
        )
        self.lbl_month_year.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_next = tk.Button(
            nav_frame,
            text="▶",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_PRIMARY,
            bg="#E2E8F0",
            activebackground="#CBD5E1",
            relief=tk.FLAT,
            padx=6,
            pady=2,
            cursor="hand2",
            command=self.next_month
        )
        btn_next.pack(side=tk.RIGHT)

        # Calendar Grid
        self.cal_frame = tk.Frame(container, bg=COLOR_SURFACE, padx=6, pady=6, highlightbackground="#CBD5E1", highlightthickness=1)
        self.cal_frame.pack(fill=tk.BOTH, expand=True)

        # Quick Today & Cancel Buttons
        bottom_bar = tk.Frame(container, bg=COLOR_BG)
        bottom_bar.pack(fill=tk.X, pady=(8, 0))

        btn_today = tk.Button(
            bottom_bar,
            text="Today",
            font=("Segoe UI", 8),
            fg="#0284C7",
            bg="#F0F9FF",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.select_today
        )
        btn_today.pack(side=tk.LEFT)

        btn_cancel = tk.Button(
            bottom_bar,
            text="Cancel",
            font=("Segoe UI", 8),
            fg="#64748B",
            bg="#F1F5F9",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side=tk.RIGHT)

        self.render_calendar()

    def render_calendar(self):
        # Clear existing grid
        for child in self.cal_frame.winfo_children():
            child.destroy()

        # Update Month/Year Label
        month_name = calendar.month_name[self.current_month]
        self.lbl_month_year.configure(text=f"{month_name} {self.current_year}")

        # Day of week headers (Mon to Sun)
        day_headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, h in enumerate(day_headers):
            lbl = tk.Label(
                self.cal_frame,
                text=h,
                font=("Segoe UI", 8, "bold"),
                fg="#64748B" if col < 5 else "#94A3B8",
                bg=COLOR_SURFACE,
                width=3
            )
            lbl.grid(row=0, column=col, pady=(0, 4))
            self.cal_frame.columnconfigure(col, weight=1)

        # Days of month
        month_matrix = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.date.today()

        for r_idx, week in enumerate(month_matrix):
            for c_idx, day_num in enumerate(week):
                if day_num == 0:
                    lbl_empty = tk.Label(self.cal_frame, text="", bg=COLOR_SURFACE)
                    lbl_empty.grid(row=r_idx + 1, column=c_idx, padx=1, pady=1)
                else:
                    d_obj = datetime.date(self.current_year, self.current_month, day_num)
                    is_selected = (d_obj == self.selected_date)
                    is_today = (d_obj == today)

                    btn_bg = COLOR_SELECTED if is_selected else (COLOR_HOVER if is_today else COLOR_SURFACE)
                    btn_fg = "#FFFFFF" if is_selected else (COLOR_PRIMARY if is_today else "#1E293B")
                    font_style = ("Segoe UI", 8, "bold" if (is_selected or is_today) else "normal")

                    btn = tk.Button(
                        self.cal_frame,
                        text=str(day_num),
                        font=font_style,
                        fg=btn_fg,
                        bg=btn_bg,
                        activebackground=COLOR_HOVER,
                        activeforeground=COLOR_PRIMARY,
                        relief=tk.FLAT,
                        width=3,
                        height=1,
                        cursor="hand2",
                        command=lambda d=d_obj: self.on_day_clicked(d)
                    )
                    btn.grid(row=r_idx + 1, column=c_idx, padx=1, pady=1, sticky="nsew")

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.render_calendar()

    def select_today(self):
        self.on_day_clicked(datetime.date.today())

    def on_day_clicked(self, date_obj: datetime.date):
        if self.include_day_name:
            formatted = date_obj.strftime("%d/%m/%Y (%A)")
        else:
            formatted = date_obj.strftime("%d/%m/%Y")

        if self.on_selected:
            self.on_selected(formatted)

        self.destroy()

def open_date_picker(parent: tk.Tk, entry_widget: ttk.Entry, include_day_name: bool = True):
    """
    Helper function that parses current entry text (if any) and opens the date picker.
    When a date is chosen, updates the entry widget directly.
    """
    current_text = entry_widget.get().strip()
    parsed_date = parse_date_string(current_text)

    def on_date_chosen(formatted_date: str):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, formatted_date)

    DatePickerDialog(
        parent=parent,
        initial_date=parsed_date,
        include_day_name=include_day_name,
        on_selected=on_date_chosen
    )
