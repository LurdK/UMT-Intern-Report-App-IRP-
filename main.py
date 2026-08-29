import os
import sys
import ctypes

def enable_high_dpi():
    if sys.platform == "win32":
        try:
            # Set DPI awareness for crisp font rendering
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def get_base_dir() -> str:
    # If running as PyInstaller bundled executable
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Otherwise standard script directory
    return os.path.dirname(os.path.abspath(__file__))

def main():
    enable_high_dpi()
    base_dir = get_base_dir()
    
    # Import and run app
    from ui.app import InternReportApp
    app = InternReportApp(workspace_dir=base_dir)
    app.mainloop()

if __name__ == "__main__":
    main()
