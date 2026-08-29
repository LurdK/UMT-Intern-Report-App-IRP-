# Intern Report App (IRP) - e-Logbook Manager

A desktop management and automation system for weekly industrial training logbooks (CSF4992 / CSF49712 Industrial Training) at Universiti Malaysia Terengganu (UMT).

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
- **Automated LaTeX Engine**:
  - Automatically formats input data into LaTeX code matching the official UMT `modernbox` and `timelinebox` template style.
  - Escapes LaTeX special characters (`&`, `%`, `$`, `#`, `_`, `{`, `}`, `\`, `~`, `^`) to prevent compilation errors.
- **One-Click PDF Compilation**:
  - Integrates with `pdflatex` to build PDF documents directly from the interface.
  - Background process execution with zero terminal window popups or interruptions.
  - Automatic cleanup of LaTeX auxiliary files (`.aux`, `.log`, `.out`, `.synctex.gz`, `.toc`).
- **Compiler Health Diagnostics**:
  - Automatic detection of LaTeX distributions (MiKTeX and TeX Live) from system PATH, registry, and standard Windows directories.
  - Custom compiler path configuration with file browser and live verification testing.
  - Direct download guidance when a compiler is missing.
- **Flat-File JSON Storage**:
  - Saves report drafts as `report_data.json` inside each week's folder, allowing revisions at any time without database dependencies.
- **Single Portable Executable**:
  - Can be packaged into a standalone `.exe` that runs without requiring Python installed on the target machine.

---

## System Requirements

### Operating System
- Windows 10 or Windows 11 (64-bit)

### LaTeX Compiler (Required for PDF compilation)
To compile PDF reports, one of the following LaTeX distributions must be installed:
- **MiKTeX**: https://miktex.org/download (Recommended)
- **TeX Live**: https://tug.org/texlive/windows.html

*Note: You can still use the app to create, edit, and generate `.tex` source files even if a compiler is not yet installed.*

---

## Quick Start (For End Users)

1. Download the latest `InternReportApp.exe` from the GitHub **Releases** page.
2. Place `InternReportApp.exe` into your desired working directory.
3. Double-click `InternReportApp.exe` to launch the application.
4. Click **Create New Week** to start your first weekly report.
5. Fill in your weekly activities and click **Compile PDF**.

---

## Development Setup (Running From Source)

### Prerequisites
- Python 3.10 or higher
- Standard Tkinter library (included with official Python Windows installers)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/intern-report-app.git
   cd intern-report-app
   ```

2. Run the application directly:
   ```bash
   python main.py
   ```
   Or double-click `run_app.bat`.

---

## Building the Standalone Executable (.exe)

To bundle the application into a single portable binary using PyInstaller:

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
   pyinstaller --noconfirm --onefile --windowed --name "InternReportApp" --distpath "Intern Report App" --add-data "Report Format;Report Format" main.py
   ```

3. The generated executable will be available at:
   ```
   Intern Report App/InternReportApp.exe
   ```


---

## Project Structure

```
Intern Report App (IRP)/
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
|   |-- folder_manager.py          # Directory lifecycle and asset healing
|   |-- latex_engine.py            # Data extraction and LaTeX code generation
|   `-- storage.py                 # JSON configuration and draft persistence
|-- ui/                            # Desktop user interface
|   |-- app.py                     # Main application window and layout
|   |-- date_picker.py             # Calendar dialog component
|   `-- settings_dialog.py         # Configuration and compiler setup modal
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
- **Google Antigravity**: For agentic pair programming and assistance in designing and implementing the application.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
