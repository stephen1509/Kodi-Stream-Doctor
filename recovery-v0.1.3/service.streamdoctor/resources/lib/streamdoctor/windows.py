import json, platform, re, subprocess
from typing import Optional
from .model import SystemContext
from .parsing import parse_link_mbps

_PS = r'''$ErrorActionPreference='SilentlyContinue';
$cpu=Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed;
$os=Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,TotalVisibleMemorySize,FreePhysicalMemory;
$gpu=@(Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,DriverDate,AdapterRAM,VideoProcessor);
$net=@(Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object { $s=Get-NetAdapterStatistics -Name $_.Name; [pscustomobject]@{Name=$_.Name;Description=$_.InterfaceDescription;LinkSpeed=$_.LinkSpeed;DriverVersion=$_.DriverVersion;DriverDate=$_.DriverDate;ReceivedPacketErrors=$s.ReceivedPacketErrors;OutboundPacketErrors=$s.OutboundPacketErrors;ReceivedDiscardedPackets=$s.ReceivedDiscardedPackets;OutboundDiscardedPackets=$s.OutboundDiscardedPackets} });
$power=(Get-CimInstance -Namespace root/cimv2/power -ClassName Win32_PowerPlan | Where-Object {$_.IsActive} | Select-Object -First 1 -ExpandProperty ElementName);
[pscustomobject]@{cpu=$cpu;os=$os;gpu=$gpu;net=$net;power_plan=$power} | ConvertTo-Json -Compress -Depth 6'''


def _int(x) -> Optional[int]:
    try: return int(x)
    except (TypeError, ValueError): return None


def inspect_windows(timeout=6.0) -> SystemContext:
    ctx = SystemContext(platform=platform.system().lower())
    if platform.system().lower() != "windows":
        ctx.notes.append("Windows companion snapshot unavailable on this platform.")
        return ctx
    try:
        cp = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _PS], capture_output=True, text=True, timeout=timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if cp.returncode != 0 or not cp.stdout.strip():
            ctx.notes.append("Windows read-only PowerShell inventory failed; Kodi telemetry remains active.")
            return ctx
        data = json.loads(cp.stdout)
        cpu = data.get("cpu") or {}; osd = data.get("os") or {}
        ctx.cpu_name = str(cpu.get("Name") or "").strip()
        ctx.cpu_cores = _int(cpu.get("NumberOfCores")); ctx.logical_processors = _int(cpu.get("NumberOfLogicalProcessors"))
        try: ctx.cpu_max_mhz = float(cpu.get("MaxClockSpeed"))
        except (TypeError, ValueError): pass
        ctx.os_version = " ".join(str(osd.get(k) or "") for k in ("Caption","Version","BuildNumber")).strip()
        total_kb = _int(osd.get("TotalVisibleMemorySize"))
        if total_kb: ctx.total_ram_gb = round(total_kb / 1024 / 1024, 2)
        gpu = data.get("gpu") or []
        if isinstance(gpu, dict): gpu=[gpu]
        ctx.gpu_names=[str(g.get("Name") or "") for g in gpu if g.get("Name")]
        ctx.gpu_driver_versions=[str(g.get("DriverVersion") or "") for g in gpu]
        ctx.gpu_driver_dates=[str(g.get("DriverDate") or "") for g in gpu]
        net = data.get("net") or []
        if isinstance(net, dict): net=[net]
        ctx.adapter_names=[str(n.get("Name") or n.get("Description") or "") for n in net]
        ctx.adapter_driver_versions=[str(n.get("DriverVersion") or "") for n in net]
        ctx.adapter_driver_dates=[str(n.get("DriverDate") or "") for n in net]
        ctx.adapter_link_mbps=[v for v in (parse_link_mbps(n.get("LinkSpeed")) for n in net) if v]
        ctx.power_plan = str(data.get("power_plan") or "").strip()
        for field, target in [("ReceivedPacketErrors","adapter_rx_errors"),("OutboundPacketErrors","adapter_tx_errors"),("ReceivedDiscardedPackets","adapter_rx_discards"),("OutboundDiscardedPackets","adapter_tx_discards")]:
            vals=[_int(n.get(field)) or 0 for n in net]
            if vals: setattr(ctx,target,sum(vals))
    except Exception as e:
        ctx.notes.append("Windows inventory unavailable: " + type(e).__name__)
    return ctx
