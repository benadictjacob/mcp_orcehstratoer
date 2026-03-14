import subprocess

def shell(cmd, timeout=30):
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return {"ok": proc.returncode == 0, "out": proc.stdout.strip(), "err": proc.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "err": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"ok": False, "err": str(e)}

def run(capability_input):
    cmd = (capability_input or "help").strip().lower().split()[0]

    if cmd == "report":
        sections = []

        r = shell("Get-WmiObject Win32_Processor | Select-Object Name, LoadPercentage, NumberOfCores, MaxClockSpeed | Format-List")
        sections.append("=== CPU ===\n" + r.get("out", r.get("err")))

        r = shell("""
$os = Get-WmiObject Win32_OperatingSystem
$total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$free  = [math]::Round($os.FreePhysicalMemory   / 1MB, 2)
$used  = [math]::Round($total - $free, 2)
$pct   = [math]::Round(($used / $total) * 100, 1)
"Total : $total GB"
"Used  : $used GB ($pct%)"
"Free  : $free GB"
""")
        sections.append("=== MEMORY ===\n" + r.get("out", r.get("err")))

        r = shell("Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Used(GB)';E={[math]::Round($_.Used/1GB,2)}}, @{N='Free(GB)';E={[math]::Round($_.Free/1GB,2)}} | Format-Table -AutoSize")
        sections.append("=== DISK ===\n" + r.get("out", r.get("err")))

        r = shell("(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime | Select-Object Days,Hours,Minutes | Format-List")
        sections.append("=== UPTIME ===\n" + r.get("out", r.get("err")))

        r = shell("Get-WmiObject Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture, BuildNumber | Format-List")
        sections.append("=== OS INFO ===\n" + r.get("out", r.get("err")))

        r = shell("Get-Process | Sort-Object CPU -Descending | Select-Object -First 8 Name,Id,@{N='CPU(s)';E={[math]::Round($_.CPU,1)}},@{N='RAM(MB)';E={[math]::Round($_.WorkingSet/1MB,1)}} | Format-Table -AutoSize")
        sections.append("=== TOP PROCESSES ===\n" + r.get("out", r.get("err")))

        r = shell("Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object Name, InterfaceDescription, LinkSpeed | Format-Table -AutoSize")
        sections.append("=== NETWORK ADAPTERS (Active) ===\n" + r.get("out", r.get("err")))

        r = shell("Get-WmiObject Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus | Format-List")
        bat = r.get("out", "")
        sections.append("=== BATTERY ===\n" + (bat if bat else "No battery / Desktop system"))

        return "\n\n".join(sections)

    elif cmd == "cpu":
        r = shell("Get-WmiObject Win32_Processor | Select-Object Name, LoadPercentage, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed | Format-List")
        return "[CPU HEALTH]\n" + r.get("out", r.get("err"))

    elif cmd == "memory":
        r = shell("""
$os = Get-WmiObject Win32_OperatingSystem
$total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$free  = [math]::Round($os.FreePhysicalMemory   / 1MB, 2)
$used  = [math]::Round($total - $free, 2)
$pct   = [math]::Round(($used / $total) * 100, 1)
"Total RAM : $total GB"
"Used      : $used GB ($pct% used)"
"Free      : $free GB"
""")
        return "[MEMORY HEALTH]\n" + r.get("out", r.get("err"))

    elif cmd == "disk":
        r = shell("Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Used(GB)';E={[math]::Round($_.Used/1GB,2)}}, @{N='Free(GB)';E={[math]::Round($_.Free/1GB,2)}}, @{N='Total(GB)';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}} | Format-Table -AutoSize")
        return "[DISK HEALTH]\n" + r.get("out", r.get("err"))

    elif cmd == "processes":
        r = shell("Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 Name,Id,@{N='CPU(s)';E={[math]::Round($_.CPU,1)}},@{N='RAM(MB)';E={[math]::Round($_.WorkingSet/1MB,1)}} | Format-Table -AutoSize")
        return "[TOP PROCESSES]\n" + r.get("out", r.get("err"))

    elif cmd == "network":
        r = shell("Get-NetAdapter | Select-Object Name, Status, LinkSpeed, InterfaceDescription | Format-Table -AutoSize")
        r2 = shell("Test-Connection 8.8.8.8 -Count 2 -ErrorAction SilentlyContinue | Select-Object Address, Latency | Format-Table -AutoSize")
        return "[NETWORK]\n" + r.get("out", r.get("err")) + "\n\n[PING 8.8.8.8]\n" + (r2.get("out") or "No response")

    elif cmd == "uptime":
        r = shell("$b = (gcim Win32_OperatingSystem).LastBootUpTime; $u = (Get-Date) - $b; \"Last Boot : $b\"; \"Uptime    : $($u.Days)d $($u.Hours)h $($u.Minutes)m\"")
        return "[UPTIME]\n" + r.get("out", r.get("err"))

    elif cmd == "battery":
        r = shell("Get-WmiObject Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus, Name | Format-List")
        out = r.get("out", "")
        return "[BATTERY]\n" + (out if out else "No battery detected / Desktop system")

    elif cmd == "temp":
        r = shell("Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root/wmi -ErrorAction SilentlyContinue | ForEach-Object { \"Zone: $($_.InstanceName) | Temp: $([math]::Round($_.CurrentTemperature / 10 - 273.15, 1)) C\" }")
        out = r.get("out", "")
        return "[TEMPERATURE]\n" + (out if out else "Temperature sensors not accessible via WMI")

    elif cmd == "services":
        r = shell("Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, DisplayName | Sort-Object DisplayName | Format-Table -AutoSize")
        return "[RUNNING SERVICES]\n" + r.get("out", r.get("err"))

    elif cmd == "alerts":
        lines = ["[HEALTH ALERTS]"]

        r = shell("(Get-WmiObject Win32_Processor).LoadPercentage")
        try:
            cpu = int(r.get("out", "0"))
            status = "WARNING - HIGH CPU" if cpu > 85 else "OK"
            lines.append(f"CPU Usage : {cpu}% [{status}]")
        except:
            lines.append("CPU : Could not read")

        r = shell("""
$os = Get-WmiObject Win32_OperatingSystem
$total = $os.TotalVisibleMemorySize
$free  = $os.FreePhysicalMemory
$pct   = [math]::Round((($total - $free) / $total) * 100, 1)
Write-Output $pct
""")
        try:
            ram = float(r.get("out", "0"))
            status = "WARNING - HIGH RAM" if ram > 85 else "OK"
            lines.append(f"RAM Usage : {ram}% [{status}]")
        except:
            lines.append("RAM : Could not read")

        r = shell("[math]::Round((Get-PSDrive C).Free / 1GB, 2)")
        try:
            free_gb = float(r.get("out", "999"))
            status = "WARNING - LOW SPACE" if free_gb < 10 else "OK"
            lines.append(f"Disk C Free : {free_gb} GB [{status}]")
        except:
            lines.append("Disk : Could not read")

        r = shell("Test-Connection 8.8.8.8 -Count 1 -Quiet")
        internet = r.get("out", "").strip().lower()
        lines.append("Internet : " + ("Connected [OK]" if "true" in internet else "NOT reachable [ALERT]"))

        return "\n".join(lines)

    else:
        return """[OS HEALTH MONITOR] Commands:
  report     - Full system health report
  cpu        - CPU usage, cores, clock speed
  memory     - RAM total / used / free
  disk       - All drives usage
  processes  - Top 15 processes by CPU
  network    - Adapters + ping test
  uptime     - System uptime and last boot
  battery    - Battery charge and status
  temp       - CPU thermal temperature
  services   - All running services
  alerts     - Smart health alerts and warnings"""
