import os
import shutil
import subprocess
import sys
from typing import Tuple, Optional, Dict, Any

MIKTEX_URL = "https://miktex.org/download"
TEXLIVE_URL = "https://tug.org/texlive/windows.html"

def find_pdflatex(custom_path: Optional[str] = None) -> Optional[str]:
    """
    Searches for the pdflatex executable.
    Checks custom path, system PATH, and common Windows install directories.
    """
    # 1. Custom path
    if custom_path and os.path.isfile(custom_path) and os.access(custom_path, os.X_OK):
        return custom_path

    # 2. System PATH
    found = shutil.which("pdflatex")
    if found:
        return found

    # 3. Known Windows directories
    known_paths = [
        r"C:\texlive\2026\bin\windows\pdflatex.exe",
        r"C:\texlive\2025\bin\windows\pdflatex.exe",
        r"C:\texlive\2024\bin\windows\pdflatex.exe",
        r"C:\texlive\2023\bin\windows\pdflatex.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\MiKTeX\miktex\bin\x64\pdflatex.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\MiKTeX\miktex\bin\pdflatex.exe"),
    ]

    for p in known_paths:
        if os.path.isfile(p):
            return p

    return None

def get_subprocess_window_flags():
    """
    Returns (startupinfo, creationflags) configured to completely suppress
    any command prompt/terminal windows from flashing on Windows.
    """
    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return startupinfo, creationflags

def check_latex_environment(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Checks if LaTeX compiler is available and returns diagnostics without flashing a console window.
    """
    compiler_path = find_pdflatex(custom_path)
    if compiler_path:
        try:
            startupinfo, creationflags = get_subprocess_window_flags()
            res = subprocess.run(
                [compiler_path, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            first_line = res.stdout.splitlines()[0] if res.stdout else "pdflatex available"
            return {
                "available": True,
                "path": compiler_path,
                "version": first_line,
                "error": None
            }
        except Exception as e:
            return {
                "available": True,
                "path": compiler_path,
                "version": "pdflatex",
                "error": str(e)
            }
    else:
        return {
            "available": False,
            "path": None,
            "version": None,
            "error": "pdflatex compiler was not found on your system.",
            "miktex_url": MIKTEX_URL,
            "texlive_url": TEXLIVE_URL
        }

def clean_auxiliary_files(week_folder_path: str) -> None:
    """
    Removes temporary LaTeX build files (.aux, .log, .out, .synctex.gz).
    """
    folder_name = os.path.basename(week_folder_path)
    base_names = [folder_name, "report"]
    extensions = [".aux", ".log", ".out", ".synctex.gz", ".toc"]
    for base in base_names:
        for ext in extensions:
            file_path = os.path.join(week_folder_path, f"{base}{ext}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

def compile_pdf(week_folder_path: str, custom_path: Optional[str] = None, clean_aux: bool = False) -> Tuple[bool, str, str]:
    """
    Compiles <folder_name>.tex in week_folder_path into <folder_name>.pdf using pdflatex.
    Returns: (success: bool, output_message: str, pdf_path: str)
    """
    from backend.folder_manager import FolderManager
    # Ensure assets (like img/UMT Logo.png) are present in the folder before compiling
    try:
        parent_dir = os.path.dirname(os.path.abspath(week_folder_path))
        FolderManager(parent_dir).ensure_week_assets(week_folder_path)
    except Exception:
        pass

    compiler_path = find_pdflatex(custom_path)
    if not compiler_path:
        return (
            False,
            f"pdflatex compiler not found!\n\nPlease install MiKTeX ({MIKTEX_URL}) or TeX Live ({TEXLIVE_URL}) to compile PDFs.",
            ""
        )

    folder_name = os.path.basename(week_folder_path)
    tex_filename = f"{folder_name}.tex"
    tex_file = os.path.join(week_folder_path, tex_filename)
    if not os.path.exists(tex_file):
        # Fallback to report.tex
        legacy_tex = os.path.join(week_folder_path, "report.tex")
        if os.path.exists(legacy_tex):
            tex_file = legacy_tex
            tex_filename = "report.tex"
        else:
            return False, f"File not found: {tex_file}", ""

    pdf_filename = f"{folder_name}.pdf" if tex_filename == f"{folder_name}.tex" else "report.pdf"
    pdf_file = os.path.join(week_folder_path, pdf_filename)

    # Run pdflatex in target directory
    cmd = [compiler_path, "-interaction=nonstopmode", tex_filename]

    try:
        startupinfo, creationflags = get_subprocess_window_flags()

        # First pass
        proc = subprocess.run(
            cmd,
            cwd=week_folder_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        # Second pass (for tcolorbox layout stability and form checkboxes)
        if proc.returncode == 0:
            subprocess.run(
                cmd,
                cwd=week_folder_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
                startupinfo=startupinfo,
                creationflags=creationflags
            )


        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
            if clean_aux:
                clean_auxiliary_files(week_folder_path)
            return True, "PDF compiled successfully!", pdf_file
        else:
            return False, f"LaTeX Compilation finished with errors:\n\n{proc.stdout[-1500:]}", ""

    except subprocess.TimeoutExpired:
        return False, "LaTeX Compilation timed out (exceeded 45 seconds).", ""
    except Exception as e:
        return False, f"Error running LaTeX compiler: {str(e)}", ""

