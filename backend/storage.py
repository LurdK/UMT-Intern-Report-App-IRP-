import json
import os
from typing import Dict, Any, List

DEFAULT_CONFIG: Dict[str, Any] = {
    "matric_no": "S70012",
    "course_code": "CSF4992 / CSF49712 INDUSTRIAL TRAINING",
    "student_name": "",
    "custom_pdflatex_path": "",
    "custom_reports_dir": "",
    "auto_clean_aux": True,
    "language": "en",
    "theme": "light"
}



def get_config_path(base_dir: str) -> str:
    return os.path.join(base_dir, "config.json")

def load_config(base_dir: str) -> Dict[str, Any]:
    config_path = get_config_path(base_dir)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    else:
        save_config(base_dir, DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(base_dir: str, config: Dict[str, Any]) -> None:
    config_path = get_config_path(base_dir)
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_report_data_path(week_folder_path: str) -> str:
    return os.path.join(week_folder_path, "report_data.json")

def normalize_attendance_data(att_raw: Any) -> List[Dict[str, Any]]:
    """
    Normalizes attendance into a list of day objects:
    [{"label": "Day 1", "status": "present", "checked": True}, ...]
    Handles both list format and legacy dict format.
    """
    if isinstance(att_raw, list):
        normalized = []
        for i, item in enumerate(att_raw):
            label = item.get("label", f"Day {i+1}")
            status = item.get("status", "present")
            checked = item.get("checked", (status == "present"))
            normalized.append({
                "label": label,
                "status": status,
                "checked": checked
            })
        return normalized if normalized else get_default_attendance()
    elif isinstance(att_raw, dict):
        normalized = []
        # Sort keys day1, day2...
        keys = sorted(att_raw.keys(), key=lambda k: int(k.replace("day", "")) if k.replace("day", "").isdigit() else 99)
        for i, k in enumerate(keys):
            item = att_raw[k]
            label = f"Day {i+1}"
            status = item.get("status", "present")
            checked = item.get("checked", (status == "present"))
            normalized.append({
                "label": label,
                "status": status,
                "checked": checked
            })
        return normalized if normalized else get_default_attendance()
    else:
        return get_default_attendance()

def get_default_attendance() -> List[Dict[str, Any]]:
    return [
        {"label": "Day 1", "status": "present", "checked": True},
        {"label": "Day 2", "status": "present", "checked": True},
        {"label": "Day 3", "status": "present", "checked": True},
        {"label": "Day 4", "status": "present", "checked": True},
        {"label": "Day 5", "status": "present", "checked": True}
    ]

def load_week_data(week_folder_path: str, default_matric: str = "S70012") -> Dict[str, Any]:
    data_path = get_report_data_path(week_folder_path)
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["attendance"] = normalize_attendance_data(data.get("attendance"))
                return data
        except Exception:
            pass
    return get_default_week_data(default_matric)

def save_week_data(week_folder_path: str, data: Dict[str, Any]) -> None:
    data_path = get_report_data_path(week_folder_path)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_default_week_data(default_matric: str = "S70012") -> Dict[str, Any]:
    return {
        "week_num": "1",
        "date_from": "",
        "date_to": "",
        "matric_no": default_matric,
        "course_code": "CSF4992 / CSF49712 INDUSTRIAL TRAINING",
        "attendance": get_default_attendance(),
        "daily_activities": [
            {
                "date_label": "DD/MM/YYYY (Monday)",
                "items": ["Attended daily briefing and assigned tasks.", "Worked on initial setup and development."]
            },
            {
                "date_label": "DD/MM/YYYY (Tuesday)",
                "items": ["Continued task implementation.", "Tested module functionality."]
            },
            {
                "date_label": "DD/MM/YYYY (Wednesday)",
                "items": ["Collaborated with team on feature integration."]
            },
            {
                "date_label": "DD/MM/YYYY (Thursday)",
                "items": ["Code review and refactoring."]
            },
            {
                "date_label": "DD/MM/YYYY (Friday)",
                "items": ["Documented weekly progress and finalized deliverables."]
            }
        ],
        "skills_gained": [
            "Gained practical experience with system architecture.",
            "Improved problem solving and debugging skills."
        ],
        "problems_comments": [
            "Encountered minor issues during deployment, successfully resolved with team guidance."
        ]
    }
