# Intern Report App (IRP) - e-Logbook Manager

A desktop management and automation system for weekly industrial training logbooks at Universiti Malaysia Terengganu (UMT).

The application provides a graphical user interface to fill out daily activities, track attendance, record knowledge and skills gained, manage problem statements, and automatically compile structured LaTeX documents into publication-ready PDF reports.

---

## Key Features

- **Automated Directory Management**: Creates and organizes weekly report folders inside the `Report/` directory with automatic asset provisioning (`img/UMT Logo.png`).
- **Interactive Form Interface**:
  - Document metadata fields (Week number, Date range, Matric number, Course title).
  - Daily attendance grid with interactive checkboxes and status selectors (Present, MC, Public Holiday, Leave, Absent).
  - Dynamic daily activity timeline cards with date pickers, task items, and day management.
  - Bullet-point sections for knowledge gained and problem statements/comments.
  - Interactive calendar popups for quick date selection with automatic day calculation.
- **Bilingual Internationalization (i18n)**:
  - Full support for **English** and **Bahasa Melayu**.
  - Dynamic language switching inside Settings that refreshes all UI elements, day cards, attendance statuses, and dialogs in real-time without restarting.
- **Automated LaTeX Engine**:
  - Automatically formats input data into LaTeX code matching the official UMT `modernbox` and `timelinebox` template style.
  - Escapes LaTeX special characters (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `\`, `~`, `^`) to prevent compilation errors.
- **One-Click PDF Compilation**:
  - Integrates with `pdflatex` to build PDF documents directly from the interface.
  - Background process execution with zero terminal window popups or interruptions.
  - Automatic cleanup of LaTeX auxiliary files (`.aux`, `.log`, `.out`, `.synctex.gz`, `.toc`).
- **Compiler Health Diagnostics**:
  - Automatic detection of LaTeX distributions across Windows, macOS, and Linux.
  - Custom compiler path configuration with file browser and live verification testing.
  - Direct download guidance when a compiler is missing.
- **Custom Workspace Directory & Migration**:
  - Configurable reports output directory allowing users to store logbooks anywhere on their computer.
  - Automatic transfer and merge prompt to safely migrate existing weekly logbooks when changing the directory.
- **Flat-File JSON Storage**:
  - Saves report drafts as `report_data.json` inside each week's folder, allowing revisions at any time without database dependencies.
- **Standalone Portable Executable (Windows)**:
  - Prepackaged `.exe` available for Windows with zero Python dependencies required.

---

## System Requirements

### Supported Operating Systems
- **Windows**: Windows 10 or Windows 11 (64-bit) — Standalone `.exe` or running from source.
- **macOS (Apple)**: macOS 11 (Big Sur) or higher — Running from source.
- **Linux**: Ubuntu, Debian, Fedora, Arch Linux, etc. — Running from source.

### LaTeX Compiler (Required for PDF compilation)
To compile PDF reports, one of the following LaTeX distributions is recommended:
- **Windows**: [MiKTeX](https://miktex.org/download) (Recommended) or [TeX Live](https://tug.org/texlive/)
- **macOS**: [MacTeX](https://www.tug.org/mactex/) or BasicTeX
- **Linux**: TeX Live (`sudo apt install texlive-latex-extra texlive-fonts-recommended`)

*Note: You can still use the app to create, edit, and generate `.tex` source files even if a compiler is not yet installed.*

---

## Quick Start

### Windows (Precompiled Executable)

1. Download the latest precompiled bundle: [InternReportApp-v1.0.0-windows-x64.zip](https://github.com/LurdK/UMT-Intern-Report-App-IRP-/releases/latest/download/InternReportApp-v1.0.0-windows-x64.zip) (or browse all versions on the [Releases](https://github.com/LurdK/UMT-Intern-Report-App-IRP-/releases) page).
2. Extract the zip file to your preferred folder.
3. Double-click `InternReportApp.exe` to launch the application.
4. Click **Create New Week** to start your first weekly report.
5. Fill in your activities and click **Compile PDF**.


---

### Running From Source (Windows, macOS, Linux)

#### Prerequisites
- Python 3.10 or higher
- Standard Tkinter library

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/LurdK/UMT-Intern-Report-App-IRP-.git
   cd UMT-Intern-Report-App-IRP-
   ```

2. (Linux users only) Ensure Tkinter is installed:
   ```bash
   # Debian / Ubuntu
   sudo apt install python3-tk

   # Fedora
   sudo dnf install python3-tkinter

   # Arch Linux
   sudo pacman -S tk
   ```

3. Launch the application:
   ```bash
   # Windows
   python main.py

   # macOS / Linux
   python3 main.py
   ```

---

## Building the Standalone Executable (.exe) on Windows

To package the application into a single portable binary using PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Execute the build script:
   ```bash
   build_exe.bat
   ```
   Or run the PyInstaller command manually:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name "InternReportApp" --distpath "Intern Report App" --icon="app_icon.ico" --add-data "Report Format;Report Format" --add-data "app_icon.png;." --add-data "app_icon.ico;." main.py
   ```

3. The generated executable will be placed in:
   ```
   Intern Report App/InternReportApp.exe
   ```

---

## Project Structure

```
Intern Report App (IRP)/
|-- Intern Report App/             # Distribution output folder
|   `-- InternReportApp.exe        # Standalone portable binary
|-- Report Format/                 # Master LaTeX template and logo assets
|   |-- img/
|   |   `-- UMT Logo.png
|   `-- report.tex
|-- Report/                        # Container for all generated weekly logbooks
|   |-- Week 1 Log/
|   |   |-- img/
|   |   |   `-- UMT Logo.png
|   |   |-- Week 1 Log.tex
|   |   |-- Week 1 Log.pdf
|   |   `-- report_data.json
|   `-- ...
|-- backend/                       # Core logic and services
|   |-- compiler.py                # pdflatex search, execution, and cleanup
|   |-- folder_manager.py          # Directory lifecycle, transfer, and asset healing
|   |-- i18n.py                    # Bilingual translation engine (English / Bahasa Melayu)
|   |-- latex_engine.py            # Data extraction and LaTeX code generation
|   `-- storage.py                 # JSON configuration and draft persistence
|-- ui/                            # Desktop user interface
|   |-- about_dialog.py            # About dialog component
|   |-- app.py                     # Main application window and layout
|   |-- date_picker.py             # Bilingual calendar dialog component
|   `-- settings_dialog.py         # Configuration and compiler setup modal
|-- app_icon.ico                   # Windows application icon
|-- app_icon.png                   # High-resolution application logo
|-- feather-icon.svg               # Vector brand source icon
|-- build_exe.bat                  # PyInstaller build automation script
|-- run_app.bat                    # Local execution script
|-- main.py                        # Application entry point
|-- config.json                    # User settings (auto-generated)
|-- LICENSE                        # MIT License
`-- README.md                      # Documentation
```

---

## Credits & Acknowledgements

- **Universiti Malaysia Terengganu (UMT)**: Faculty of Computer Science and Mathematics for the Industrial Training curriculum and logbook format.
- **LaTeX Community**: For the `tcolorbox`, `tabularx`, and `hyperref` packages used in the report formatting.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
