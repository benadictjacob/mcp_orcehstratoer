import subprocess, os, glob

UIPATH_ROOT = r"C:\Users\VICTUS\OneDrive\Documents\UiPath"

COMMON_PATHS = [
    r"C:\Users\VICTUS\AppData\Local\Programs\UiPath\Studio\uipcli.exe",
    r"C:\Program Files\UiPath\Studio\uipcli.exe",
    r"C:\Program Files (x86)\UiPath\Studio\uipcli.exe",
]

def find_uipcli():
    results = []
    for path in COMMON_PATHS:
        if os.path.exists(path):
            results.append(path)
    try:
        out = subprocess.run(["where.exe","uipcli.exe"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            for line in out.stdout.strip().splitlines():
                if line.strip() not in results:
                    results.append(line.strip())
    except Exception:
        pass
    return list(set(results))

def shell(cmd, ps=True, timeout=30):
    try:
        if ps:
            proc = subprocess.run(["powershell","-NoProfile","-Command",cmd], capture_output=True, text=True, timeout=timeout)
        else:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"ok": proc.returncode==0, "code": proc.returncode, "out": proc.stdout.strip(), "err": proc.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "err": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def run(capability_input):
    parts = capability_input.strip().split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd == "whoami":
        r = shell("whoami; $env:COMPUTERNAME; $env:USERNAME")
        return "[WHOAMI]\n" + r.get("out", r.get("err",""))

    elif cmd == "find_uipath":
        lines = ["[SEARCHING FOR UIPATH CLI]"]
        found = find_uipcli()
        if found:
            lines.append("Found uipcli.exe:")
            for f in found: lines.append("  " + f)
        else:
            lines.append("Not found in common paths, running deep search...")
            r = shell(r"Get-ChildItem 'C:\Users\VICTUS\AppData\Local' -Recurse -Filter 'uipcli.exe' -ErrorAction SilentlyContinue | Select-Object -First 5 FullName", timeout=25)
            lines.append(r.get("out") or "Nothing found in AppData")
            r2 = shell("Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Where-Object {$_.DisplayName -like '*UiPath*'} | Select-Object DisplayName,InstallLocation | Format-List", timeout=10)
            lines.append("[REGISTRY]\n" + (r2.get("out") or "UiPath not in registry"))
        return "\n".join(lines)

    elif cmd == "run_uipath":
        proj = args.strip() or UIPATH_ROOT
        found = find_uipcli()
        if not found:
            return "[ERROR] uipcli.exe not found. Run find_uipath first."
        cli = found[0]
        r = shell(f'& "{cli}" run "{proj}"', timeout=120)
        out = [f"[UIPATH RUN] cli={cli}", f"project={proj}", f"exit={r.get('code','?')}"]
        if r.get("out"): out.append("[OUTPUT]\n" + r["out"])
        if r.get("err"): out.append("[STDERR]\n" + r["err"])
        return "\n".join(out)

    elif cmd == "run":
        if not args: return "[ERROR] Usage: run <powershell command>"
        r = shell(args)
        return f"[PS] {args}\nExit:{r.get('code','?')}\n{r.get('out','')}\n{r.get('err','')}"

    elif cmd == "cmd":
        if not args: return "[ERROR] Usage: cmd <command>"
        r = shell(args, ps=False)
        return f"[CMD] {args}\nExit:{r.get('code','?')}\n{r.get('out','')}\n{r.get('err','')}"

    elif cmd == "ps":
        r = shell("Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 Name,Id,CPU | Format-Table -AutoSize")
        return "[PROCESSES]\n" + r.get("out","")

    elif cmd == "env":
        v = args.strip() or "PATH"
        r = shell(f"$env:{v}")
        return f"[ENV:{v}]\n" + r.get("out","not found")

    else:
        return """[SHELL EXECUTOR] Commands:
  whoami           - Current user info
  find_uipath      - Locate uipcli.exe
  run_uipath <path>- Run a UiPath project
  run <cmd>        - PowerShell command
  cmd <cmd>        - CMD command
  ps               - Running processes
  env <VAR>        - Environment variable"""
