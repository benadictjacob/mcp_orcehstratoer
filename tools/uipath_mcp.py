"""
UiPath MCP Capability
=====================
Scans C:\\Users\\VICTUS\\OneDrive\\Documents\\UiPath
Provides tools to list, read, summarize, search,
create and modify UiPath workflows (.xaml files).

Commands:
- list_projects              : List all UiPath projects
- list_workflows <proj_path> : List .xaml files in a project
- summarize <xaml_path>      : Parse and summarize a workflow
- read <xaml_path>           : Read raw XAML content
- write <xaml_path>|<content>: Write/update a workflow (auto-backup)
- search <name>              : Search .xaml files by name
- create <project_name>      : Create a new UiPath project
- info <proj_path>           : Show project.json metadata
- help                       : Show this help
"""

import os
import json
import glob
import xml.etree.ElementTree as ET

UIPATH_ROOT = r"C:\Users\VICTUS\OneDrive\Documents\UiPath"


def get_all_projects(root):
    projects = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            if "project.json" in filenames:
                proj_file = os.path.join(dirpath, "project.json")
                try:
                    with open(proj_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    meta = {}
                projects.append({
                    "name": meta.get("name", os.path.basename(dirpath)),
                    "description": meta.get("description", ""),
                    "version": meta.get("projectVersion", "unknown"),
                    "path": dirpath,
                    "main": meta.get("main", "Main.xaml"),
                })
    except Exception as e:
        return [{"error": str(e)}]
    return projects


def get_xaml_files(project_path):
    return glob.glob(os.path.join(project_path, "**", "*.xaml"), recursive=True)


def parse_xaml_summary(xaml_path):
    try:
        tree = ET.parse(xaml_path)
        root = tree.getroot()
    except Exception as e:
        return {"error": str(e)}

    activity_counts = {}
    variables = []
    sequences = []

    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        activity_counts[tag] = activity_counts.get(tag, 0) + 1
        if tag == "Variable":
            name = elem.get("Name", "")
            vtype = elem.get("{http://schemas.microsoft.com/winfx/2006/xaml}TypeArguments", "")
            if name:
                variables.append(f"{name} ({vtype})")
        if tag == "Sequence":
            dn = elem.get("DisplayName", "")
            if dn:
                sequences.append(dn)

    top_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return {
        "filename": os.path.basename(xaml_path),
        "path": xaml_path,
        "variables": variables[:20],
        "sequences": sequences[:10],
        "top_activities": top_activities,
        "total_elements": sum(activity_counts.values()),
    }


def read_xaml_raw(xaml_path, max_chars=6000):
    try:
        with open(xaml_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > max_chars:
            return content[:max_chars] + f"\n\n... [TRUNCATED - total {len(content)} chars]"
        return content
    except Exception as e:
        return f"ERROR reading: {e}"


def write_xaml(xaml_path, content):
    try:
        if os.path.exists(xaml_path):
            with open(xaml_path, "r", encoding="utf-8") as f:
                original = f.read()
            with open(xaml_path + ".bak", "w", encoding="utf-8") as f:
                f.write(original)
        with open(xaml_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"SUCCESS: Written to {xaml_path}\nBackup saved at {xaml_path}.bak"
    except Exception as e:
        return f"ERROR writing: {e}"


def search_xaml(name):
    pattern = os.path.join(UIPATH_ROOT, "**", f"*{name}*")
    return [f for f in glob.glob(pattern, recursive=True) if f.endswith(".xaml")]


def create_project(project_name, description=""):
    proj_path = os.path.join(UIPATH_ROOT, project_name)
    try:
        os.makedirs(proj_path, exist_ok=True)

        project_json = {
            "name": project_name,
            "description": description,
            "main": "Main.xaml",
            "outputType": "Process",
            "expressionLanguage": "VisualBasic",
            "projectVersion": "1.0.0",
            "dependencies": {
                "UiPath.System.Activities": "[23.4.4, )",
                "UiPath.UIAutomation.Activities": "[23.4.7, )"
            },
            "schemaVersion": "3.4"
        }
        with open(os.path.join(proj_path, "project.json"), "w", encoding="utf-8") as f:
            json.dump(project_json, f, indent=2)

        main_xaml = (
            '<Activity mc:Ignorable="sap sap2010" x:Class="Main"\n'
            '  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"\n'
            '  xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"\n'
            '  xmlns:sap="http://schemas.microsoft.com/netfx/2009/xaml/activities/presentation"\n'
            '  xmlns:sap2010="http://schemas.microsoft.com/netfx/2010/xaml/activities/presentation"\n'
            '  xmlns:scg="clr-namespace:System.Collections.Generic;assembly=System.Private.CoreLib"\n'
            '  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">\n'
            '  <Sequence DisplayName="Main Sequence" sap2010:WorkflowViewState.IdRef="Sequence_1">\n'
            '    <sap:WorkflowViewStateService.ViewState>\n'
            '      <scg:Dictionary x:TypeArguments="x:String, x:Object">\n'
            '        <x:Boolean x:Key="IsExpanded">True</x:Boolean>\n'
            '      </scg:Dictionary>\n'
            '    </sap:WorkflowViewStateService.ViewState>\n'
            f'    <WriteLine Text="Hello from {project_name}!" />\n'
            '  </Sequence>\n'
            '</Activity>'
        )

        with open(os.path.join(proj_path, "Main.xaml"), "w", encoding="utf-8") as f:
            f.write(main_xaml)

        return (
            f"SUCCESS: Project '{project_name}' created!\n"
            f"  Path  : {proj_path}\n"
            f"  Files : project.json, Main.xaml\n"
            f"  Open  : File -> Open -> {proj_path} in UiPath Studio"
        )
    except Exception as e:
        return f"ERROR creating project: {e}"


def run(input_data=""):

    HELP = (
        f"UiPath MCP Capability\n"
        f"Root: {UIPATH_ROOT}\n\n"
        f"Commands:\n"
        f"  list_projects                      - List all UiPath projects\n"
        f"  list_workflows <project_path>      - List .xaml files in a project\n"
        f"  summarize <xaml_path>              - Decode and summarize a workflow\n"
        f"  read <xaml_path>                   - Read raw XAML content\n"
        f"  write <xaml_path>|<xaml_content>   - Write/update a workflow (pipe-separated)\n"
        f"  search <name>                      - Search .xaml files by name\n"
        f"  create <project_name>              - Create a new blank project\n"
        f"  info <project_path>                - Show project.json metadata\n"
        f"  help                               - Show this message\n\n"
        f"Examples:\n"
        f"  list_projects\n"
        f"  list_workflows C:\\Users\\VICTUS\\OneDrive\\Documents\\UiPath\\MyBot\n"
        f"  summarize C:\\Users\\VICTUS\\OneDrive\\Documents\\UiPath\\MyBot\\Main.xaml\n"
        f"  search invoice\n"
        f"  create EmailAutomation\n"
    )

    if not input_data or input_data.strip().lower() == "help":
        return HELP

    parts = input_data.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""

    if command == "list_projects":
        projects = get_all_projects(UIPATH_ROOT)
        if not projects:
            return f"No UiPath projects found in:\n{UIPATH_ROOT}"
        lines = [f"Found {len(projects)} project(s) in {UIPATH_ROOT}:\n"]
        for p in projects:
            if "error" in p:
                lines.append(f"  ERROR: {p['error']}")
                continue
            lines.append(f"  [PROJECT] {p['name']}  (v{p['version']})")
            lines.append(f"     Path : {p['path']}")
            lines.append(f"     Main : {p['main']}")
            if p["description"]:
                lines.append(f"     Desc : {p['description']}")
            lines.append("")
        return "\n".join(lines)

    elif command == "list_workflows":
        if not args:
            return "ERROR: Provide a project path.\nExample: list_workflows C:\\Users\\VICTUS\\OneDrive\\Documents\\UiPath\\MyBot"
        xamls = get_xaml_files(args)
        if not xamls:
            return f"No .xaml files found in: {args}"
        lines = [f"Found {len(xamls)} workflow(s) in {os.path.basename(args)}:\n"]
        for x in xamls:
            size = os.path.getsize(x) if os.path.exists(x) else 0
            lines.append(f"  [XAML] {os.path.basename(x)}  ({size:,} bytes)")
            lines.append(f"         {x}")
        return "\n".join(lines)

    elif command == "summarize":
        if not args:
            return "ERROR: Provide a .xaml path.\nExample: summarize C:\\...\\Main.xaml"
        s = parse_xaml_summary(args)
        if "error" in s:
            return f"Parse error: {s['error']}"
        lines = [
            f"[FILE] {s['filename']}",
            f"[PATH] {s['path']}",
            f"[COUNT] Total elements: {s['total_elements']}",
            "",
            "[VARIABLES]",
        ]
        for v in (s["variables"] or ["  (none found)"]):
            lines.append(f"   - {v}")
        lines += ["", "[SEQUENCES]"]
        for seq in (s["sequences"] or ["  (none found)"]):
            lines.append(f"   - {seq}")
        lines += ["", "[TOP ACTIVITY TYPES]"]
        for act, count in s["top_activities"]:
            lines.append(f"   {count:>4}x  {act}")
        return "\n".join(lines)

    elif command == "read":
        if not args:
            return "ERROR: Provide a .xaml path.\nExample: read C:\\...\\Main.xaml"
        return read_xaml_raw(args)

    elif command == "write":
        if "|" not in args:
            return "ERROR: Use pipe separator.\nFormat: write <xaml_path>|<xaml_content>"
        xaml_path, content = args.split("|", 1)
        return write_xaml(xaml_path.strip(), content.strip())

    elif command == "search":
        if not args:
            return "ERROR: Provide a search name.\nExample: search invoice"
        results = search_xaml(args)
        if not results:
            return f"No .xaml files matching '{args}' found in {UIPATH_ROOT}"
        lines = [f"Found {len(results)} match(es) for '{args}':\n"]
        for r in results:
            lines.append(f"  [XAML] {r}")
        return "\n".join(lines)

    elif command == "create":
        if not args:
            return "ERROR: Provide a project name.\nExample: create EmailAutomation"
        name_parts = args.split(maxsplit=1)
        proj_name = name_parts[0]
        desc = name_parts[1] if len(name_parts) > 1 else ""
        return create_project(proj_name, desc)

    elif command == "info":
        if not args:
            return "ERROR: Provide a project path.\nExample: info C:\\...\\MyBot"
        json_path = os.path.join(args, "project.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        except FileNotFoundError:
            return f"ERROR: project.json not found in {args}"
        except Exception as e:
            return f"ERROR: {e}"

    else:
        return f"Unknown command: '{command}'\nType 'help' to see available commands."
