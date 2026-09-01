import json, os
from .storage import MAX_FILE_BYTES

def _present(value):
    if isinstance(value,bool): return True
    return value not in (None,"",0,[])

def _render(report):
    raw_score=report.get("health_score")
    score_text="not rated" if raw_score is None else f"{raw_score}/100"
    lines=["STREAM DOCTOR", "", f"Status: {report.get('health_status','UNKNOWN')}", f"Health score: {score_text}", f"Telemetry coverage: {report.get('telemetry_coverage_pct','?')}%", report.get('summary',''), ""]

    scores=report.get('component_scores') or {}
    if scores:
        lines.append("COMPONENT EVIDENCE SCORES")
        for k,v in scores.items(): lines.append(f"  {k.title()}: {v}/100")
        lines.append("")

    ctx=report.get('context') or {}
    if ctx:
        lines.append("DEVICE / CONNECTION CONTEXT")
        simple=[('Kodi',ctx.get('kodi_version')),('Platform',ctx.get('platform')),('OS',ctx.get('os_version')),('CPU',ctx.get('cpu_name')),('CPU cores',ctx.get('cpu_cores')),('Logical processors',ctx.get('logical_processors')),('CPU max MHz',ctx.get('cpu_max_mhz')),('Total RAM GB',ctx.get('total_ram_gb')),('Internet plan Mbps',ctx.get('internet_plan_mbps')),('Known tested capacity Mbps',ctx.get('known_capacity_mbps')),('Power plan',ctx.get('power_plan'))]
        for label,value in simple:
            if value not in (None,'',[],0): lines.append(f"  {label}: {value}")
        gpus=ctx.get('gpu_names') or []; drivers=ctx.get('gpu_driver_versions') or []; driver_dates=ctx.get('gpu_driver_dates') or []
        for i,gpu in enumerate(gpus):
            drv=drivers[i] if i < len(drivers) else ''; date=driver_dates[i] if i < len(driver_dates) else ''
            extra=(f" | driver {drv}" if drv else '') + (f" | date {date}" if date else '')
            lines.append(f"  GPU {i+1}: {gpu}" + extra)
        adapters=ctx.get('adapter_names') or []; links=ctx.get('adapter_link_mbps') or []; adrv=ctx.get('adapter_driver_versions') or []; adate=ctx.get('adapter_driver_dates') or []
        if adapters and len(adapters)==len(links):
            for i,(name,link) in enumerate(zip(adapters,links)):
                extra=(f" | {link:g} Mbps" if link else '') + (f" | driver {adrv[i]}" if i < len(adrv) and adrv[i] else '') + (f" | date {adate[i]}" if i < len(adate) and adate[i] else '')
                lines.append(f"  Adapter {i+1}: {name}" + extra)
        else:
            for i,name in enumerate(adapters): lines.append(f"  Adapter {i+1}: {name}")
            if links: lines.append("  Reported active link speed(s): " + ", ".join(f"{x:g} Mbps" for x in links))
        for note in ctx.get('notes') or []: lines.append("  Note: "+str(note))
        lines.append("")

    source=report.get('source') or {}
    if any(_present(v) for v in source.values()):
        lines.append("SOURCE / PLAYBACK")
        for k,v in source.items():
            if _present(v): lines.append(f"  {k.replace('_',' ').title()}: {v}")
        lines.append("")

    metrics=report.get('metrics') or {}
    if metrics:
        lines.append("KEY MEASUREMENTS")
        for key in ('video_bitrate_mbps','audio_bitrate_kbps','video_queue_data_pct','audio_queue_data_pct','cpu_usage_pct','free_memory_pct','cpu_temp_c','gpu_temp_c','video_fps','refresh_hz','link_mbps'):
            v=metrics.get(key)
            if isinstance(v,dict):
                vals=(v.get('min'),v.get('median'),v.get('max'))
                if all(isinstance(x,(int,float)) for x in vals):
                    lines.append(f"  {key.replace('_',' ')}: min {vals[0]:.2f} | median {vals[1]:.2f} | max {vals[2]:.2f}")
        if 'caching_sample_pct' in metrics: lines.append(f"  caching samples: {metrics.get('caching_sample_pct'):.1f}%")
        if metrics.get('user_marker_count'): lines.append(f"  user problem markers: {metrics.get('user_marker_count')} ({', '.join(metrics.get('user_marker_types') or [])})")
        lines.append("")

    fs=report.get('findings') or []
    if fs:
        lines.append("FINDINGS")
        for i,f in enumerate(fs,1):
            lines.extend([f"{i}. {f.get('title','')}", f"   Confidence: {f.get('confidence','?')}% | Severity: {f.get('severity','')}", f"   {f.get('explanation','')}"])
            ev=f.get('evidence') or []
            if ev:
                lines.append("   Evidence:"); lines.extend("   - "+x for x in ev)
            rec=f.get('recommendations') or []
            if rec:
                lines.append("   Suggestions:"); lines.extend("   - "+x for x in rec)
            ex=f.get('exclusions') or []
            if ex:
                lines.append("   Not supported by this evidence:"); lines.extend("   - "+x for x in ex)
            lines.append("")
    else:
        lines.append("No strong fault diagnosis was recorded.")
    return "\n".join(lines)

def _latest_report(xbmcvfs, addon=None):
    try:
        profile=addon.getAddonInfo("profile") if addon is not None else ""
    except Exception:
        profile=""
    profile=profile or "special://profile/addon_data/service.streamdoctor"
    base=xbmcvfs.translatePath(profile.rstrip("/\\") + "/reports")
    if not os.path.isdir(base): return None
    files=[os.path.join(base,n) for n in os.listdir(base) if n.startswith('streamdoctor-') and n.endswith('.json')]
    if not files: return None
    files.sort(key=os.path.getmtime, reverse=True)
    for p in files:
        try:
            if os.path.getsize(p) > MAX_FILE_BYTES:
                continue
            with open(p,encoding='utf-8') as f:
                report=json.load(f)
            if isinstance(report,dict):
                return report
        except Exception:
            continue
    return None

def run():
    import xbmcaddon, xbmcgui, xbmcvfs
    addon=xbmcaddon.Addon(); dialog=xbmcgui.Dialog(); home=xbmcgui.Window(10000)
    choices=["Live status", "Last completed stream report", "Mark a problem that just happened", "Settings"]
    pick=dialog.select("Stream Doctor",choices)
    if pick==0:
        text=home.getProperty("StreamDoctor.LiveText") or "Stream Doctor is waiting for enough live playback telemetry."
        dialog.textviewer("Stream Doctor — Live status",text)
    elif pick==1:
        r=_latest_report(xbmcvfs,addon)
        if r: dialog.textviewer("Stream Doctor — Last report",_render(r))
        else: dialog.ok("Stream Doctor","No completed stream report is available yet.")
    elif pick==2:
        import time
        labels=["Freeze / buffering", "Jerky or stuttering picture", "Sound dropout / jerking", "Audio/video sync", "Poor picture quality", "Other"]
        codes=["freeze","video","audio","avsync","quality","other"]
        issue=dialog.select("What just happened?",labels)
        if issue >= 0:
            home.setProperty("StreamDoctor.MarkerType",codes[issue])
            home.setProperty("StreamDoctor.UserMarker",str(time.time()))
            dialog.notification("Stream Doctor","Problem marker recorded for the current telemetry window.",xbmcgui.NOTIFICATION_INFO,3500)
    elif pick==3:
        addon.openSettings()
