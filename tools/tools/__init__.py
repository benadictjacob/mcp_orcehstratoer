import sys
import os

# Add tools directory to path
tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

# Now import from web_tools_mcp
from web_tools_mcp import *
