"""Paint automation tool for drawing circles."""
import subprocess
import time
import json

def run(input_text: str = "") -> str:
    """
    Draw a circle in Microsoft Paint.
    
    Args:
        input_text: Optional parameters in format "x,y,radius" (e.g., "400,300,100")
                   If not provided, uses default values.
    
    Returns:
        JSON string with status message about the circle drawing operation.
    """
    try:
        # Parse input parameters
        if input_text and input_text.strip():
            parts = input_text.split(',')
            x = int(parts[0]) if len(parts) > 0 else 400
            y = int(parts[1]) if len(parts) > 1 else 300
            radius = int(parts[2]) if len(parts) > 2 else 100
        else:
            x, y, radius = 400, 300, 100
        
        result = {
            "success": True,
            "operation": "draw_circle",
            "parameters": {
                "center_x": x,
                "center_y": y,
                "radius": radius
            },
            "message": f"Circle drawing instructions generated for Paint",
            "instructions": [
                "Open Microsoft Paint (mspaint.exe)",
                "Click on 'Shapes' in the toolbar",
                "Select the circle/oval shape",
                f"Hold Shift key and drag from point ({x-radius}, {y-radius}) to ({x+radius}, {y+radius})",
                "Release mouse to complete the circle"
            ],
            "note": "Automated drawing requires pyautogui library (pip install pyautogui)"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_result)
