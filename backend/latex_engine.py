import os
import re
from typing import Dict, Any, List
from backend.storage import normalize_attendance_data

def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters in user input to prevent compilation errors.
    """
    if not text:
        return ""
    
    # Mapping of special characters
    special_chars = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    # Process backslash first
    result = str(text).replace('\\', special_chars['\\'])
    for char, replacement in special_chars.items():
        if char != '\\':
            result = result.replace(char, replacement)
    
    return result

def format_attendance_cell(day_key: str, att_data: Dict[str, Any]) -> str:
    """
    Formats the attendance cell for a given day (e.g. Day 1).
    att_data format: {"label": "Day 1", "status": "present"|"mc"|"holiday"|"leave"|"absent", "checked": bool}
    """
    status = att_data.get("status", "present").lower()
    is_checked = att_data.get("checked", True)

    if status == "present":
        checked_str = ",checked=true" if is_checked else ""
        return f"\\CheckBox[name={day_key},width=1em,height=1em{checked_str}]{{}} Present"
    elif status == "mc":
        return r"\textbf{MC}"
    elif status == "holiday":
        return r"\textbf{Public Holiday}"
    elif status == "leave":
        return r"\textbf{Leave}"
    elif status == "absent":
        return r"\textbf{Absent}"
    else:
        return r"\textbf{" + escape_latex(str(status)) + r"}"

def generate_latex_content(data: Dict[str, Any]) -> str:
    """
    Generates the complete report.tex string matching the exact UMT e-Logbook template.
    """
    week_num = escape_latex(str(data.get("week_num", "1")))
    date_from = escape_latex(str(data.get("date_from", "")))
    dateto = escape_latex(str(data.get("date_to", "")))
    matricno = escape_latex(str(data.get("matric_no", "S70012")))
    course_code = escape_latex(str(data.get("course_code", "CSF4992 / CSF49712 INDUSTRIAL TRAINING")))

    # Attendance table generation
    att_raw = data.get("attendance", [])
    att_list = normalize_attendance_data(att_raw)
    if not att_list:
        att_list = [{"label": f"Day {i+1}", "status": "present", "checked": True} for i in range(5)]

    col_count = len(att_list)
    header_cols = " & ".join(f"\\textbf{{{escape_latex(d.get('label', f'Day {i+1}'))}}}" for i, d in enumerate(att_list))
    cell_cols = " & \n    ".join(format_attendance_cell(f"day{i+1}", d) for i, d in enumerate(att_list))

    attendance_table = f"""\\begin{{tabularx}}{{\\textwidth}}{{@{{}} *{{{col_count}}}{{X}} @{{}}}}
    \\toprule
    {header_cols} \\\\
    \\midrule
    {cell_cols} \\\\
    \\bottomrule
\\end{{tabularx}}"""

    # Daily timeline boxes
    timeline_boxes = []
    activities = data.get("daily_activities", [])
    for act in activities:
        date_label = escape_latex(act.get("date_label", ""))
        items = act.get("items", [])
        if not items:
            item_latex = "        \\item % No activity recorded"
        else:
            item_latex = "\n".join(f"            \\item {escape_latex(item)}" for item in items if item.strip())
            if not item_latex.strip():
                item_latex = "            \\item % No activity recorded"

        box_code = f"""    \\begin{{tcolorbox}}[timelinebox={{{date_label}}}]
        \\begin{{itemize}}[leftmargin=*, noitemsep]
{item_latex}
        \\end{{itemize}}
    \\end{{tcolorbox}}"""
        timeline_boxes.append(box_code)

    if not timeline_boxes:
        timeline_content = "    % No daily activities added"
    else:
        timeline_content = "\n\n".join(timeline_boxes)

    # Skills items
    skills = data.get("skills_gained", [])
    if skills:
        skills_latex = "\n".join(f"        \\item {escape_latex(s)}" for s in skills if s.strip())
        if not skills_latex.strip():
            skills_latex = "        \\item % None recorded"
    else:
        skills_latex = "        \\item % None recorded"

    # Problems & Comments items
    problems = data.get("problems_comments", [])
    if problems:
        problems_latex = "\n".join(f"        \\item {escape_latex(p)}" for p in problems if p.strip())
        if not problems_latex.strip():
            problems_latex = "        \\item % None recorded"
    else:
        problems_latex = "        \\item % None recorded"

    student_name = escape_latex(str(data.get("student_name", "")))
    name_display = f" {student_name}" if student_name else ""

    # Full template construction
    latex_template = f"""\\documentclass[11pt,a4paper]{{article}}

% --- Packages ---
\\usepackage[utf8]{{inputenc}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{tabularx}}
\\usepackage{{booktabs}}
\\usepackage{{graphicx}}
\\usepackage[many]{{tcolorbox}}
\\usepackage{{enumitem}}
\\usepackage{{xcolor}}
\\usepackage{{hyperref}}

% --- Colors & Styling ---
\\definecolor{{umtblue}}{{RGB}}{{0, 71, 143}}
\\definecolor{{boxbg}}{{RGB}}{{248, 250, 252}} % Light grayish blue for modern look
\\definecolor{{boxborder}}{{RGB}}{{203, 213, 225}}

% tcolorbox setup for modern content blocks
\\tcbset{{
    modernbox/.style={{
        enhanced,
        breakable,
        colback=boxbg,
        colframe=boxborder,
        boxrule=1pt,
        arc=4pt,
        left=10pt,
        right=10pt,
        top=10pt,
        bottom=10pt,
        fonttitle=\\bfseries\\large,
        coltitle=umtblue,
        colbacktitle=boxbg,
        attach boxed title to top left={{yshift=-2mm, xshift=4mm}},
        boxed title style={{colframe=boxbg, colback=boxbg}},
        shadow={{2mm}}{{-1mm}}{{0mm}}{{black!10!white}}
    }},
    timelinebox/.style={{
        enhanced,
        blanker,
        borderline west={{1.5pt}}{{0pt}}{{umtblue}},
        left=15pt,
        top=20pt,
        bottom=10pt,
        before skip=0pt,
        after skip=0pt,
        underlay={{
            \\filldraw[umtblue] ([xshift=0.75pt, yshift=-5pt]frame.north west) circle (3.5pt);
            \\node[anchor=west, font=\\bfseries\\color{{umtblue}}, inner sep=0pt] at ([xshift=15pt, yshift=-5pt]frame.north west) {{#1}};
        }}
    }}
}}

% --- Document Info ---
\\newcommand{{\\weeknum}}{{{week_num}}}
\\newcommand{{\\datefrom}}{{{date_from}}}
\\newcommand{{\\dateto}}{{{dateto}}}
\\newcommand{{\\matricno}}{{{matricno}}}
\\newcommand{{\\leadingzero}}[1]{{\\ifnum#1<10 0\\the#1\\else\\the#1\\fi}}
\\newcommand{{\\timestamp}}{{\\leadingzero{{\\day}}/\\leadingzero{{\\month}}/\\the\\year}}

\\begin{{document}}

% --- PDF Form Environment (for checkboxes) ---
\\begin{{Form}}

% --- Header Section ---
\\noindent
\\begin{{minipage}}[c]{{0.2\\textwidth}}
    \\includegraphics[width=\\linewidth, height=2.5cm, keepaspectratio]{{"img/UMT Logo.png"}}
\\end{{minipage}}%
\\begin{{minipage}}[c]{{0.8\\textwidth}}
    \\raggedleft
    {{\\Huge \\bfseries \\textcolor{{umtblue}}{{e-Logbook}}}}\\\\[0.5em]
    {{\\large \\textbf{{{course_code}}}}}\\\\[0.5em]
    \\textbf{{Week:}} \\weeknum \\hspace{{1em}} \\textbf{{Date:}} \\datefrom{{}} to \\dateto\\\\[0.2em]
    \\textbf{{Matric No.:}} \\matricno \\hspace{{1em}} \\textbf{{Generated:}} \\timestamp
\\end{{minipage}}

\\vspace{{1em}}
\\hrule height 1pt
\\vspace{{1.5em}}

% --- Attendance Section ---
\\section*{{Daily Attendance}}
\\noindent
{attendance_table}
\\end{{Form}}

\\vspace{{2em}}

% --- Main Content Section ---
\\section*{{Report For This Week}}

\\begin{{tcolorbox}}[modernbox, title={{Weekly Activities}}]
{timeline_content}
\\end{{tcolorbox}}

\\vspace{{1em}}

\\begin{{tcolorbox}}[modernbox, title={{Knowledge / Skills Gained}}]
    \\begin{{itemize}}[leftmargin=*, noitemsep]
{skills_latex}
    \\end{{itemize}}
\\end{{tcolorbox}}

\\vspace{{1em}}

\\begin{{tcolorbox}}[modernbox, title={{Problems / Comments / Other Info}}]
    \\begin{{itemize}}[leftmargin=*, noitemsep]
{problems_latex}
    \\end{{itemize}}
\\end{{tcolorbox}}

\\vspace{{2.5em}}

% --- Verification & Signatures ---
\\noindent
\\begin{{minipage}}[t]{{0.46\\textwidth}}
    \\textbf{{Student Signature:}}\\\\[3.5em]
    \\rule{{\\linewidth}}{{0.6pt}}\\\\[0.4em]
    \\textbf{{Name:}}{name_display}\\\\[0.3em]
    \\textbf{{Date:}}
\\end{{minipage}}%
\\hfill
\\begin{{minipage}}[t]{{0.46\\textwidth}}
    \\textbf{{Industry Supervisor Signature:}}\\\\[3.5em]
    \\rule{{\\linewidth}}{{0.6pt}}\\\\[0.4em]
    \\textbf{{Name:}}\\\\[0.3em]
    \\textbf{{Date:}}
\\end{{minipage}}

\\end{{document}}
"""

    return latex_template

def save_latex_file(week_folder_path: str, data: Dict[str, Any]) -> str:
    """
    Generates and saves the <folder_name>.tex file inside the given week folder.
    Returns the absolute path to the written .tex file.
    """
    from backend.folder_manager import FolderManager
    try:
        parent_dir = os.path.dirname(os.path.abspath(week_folder_path))
        FolderManager(parent_dir).ensure_week_assets(week_folder_path)
    except Exception:
        pass

    folder_name = os.path.basename(week_folder_path)
    tex_path = os.path.join(week_folder_path, f"{folder_name}.tex")
    
    # Clean up legacy report.tex if folder_name is different
    legacy_tex = os.path.join(week_folder_path, "report.tex")
    if legacy_tex != tex_path and os.path.exists(legacy_tex):
        try:
            os.remove(legacy_tex)
        except Exception:
            pass

    content = generate_latex_content(data)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(content)
    return tex_path


