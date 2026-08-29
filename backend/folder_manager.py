import os
import re
import shutil
import subprocess
import sys
from typing import List, Dict, Optional

class FolderManager:
    def __init__(self, root_dir: str, custom_reports_dir: Optional[str] = None):
        self.root_dir = os.path.abspath(root_dir)
        self.set_reports_dir(custom_reports_dir)
        self.template_dir = self._resolve_template_path()

    def set_reports_dir(self, custom_reports_dir: Optional[str] = None):
        if custom_reports_dir and custom_reports_dir.strip():
            self.reports_dir = os.path.abspath(custom_reports_dir.strip())
        else:
            self.reports_dir = os.path.join(self.root_dir, "Report")
        os.makedirs(self.reports_dir, exist_ok=True)


    def _resolve_template_path(self) -> str:
        # 1. Local workspace "Report Format"
        local_path = os.path.join(self.root_dir, "Report Format")
        if os.path.exists(local_path) and os.path.isdir(local_path):
            return local_path

        # 2. Inside Report/Report Format
        in_rep = os.path.join(self.reports_dir, "Report Format")
        if os.path.exists(in_rep) and os.path.isdir(in_rep):
            return in_rep

        # 3. PyInstaller bundled resources (_MEIPASS)
        if hasattr(sys, "_MEIPASS"):
            bundled_path = os.path.join(sys._MEIPASS, "Report Format")
            if os.path.exists(bundled_path) and os.path.isdir(bundled_path):
                return bundled_path

        # 4. Relative to script directory
        module_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = os.path.abspath(os.path.join(module_dir, "..", "Report Format"))
        if os.path.exists(rel_path) and os.path.isdir(rel_path):
            return rel_path

        return local_path

    def get_template_path(self) -> str:
        return self.template_dir

    def template_exists(self) -> bool:
        src = self._resolve_template_path()
        return os.path.exists(src) and os.path.isdir(src)

    @staticmethod
    def get_tex_path(folder_path: str) -> str:
        folder_name = os.path.basename(folder_path)
        named_tex = os.path.join(folder_path, f"{folder_name}.tex")
        legacy_tex = os.path.join(folder_path, "report.tex")
        if os.path.exists(named_tex):
            return named_tex
        if os.path.exists(legacy_tex):
            return legacy_tex
        return named_tex

    @staticmethod
    def get_pdf_path(folder_path: str) -> str:
        folder_name = os.path.basename(folder_path)
        named_pdf = os.path.join(folder_path, f"{folder_name}.pdf")
        legacy_pdf = os.path.join(folder_path, "report.pdf")
        if os.path.exists(named_pdf):
            return named_pdf
        if os.path.exists(legacy_pdf):
            return legacy_pdf
        return named_pdf

    def ensure_week_assets(self, week_folder_path: str) -> None:
        """
        Ensures that the week directory has all required assets, including
        the 'img/UMT Logo.png' image file needed for compilation.
        """
        if not os.path.exists(week_folder_path):
            return

        img_dir = os.path.join(week_folder_path, "img")
        os.makedirs(img_dir, exist_ok=True)
        target_logo = os.path.join(img_dir, "UMT Logo.png")

        if not os.path.exists(target_logo):
            candidate_dirs = [
                os.path.join(self.template_dir, "img"),
                os.path.join(self.root_dir, "Report Format", "img"),
                os.path.join(self.reports_dir, "Report Format", "img"),
            ]
            if hasattr(sys, "_MEIPASS"):
                candidate_dirs.insert(0, os.path.join(sys._MEIPASS, "Report Format", "img"))
                candidate_dirs.insert(0, os.path.join(sys._MEIPASS, "img"))

            # Also check any other week folders
            if os.path.exists(self.reports_dir):
                for entry in os.listdir(self.reports_dir):
                    candidate_dirs.append(os.path.join(self.reports_dir, entry, "img"))
            if os.path.exists(self.root_dir):
                for entry in os.listdir(self.root_dir):
                    candidate_dirs.append(os.path.join(self.root_dir, entry, "img"))

            found_src = None
            for c_dir in candidate_dirs:
                if c_dir and os.path.exists(c_dir):
                    candidate_file = os.path.join(c_dir, "UMT Logo.png")
                    if os.path.exists(candidate_file):
                        found_src = candidate_file
                        break

            if found_src:
                try:
                    shutil.copy2(found_src, target_logo)
                except Exception:
                    pass

    def list_week_folders(self) -> List[Dict[str, any]]:
        """
        Scans Report/ directory (and root directory for backward compatibility)
        for weekly folders. Returns sorted list.
        """
        os.makedirs(self.reports_dir, exist_ok=True)
        weeks = []
        pattern = re.compile(r"^Week\s*(\d+)", re.IGNORECASE)

        # Helper to process a directory
        def scan_dir(target_dir: str):
            if not os.path.exists(target_dir):
                return
            for entry in os.listdir(target_dir):
                entry_path = os.path.join(target_dir, entry)
                if os.path.isdir(entry_path) and entry not in ("Report Format", "Report", "build", "dist", "Intern Report App", ".git", ".agents", "__pycache__") and not entry.startswith("."):
                    match = pattern.search(entry)
                    week_num = int(match.group(1)) if match else 999
                    
                    # Auto-heal missing assets in any week folder
                    self.ensure_week_assets(entry_path)

                    tex_file = self.get_tex_path(entry_path)
                    pdf_file = self.get_pdf_path(entry_path)
                    
                    weeks.append({
                        "name": entry,
                        "week_num": week_num,
                        "path": entry_path,
                        "has_tex": os.path.exists(tex_file),
                        "has_pdf": os.path.exists(pdf_file)
                    })

        # Scan Report/ folder
        scan_dir(self.reports_dir)

        # Also check root folder if empty in Report
        if not weeks:
            scan_dir(self.root_dir)

        # Sort naturally by week number then name
        weeks.sort(key=lambda x: (x["week_num"], x["name"]))
        return weeks

    def get_next_week_number(self) -> int:
        weeks = self.list_week_folders()
        if not weeks:
            return 1
        valid_nums = [w["week_num"] for w in weeks if w["week_num"] != 999]
        if not valid_nums:
            return len(weeks) + 1
        return max(valid_nums) + 1

    def create_week_folder(self, folder_name: Optional[str] = None, week_num: Optional[int] = None) -> str:
        """
        Creates a new week directory inside Report/ by copying the master template.
        The main .tex file is created as <folder_name>.tex.
        """
        if week_num is None:
            week_num = self.get_next_week_number()

        if not folder_name or not folder_name.strip():
            folder_name = f"Week {week_num} Log"
        else:
            folder_name = folder_name.strip()

        os.makedirs(self.reports_dir, exist_ok=True)
        target_path = os.path.join(self.reports_dir, folder_name)

        if os.path.exists(target_path):
            raise FileExistsError(f"Folder '{folder_name}' already exists in Report.")

        src_template = self._resolve_template_path()
        if os.path.exists(src_template) and os.path.isdir(src_template):
            shutil.copytree(src_template, target_path)
            
            # If report.tex exists from template, rename it to <folder_name>.tex
            old_tex = os.path.join(target_path, "report.tex")
            new_tex = os.path.join(target_path, f"{folder_name}.tex")
            if os.path.exists(old_tex):
                try:
                    os.rename(old_tex, new_tex)
                except Exception:
                    pass

            # Clean any old build artifacts
            for f in os.listdir(target_path):
                if f.endswith((".aux", ".log", ".out", ".synctex.gz", ".pdf")):
                    try:
                        os.remove(os.path.join(target_path, f))
                    except Exception:
                        pass
        else:
            os.makedirs(target_path, exist_ok=True)

        self.ensure_week_assets(target_path)
        return target_path


    def rename_week_folder(self, current_folder_path: str, new_name: str) -> str:
        """
        Renames an existing week folder and renames the .tex and .pdf files inside it.
        """
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Folder name cannot be empty.")

        parent_dir = os.path.dirname(os.path.abspath(current_folder_path))
        new_folder_path = os.path.join(parent_dir, new_name)

        if os.path.exists(new_folder_path) and new_folder_path != current_folder_path:
            raise FileExistsError(f"A folder named '{new_name}' already exists.")

        old_folder_name = os.path.basename(current_folder_path)

        # 1. Rename files inside if they match old folder name
        old_tex = os.path.join(current_folder_path, f"{old_folder_name}.tex")
        if not os.path.exists(old_tex):
            old_tex = os.path.join(current_folder_path, "report.tex")
        
        old_pdf = os.path.join(current_folder_path, f"{old_folder_name}.pdf")
        if not os.path.exists(old_pdf):
            old_pdf = os.path.join(current_folder_path, "report.pdf")

        new_tex_target = os.path.join(current_folder_path, f"{new_name}.tex")
        new_pdf_target = os.path.join(current_folder_path, f"{new_name}.pdf")

        if os.path.exists(old_tex) and old_tex != new_tex_target:
            try:
                os.rename(old_tex, new_tex_target)
            except Exception:
                pass

        if os.path.exists(old_pdf) and old_pdf != new_pdf_target:
            try:
                os.rename(old_pdf, new_pdf_target)
            except Exception:
                pass

        # 2. Rename the directory itself
        if current_folder_path != new_folder_path:
            os.rename(current_folder_path, new_folder_path)

        return new_folder_path

    @staticmethod
    def open_in_explorer(path: str) -> None:
        path = os.path.abspath(path)
        if sys.platform == "win32":
            if os.path.isfile(path):
                subprocess.Popen(f'explorer /select,"{path}"')
            else:
                subprocess.Popen(f'explorer "{path}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    @staticmethod
    def open_file_default(file_path: str) -> None:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            return
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", file_path])
        else:
            subprocess.Popen(["xdg-open", file_path])
