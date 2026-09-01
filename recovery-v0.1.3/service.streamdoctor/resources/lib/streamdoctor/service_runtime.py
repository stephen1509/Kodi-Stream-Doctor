import platform, re, time


def marker_is_fresh(value, now=None, max_age=20.0):
    try:
        stamp=float(value)
    except (TypeError, ValueError):
        return False
    now=time.time() if now is None else float(now)
    age=now-stamp
    return -2.0 <= age <= float(max_age)

def kodi_major_version(value):
    m=re.search(r"\d+", str(value or ""))
    return int(m.group(0)) if m else 0

def run():
    import xbmc, xbmcaddon, xbmcgui, xbmcvfs
    from .kodi_sensor import KodiTelemetryReader
    from .session import SessionAnalyzer
    from .storage import write_report, load_reports
    from .history import apply_history
    from .windows import inspect_windows
    from .scoring import telemetry_coverage, health_status

    addon=xbmcaddon.Addon(); monitor=xbmc.Monitor()
    if not addon.getSettingBool("enabled"): return
    major=kodi_major_version(xbmc.getInfoLabel("System.BuildVersion"))
    if major and major < 22:
        xbmcgui.Dialog().notification("Stream Doctor", "Kodi 22 Piers is required for full telemetry.", xbmcgui.NOTIFICATION_WARNING, 6000)
    player=xbmc.Player(); sensor=KodiTelemetryReader(xbmc, player)
    context=inspect_windows(); context.kodi_version=xbmc.getInfoLabel("System.BuildVersion") or ""; context.platform=platform.system().lower()
    try:
        p=addon.getSettingInt("internet_plan_mbps"); context.internet_plan_mbps=float(p) if p>0 else None
        c=addon.getSettingInt("known_capacity_mbps"); context.known_capacity_mbps=float(c) if c>0 else None
    except Exception: pass
    session=None; active_source_key=""; last_notice={}; last_live_update=0.0; home=xbmcgui.Window(10000); last_marker=home.getProperty("StreamDoctor.UserMarker") or ""
    interval=max(0.25,min(2.0,(addon.getSettingInt("sample_interval_ms") or 500)/1000.0))

    def finish(sess):
        if sess is None: return None
        report=sess.report()
        if addon.getSettingBool("store_reports"):
            try:
                profile=addon.getAddonInfo("profile") or "special://profile/addon_data/service.streamdoctor"
            except Exception:
                profile="special://profile/addon_data/service.streamdoctor"
            base=xbmcvfs.translatePath(profile.rstrip("/\\") + "/reports")
            try:
                report=apply_history(report, load_reports(base,20))
                write_report(base, report.to_dict(), addon.getSettingInt("retention_files") or 20)
            except Exception as e:
                xbmc.log("[Stream Doctor] report write failed: "+type(e).__name__, xbmc.LOGWARNING)
        xbmc.log("[Stream Doctor] "+report.summary, xbmc.LOGINFO)
        home.setProperty("StreamDoctor.LiveText","No live/Internet stream is currently being monitored.")
        return None

    while not monitor.abortRequested():
        try: playing=player.isPlayingVideo()
        except Exception: playing=False
        if playing:
            s=sensor.sample(time.monotonic(), playing=True)
            streamlike=s.is_live or s.is_internet_stream or s.is_livetv_content
            if not streamlike:
                session=finish(session); active_source_key=""
            else:
                # Kodi/PVR can change channels without a clean stop callback. Keep
                # evidence from different sources in separate diagnostic sessions.
                if session is not None and active_source_key and s.source_key and s.source_key != active_source_key:
                    session=finish(session); last_notice={}; last_live_update=0.0
                if session is None:
                    session=SessionAnalyzer(context); active_source_key=s.source_key or ""
                elif not active_source_key and s.source_key:
                    active_source_key=s.source_key
                session.add(s)
                marker=home.getProperty("StreamDoctor.UserMarker")
                if marker and marker != last_marker:
                    if marker_is_fresh(marker):
                        session.mark_problem(home.getProperty("StreamDoctor.MarkerType") or "other")
                    last_marker=marker
                if len(session.samples)>=8:
                    live=session.live_findings(); now=time.monotonic()
                    if now-last_live_update>=1.0:
                        recent=session.recent(30.0)
                        coverage,coverage_detail=telemetry_coverage(recent)
                        status=health_status(live,coverage,coverage_detail)
                        if status == "UNKNOWN":
                            missing=[k.replace("_"," ") for k,v in coverage_detail.items() if v < 50]
                            text=f"Status: UNKNOWN\nTelemetry coverage: {coverage}%\n\nNot enough core evidence is available to call this stream good or bad yet."
                            if missing: text += "\n\nMissing/limited: " + ", ".join(missing)
                        elif live:
                            f=live[0]; text=f"Status: {status}\nTelemetry coverage: {coverage}%\n\nHealth finding: {f.title}\nConfidence: {f.confidence}%\n\n{f.explanation}\n\n"+"\n".join("- "+x for x in f.recommendations)
                        else:
                            text=f"Status: GOOD\nTelemetry coverage: {coverage}%\n\nNo strong fault pattern is currently detected in the last 30 seconds. Stream Doctor is still monitoring."
                        home.setProperty("StreamDoctor.LiveText",text); last_live_update=now
                    if addon.getSettingBool("notifications"):
                        for f in live:
                            if f.severity != "high" or f.confidence < 80: continue
                            prev=last_notice.get(f.code, -1e9)
                            if now-prev>=90:
                                xbmcgui.Dialog().notification("Stream Doctor", f.title, xbmcgui.NOTIFICATION_WARNING, 5000); last_notice[f.code]=now
                            break
        else:
            session=finish(session); active_source_key=""
        if monitor.waitForAbort(interval): break
    finish(session)
