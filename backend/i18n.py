"""
Internationalization (i18n) Module for UMT Intern Report Manager
Supports English (en) and Bahasa Melayu (ms)
"""

from typing import Dict, Any, Optional

_CURRENT_LANG = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Branding & Sidebar
        "app_title": "UMT Intern Report Manager (IRP)",
        "app_sub": "Industrial Training e-Logbook",
        "create_new_week": "+ Create New Week",
        "reports_header": "REPORTS",
        "settings": "⚙️ Settings",
        "refresh": "🔄 Refresh",
        "about": "ℹ️ About",
        "no_reports": "No weekly reports found.\nClick '+ Create New Week' to begin!",
        "has_tex": "LaTeX ready",
        "has_pdf": "PDF compiled",

        # Header Info Card
        "week_number": "Week Number:",
        "week_placeholder": "e.g., 1",
        "date_from": "Date From:",
        "date_to": "Date To:",
        "date_format_hint": "DD/MM/YYYY",
        "matric_no": "Matric Number:",
        "matric_hint": "e.g., S70012",
        "course_title": "Course Title / Code:",
        "pick_date": "📅 Pick",
        "calc_to_date": "⚡ Set 5-Day Week",

        # Section 1: Attendance
        "sec_attendance": "Daily Attendance & Leave Status",
        "sec_attendance_sub": "Check the days you were present or select your leave/MC/public holiday status",
        "status_present": "Present",
        "status_mc": "MC (Medical Leave)",
        "status_holiday": "Public Holiday",
        "status_leave": "Personal Leave",
        "status_absent": "Absent",

        # Section 2: Daily Activities
        "sec_activities": "Daily Activities & Task Outline",
        "sec_activities_sub": "Manage daily logbook entries, dates, and activity bullet points",
        "add_day": "+ Add Day",
        "delete_day": "✕ Delete Day",
        "add_activity_bullet": "+ Add Activity Bullet",
        "activity_placeholder": "Enter task, activity, or deliverable completed on this day...",
        "day_label_default": "DD/MM/YYYY (Monday)",

        # Section 3: Knowledge & Skills Gained
        "sec_skills": "Knowledge & Skills Gained",
        "sec_skills_sub": "Key technical skills, tools, soft skills, or domain knowledge acquired this week",
        "add_skill_bullet": "+ Add Skill Bullet",
        "skill_placeholder": "e.g., Gained hands-on experience in system architecture and backend optimization...",

        # Section 4: Problems / Comments / Observations
        "sec_problems": "Problems Encountered, Comments & Observations",
        "sec_problems_sub": "Challenges faced, problem resolution, feedback, or general notes",
        "add_problem_bullet": "+ Add Comment / Problem",
        "problem_placeholder": "e.g., Encountered minor deployment issues, resolved after reviewing documentation...",

        # Action Bar Buttons
        "btn_save_draft": "💾 Save Draft (Ctrl+S)",
        "btn_generate_latex": "⚡ Generate LaTeX",
        "btn_compile_pdf": "🚀 Compile PDF",
        "btn_view_pdf": "📄 View PDF",
        "btn_open_folder": "📂 Open Folder",
        "btn_rename_week": "✏️ Rename Folder",
        "btn_delete_week": "🗑️ Delete Week",

        # Status Bar Messages
        "status_ready": "Ready",
        "status_saved": "Saved changes to {name}",
        "status_settings_saved": "Settings saved successfully.",
        "status_generating_tex": "Generating LaTeX for {name}...",
        "status_generated_tex": "Generated {filename} in {name}",
        "status_compiling_pdf": "Compiling LaTeX to PDF, please wait...",
        "status_pdf_success": "PDF compiled successfully! ✅",
        "status_pdf_failed": "Compilation failed with errors ❌",
        "status_folder_switched": "Switched reports directory to: {path}",

        # Settings Modal
        "settings_title": "Settings & Configuration",
        "settings_header": "Application Settings",
        "settings_sub": "Configure your default student details, directory paths, and compiler",
        "settings_language": "Language / Bahasa:",
        "settings_default_matric": "Default Matric Number:",
        "settings_course_code": "Course Code / Title:",
        "settings_student_name": "Student Name (Optional):",
        "settings_reports_dir": "Reports Output Directory:",
        "settings_compiler_path": "Custom pdflatex Path:",
        "settings_clean_aux": "Automatically clean auxiliary files (.aux, .log) after compile",
        "settings_browse": "📁 Browse...",
        "settings_open": "📂 Open",
        "settings_test": "🔍 Test",
        "settings_reset": "✕",
        "settings_btn_save": "Save Settings",
        "settings_btn_cancel": "Cancel",
        "compiler_detected": "✅ LaTeX Compiler Detected & Working",
        "compiler_not_detected": "⚠️ LaTeX Compiler Not Detected",
        "compiler_not_detected_desc": "pdflatex was not found. Please browse for your custom pdflatex.exe or download a TeX distribution:",
        "compiler_verified_title": "Compiler Verified",
        "compiler_verified_msg": "✅ pdflatex was successfully verified!\n\nVersion: {version}\nPath: {path}",
        "compiler_failed_title": "Compiler Test Failed",
        "compiler_failed_msg": "❌ Unable to run pdflatex at this location:\n{path}\n\nPlease check the path and make sure it points to pdflatex.exe.",

        # Directory Transfer Prompt
        "transfer_title": "Transfer Existing Reports?",
        "transfer_prompt": "The reports output directory has been changed.\n\nFrom:\n{old_dir}\n\nTo:\n{new_dir}\n\nWould you like to transfer (move) all your existing weekly reports ({count} item(s)) from the old directory to the new directory?",
        "transfer_success": "\n\nTransferred {folders} folder(s) and {files} file(s) to the new location.",
        "settings_saved_msg": "Configuration has been updated successfully!{transfer_msg}",

        # About Modal
        "about_title": "About - UMT Intern Report Manager",
        "about_header": "UMT Intern Report Manager",
        "about_sub": "Industrial Training e-Logbook Desktop Manager",
        "about_version": "Version:",
        "about_developer": "Developer:",
        "about_github": "GitHub:",
        "about_repo": "Repository:",
        "about_license": "License:",
        "about_license_val": "MIT Open Source License (2026)",
        "about_close": "Close",

        # Dialogs / Popups
        "dialog_confirm_delete_title": "Delete Week Folder",
        "dialog_confirm_delete_msg": "Are you sure you want to permanently delete:\n'{name}'?\n\nThis will remove all draft data, LaTeX source files, and generated PDFs inside this folder.",
        "dialog_create_week_title": "Create New Week Report",
        "dialog_create_week_prompt": "Enter week folder name (e.g. 'Week 1 Log'):",
        "dialog_rename_title": "Rename Week Folder",
        "dialog_rename_prompt": "Enter new folder name for '{old_name}':",
        "dialog_pdf_success_title": "Compilation Successful",
        "dialog_pdf_success_msg": "{pdf_name} was generated successfully!\n\nWould you like to open the PDF now?",
        "dialog_pdf_not_found_title": "PDF Not Found",
        "dialog_pdf_not_found_msg": "{pdf_name} has not been compiled yet.\nClick '🚀 Compile PDF' to generate it.",
        "dialog_latex_missing_title": "LaTeX Compiler Required",
        "dialog_latex_missing_msg": "To compile PDF reports directly from the app, pdflatex compiler is required.",
    },

    "ms": {
        # App Branding & Sidebar
        "app_title": "Pengurus Laporan Praktikal UMT (IRP)",
        "app_sub": "Buku Log Elektronik Latihan Industri",
        "create_new_week": "+ Cipta Minggu Baru",
        "reports_header": "LAPORAN",
        "settings": "⚙️ Tetapan",
        "refresh": "🔄 Muat Semula",
        "about": "ℹ️ Tentang",
        "no_reports": "Tiada laporan mingguan dijumpai.\nKlik '+ Cipta Minggu Baru' untuk mula!",
        "has_tex": "LaTeX sedia",
        "has_pdf": "PDF dikompil",

        # Header Info Card
        "week_number": "Nombor Minggu:",
        "week_placeholder": "cth., 1",
        "date_from": "Tarikh Mula:",
        "date_to": "Tarikh Akhir:",
        "date_format_hint": "HH/BB/TTTT",
        "matric_no": "Nombor Matrik:",
        "matric_hint": "cth., S70012",
        "course_title": "Tajuk / Kod Kursus:",
        "pick_date": "📅 Pilih",
        "calc_to_date": "⚡ Set Minggu 5-Hari",

        # Section 1: Attendance
        "sec_attendance": "Kehadiran Harian & Status Cuti",
        "sec_attendance_sub": "Tandakan hari anda hadir atau pilih status cuti/MC/cuti umum",
        "status_present": "Hadir",
        "status_mc": "MC (Cuti Sakit)",
        "status_holiday": "Cuti Umum",
        "status_leave": "Cuti Rehat",
        "status_absent": "Tidak Hadir",

        # Section 2: Daily Activities
        "sec_activities": "Aktiviti Harian & Ringkasan Tugasan",
        "sec_activities_sub": "Urus catatan buku log harian, tarikh dan senarai aktiviti",
        "add_day": "+ Tambah Hari",
        "delete_day": "✕ Padam Hari",
        "add_activity_bullet": "+ Tambah Aktiviti",
        "activity_placeholder": "Masukkan tugas, aktiviti atau hasil kerja yang disiapkan pada hari ini...",
        "day_label_default": "HH/BB/TTTT (Isnin)",

        # Section 3: Knowledge & Skills Gained
        "sec_skills": "Pengetahuan & Kemahiran yang Diperoleh",
        "sec_skills_sub": "Kemahiran teknikal, peralatan, kemahiran insaniah atau ilmu yang diperoleh minggu ini",
        "add_skill_bullet": "+ Tambah Kemahiran",
        "skill_placeholder": "cth., Memperoleh pengalaman praktikal dalam seni bina sistem dan pengoptimuman backend...",

        # Section 4: Problems / Comments / Observations
        "sec_problems": "Masalah yang Dihadapi, Komen & Pemerhatian",
        "sec_problems_sub": "Cabaran yang dihadapi, penyelesaian masalah, maklum balas atau catatan umum",
        "add_problem_bullet": "+ Tambah Komen / Masalah",
        "problem_placeholder": "cth., Menghadapi isu kecil semasa pemasangan, berjaya diselesaikan selepas merujuk dokumentasi...",

        # Action Bar Buttons
        "btn_save_draft": "💾 Simpan Draf (Ctrl+S)",
        "btn_generate_latex": "⚡ Jana LaTeX",
        "btn_compile_pdf": "🚀 Kompil PDF",
        "btn_view_pdf": "📄 Lihat PDF",
        "btn_open_folder": "📂 Buka Folder",
        "btn_rename_week": "✏️ Namakan Semula",
        "btn_delete_week": "🗑️ Padam Minggu",

        # Status Bar Messages
        "status_ready": "Sedia",
        "status_saved": "Perubahan berjaya disimpan ke {name}",
        "status_settings_saved": "Tetapan berjaya disimpan.",
        "status_generating_tex": "Menjana LaTeX untuk {name}...",
        "status_generated_tex": "Berjaya menjana {filename} dalam {name}",
        "status_compiling_pdf": "Sedang mengompil LaTeX ke PDF, sila tunggu...",
        "status_pdf_success": "PDF berjaya dikompil! ✅",
        "status_pdf_failed": "Kompilasi gagal dengan ralat ❌",
        "status_folder_switched": "Menukar direktori laporan ke: {path}",

        # Settings Modal
        "settings_title": "Tetapan & Konfigurasi",
        "settings_header": "Tetapan Aplikasi",
        "settings_sub": "Konfigurasikan butiran pelajar lalai, direktori kerja dan pengkompil LaTeX",
        "settings_language": "Bahasa / Language:",
        "settings_default_matric": "Nombor Matrik Lalai:",
        "settings_course_code": "Kod / Tajuk Kursus:",
        "settings_student_name": "Nama Pelajar (Pilihan):",
        "settings_reports_dir": "Direktori Output Laporan:",
        "settings_compiler_path": "Lokasi Khas pdflatex:",
        "settings_clean_aux": "Padam fail sampingan (.aux, .log) secara automatik selepas kompil",
        "settings_browse": "📁 Layari...",
        "settings_open": "📂 Buka",
        "settings_test": "🔍 Uji",
        "settings_reset": "✕",
        "settings_btn_save": "Simpan Tetapan",
        "settings_btn_cancel": "Batal",
        "compiler_detected": "✅ Pengkompil LaTeX Dikesan & Berfungsi",
        "compiler_not_detected": "⚠️ Pengkompil LaTeX Tidak Dikesan",
        "compiler_not_detected_desc": "pdflatex tidak dijumpai. Sila cari pdflatex.exe anda atau muat turun pengedaran TeX:",
        "compiler_verified_title": "Pengkompil Disahkan",
        "compiler_verified_msg": "✅ pdflatex berjaya disahkan!\n\nVersi: {version}\nLokasi: {path}",
        "compiler_failed_title": "Ujian Pengkompil Gagal",
        "compiler_failed_msg": "❌ Gagal menjalankan pdflatex di lokasi ini:\n{path}\n\nSila pastikan laluan menunjuk ke fail pdflatex.exe yang sah.",

        # Directory Transfer Prompt
        "transfer_title": "Pindahkan Laporan Sedia Ada?",
        "transfer_prompt": "Direktori output laporan telah diubah.\n\nDaripada:\n{old_dir}\n\nKepada:\n{new_dir}\n\nAdakah anda mahu memindahkan semua laporan mingguan sedia ada ({count} item) ke direktori baru?",
        "transfer_success": "\n\nBerjaya memindahkan {folders} folder dan {files} fail ke lokasi baru.",
        "settings_saved_msg": "Konfigurasi telah berjaya dikemas kini!{transfer_msg}",

        # About Modal
        "about_title": "Tentang - Pengurus Laporan Praktikal UMT",
        "about_header": "Pengurus Laporan Praktikal UMT",
        "about_sub": "Buku Log Elektronik Latihan Industri Desktop",
        "about_version": "Versi:",
        "about_developer": "Pembangun:",
        "about_github": "GitHub:",
        "about_repo": "Repositori:",
        "about_license": "Lesen:",
        "about_license_val": "Lesen Sumber Terbuka MIT (2026)",
        "about_close": "Tutup",

        # Dialogs / Popups
        "dialog_confirm_delete_title": "Padam Folder Minggu",
        "dialog_confirm_delete_msg": "Adakah anda pasti mahu memadam secara kekal:\n'{name}'?\n\nIni akan memadam semua data draf, fail sumber LaTeX dan PDF dalam folder ini.",
        "dialog_create_week_title": "Cipta Laporan Minggu Baru",
        "dialog_create_week_prompt": "Masukkan nama folder minggu (cth. 'Week 1 Log'):",
        "dialog_rename_title": "Namakan Semula Folder Minggu",
        "dialog_rename_prompt": "Masukkan nama baru untuk folder '{old_name}':",
        "dialog_pdf_success_title": "Kompilasi Berjaya",
        "dialog_pdf_success_msg": "{pdf_name} berjaya dijana!\n\nAdakah anda mahu membuka PDF sekarang?",
        "dialog_pdf_not_found_title": "PDF Tidak Dijumpai",
        "dialog_pdf_not_found_msg": "{pdf_name} belum dikompil.\nKlik '🚀 Kompil PDF' untuk menjananya.",
        "dialog_latex_missing_title": "Pengkompil LaTeX Diperlukan",
        "dialog_latex_missing_msg": "Untuk mengompil laporan PDF terus dari aplikasi, pengkompil pdflatex diperlukan.",
    }
}

def set_language(lang: str) -> None:
    """Sets the active application language ('en' or 'ms')."""
    global _CURRENT_LANG
    if lang in TRANSLATIONS:
        _CURRENT_LANG = lang
    else:
        _CURRENT_LANG = "en"

def get_language() -> str:
    """Returns the current active language code ('en' or 'ms')."""
    return _CURRENT_LANG

def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Translates a key into the active or specified language with optional formatting.
    Falls back to English if key is missing in target language.
    """
    target_lang = lang or _CURRENT_LANG
    lang_dict = TRANSLATIONS.get(target_lang, TRANSLATIONS["en"])
    text = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
