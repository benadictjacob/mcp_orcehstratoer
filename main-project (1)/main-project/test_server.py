import json
import subprocess
import time
from typing import Optional, Any

def run_test_scenario(scenario_name: str, code: str, logs: Optional[str] = None) -> None:
    print(f"\n>>> SCENARIO: {scenario_name}")
    process = subprocess.Popen(
        ['python', 'validation_agent.py'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    try:
        if process.stdin is None or process.stdout is None:
            print("Failed to initialize pipes")
            return

        start_time = time.time()
        # Initialize
        init_req: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}}
        process.stdin.write(json.dumps(init_req) + '\n')
        process.stdin.flush()
        process.stdout.readline()

        # Validate
        args: dict[str, Any] = {
            "generated_code": code, 
            "target_mcp_server": "T", 
            "function_purpose": scenario_name
        }
        if logs:
            args["execution_logs"] = logs

        tool_req: dict[str, Any] = {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {"name": "validate_code", "arguments": args}
        }
        process.stdin.write(json.dumps(tool_req) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline()
        end_time = time.time()
        
        if not response:
            print("No response from server")
            # Print stderr to see why
            if process.stderr:
                print("STDERR:", process.stderr.read())
            return

        print(f"RAW RESPONSE: {response.strip()[:200]}...") # Truncate for brevity
        result = json.loads(response)
        
        # Check for error explicitly
        if 'error' in result:
             print(f"RPC ERROR: {result['error']}")
             if process.stderr:
                 print("STDERR:", process.stderr.read())
             return

        if 'result' in result and 'content' in result['result']:
            text_content = result['result']['content'][0]['text']
            print(f"Tool Refurned Content: {text_content[:100]}...") # See what we got
            
            try:
                inner = json.loads(text_content)
                print(f"Status: {inner['status']}")
                print(f"Confidence: {inner['confidence_score']}")
                print(f"Errors: {len(inner['error_summary'])}")
                if len(inner['error_summary']) > 0:
                    print(f"First Error: {inner['error_summary'][0]['description']}")
                print(f"Time Taken: {round((end_time - start_time) * 1000, 2)}ms")
                if inner['status'] == "FIXED":
                    print("Correction applied successfully.")
                    print("--- CORRECTED CODE ---")
                    print(inner['corrected_code'])
                    print("--- END CORRECTED CODE ---")
                # Show explanations if they contain corrections
                for exp in inner.get('explanations', []):
                    if 'FIX-' in exp:
                        print(f"  {exp}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse inner JSON: {e}")
                print("Complete Text Content:", text_content)
                if process.stderr:
                    print("STDERR:", process.stderr.read())
        else:
            print(f"Unexpected response: {result}")
            if process.stderr:
                print("STDERR:", process.stderr.read())
            
    finally:
        process.terminate()

def test_mcp_server():
    # 1. PERFECT CODE (MCP Compliant)
    perfect_code = "\"\"\"Module docstring\"\"\"\nfrom mcp.server.fastmcp import FastMCP\nmcp = FastMCP('demo')\n\n@mcp.tool()\nasync def add(a: int, b: int) -> int:\n    return a + b"
    run_test_scenario("PERFECT_CODE", perfect_code)

    # 2. FATAL CODE (Syntax Error - unfixable)
    fatal_code = "from mcp.server.fastmcp import FastMCP\ndef broken("
    run_test_scenario("FATAL_SYNTAX_UNFIXABLE", fatal_code)

    # 3. FIXABLE SYNTAX (Missing colon after def)
    fixable_syntax = "from mcp.server.fastmcp import FastMCP\nmcp = FastMCP('demo')\n@mcp.tool()\nasync def greet(name: str)\n    return f'Hello {name}'"
    run_test_scenario("FIXABLE_SYNTAX", fixable_syntax)

    # 4. FIXABLE SYNTAX (Keyword typo)
    typo_syntax = "form mcp.server.fastmcp improt FastMCP\nmcp = FastMCP('demo')\n@mcp.tool()\nasyc dfe greet(name: str):\n    retrun f'Hello {name}'"
    run_test_scenario("FIXABLE_TYPOS", typo_syntax)

    # 5. FIXABLE CODE (Blocking sleep in async MCP tool)
    fixable_code = "from mcp.server.fastmcp import FastMCP\nmcp = FastMCP('demo')\n@mcp.tool()\nasync def slow():\n    import time\n    time.sleep(1)"
    run_test_scenario("FIXABLE_CONCURRENCY", fixable_code)

    # 6. BLOCKED CODE (Security Violation - eval)
    blocked_code = "from mcp.server.fastmcp import FastMCP\nmcp = FastMCP('demo')\n@mcp.tool()\nasync def hack():\n    eval('os.system(\"rm -rf\")')"
    run_test_scenario("BLOCKED_SECURITY", blocked_code)

    # 7. LOG ANALYSIS (Traceback in logs)
    log_code = "\"\"\"Module docstring\"\"\"\nfrom mcp.server.fastmcp import FastMCP\nmcp = FastMCP('demo')"
    broken_logs = "Error: Something went wrong\nTraceback (most recent call last):\n  File 'x.py', line 1, in <module>\nValueError: Oops"
    run_test_scenario("LOG_FAILURE", log_code, logs=broken_logs)

if __name__ == "__main__":
    test_mcp_server()
