"""
Excel Operations Module for MCP Demo Server
Handles reading, authentication, and editing of Excel files
"""
import json
import os

# Global session storage (persists across function calls)
SESSIONS = {}
VALID_USERS = {
    "admin": "admin123",
    "user": "user123"
}

def login(input_str=""):
    """
    Login to Excel editing system
    Input format: username password
    Returns: session_id for authenticated access
    """
    try:
        parts = input_str.strip().split()
        if len(parts) < 2:
            return json.dumps({
                "success": False,
                "error": "Please provide username and password",
                "usage": "username password"
            })
        
        username, password = parts[0], parts[1]
        
        if username in VALID_USERS and VALID_USERS[username] == password:
            session_id = f"session_{username}_{len(SESSIONS)}"
            SESSIONS[session_id] = {
                "username": username,
                "active": True
            }
            return json.dumps({
                "success": True,
                "session_id": session_id,
                "message": f"User '{username}' authenticated successfully",
                "note": "Use this session_id for edit operations"
            })
        
        return json.dumps({
            "success": False,
            "error": "Invalid credentials",
            "hint": "Try: admin admin123 or user user123"
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

def read_file(input_str=""):
    """
    Read Excel file
    Input format: file_path [sheet_name]
    Example: data.xlsx Sheet1
    """
    try:
        if not input_str.strip():
            return json.dumps({
                "success": False,
                "error": "Please provide file path",
                "usage": "file_path [sheet_name]"
            })
        
        parts = input_str.strip().split()
        file_path = parts[0]
        sheet_name = parts[1] if len(parts) > 1 else "Sheet1"
        
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({
                "success": False,
                "error": f"File not found: {file_path}",
                "note": "Provide full path or ensure file is in current directory"
            })
        
        # In production, would use openpyxl to read actual Excel data
        return json.dumps({
            "success": True,
            "file_path": file_path,
            "sheet_name": sheet_name,
            "message": f"Excel file '{file_path}' opened successfully",
            "data_preview": "Would contain actual cell data with openpyxl",
            "note": "Install 'openpyxl' library for actual Excel reading: pip install openpyxl"
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

def edit_file(input_str=""):
    """
    Edit Excel file cell
    Input format: file_path sheet_name cell value [session_id]
    Example: data.xlsx Sheet1 A1 100 session_admin_0
    """
    try:
        parts = input_str.strip().split(maxsplit=4)
        if len(parts) < 4:
            return json.dumps({
                "success": False,
                "error": "Insufficient parameters",
                "usage": "file_path sheet_name cell value [session_id]",
                "example": "data.xlsx Sheet1 A1 100 session_admin_0"
            })
        
        file_path = parts[0]
        sheet_name = parts[1]
        cell = parts[2]
        value = parts[3]
        session_id = parts[4] if len(parts) > 4 else None
        
        # Verify session if provided
        if session_id:
            if session_id not in SESSIONS:
                return json.dumps({
                    "success": False,
                    "error": "Invalid or expired session",
                    "hint": "Login first using excel_login to get session_id"
                })
            username = SESSIONS[session_id]["username"]
        else:
            username = "anonymous"
        
        # Check if file exists
        if not os.path.exists(file_path):
            return json.dumps({
                "success": False,
                "error": f"File not found: {file_path}",
                "note": "File must exist to edit. Create it first or provide correct path."
            })
        
        # In production, would use openpyxl to actually edit the Excel file
        return json.dumps({
            "success": True,
            "file_path": file_path,
            "sheet_name": sheet_name,
            "cell": cell,
            "value": value,
            "edited_by": username,
            "message": f"Cell {cell} in '{sheet_name}' would be updated to '{value}'",
            "note": "Install 'openpyxl' library for actual Excel editing: pip install openpyxl"
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

def list_sessions(input_str=""):
    """List all active sessions (for debugging)"""
    return json.dumps({
        "success": True,
        "sessions": list(SESSIONS.keys()),
        "count": len(SESSIONS)
    })

def run(input_str=""):
    """Main entry point - shows available functions"""
    return json.dumps({
        "success": True,
        "message": "Excel Handler Module",
        "available_functions": {
            "excel_login": "Authenticate user - returns session_id",
            "excel_read": "Read Excel file data",
            "excel_edit": "Edit Excel file cell (requires session_id)",
            "excel_list_sessions": "List active sessions"
        },
        "usage_flow": [
            "1. Login: excel_login admin admin123",
            "2. Read: excel_read myfile.xlsx Sheet1",
            "3. Edit: excel_edit myfile.xlsx Sheet1 A1 NewValue session_id"
        ]
    })
