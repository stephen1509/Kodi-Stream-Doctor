from .model import Finding, SessionReport
from .scoring import health_status


def _source_key(report):
    src=(report.get("source") or {}) if isinstance(report,dict) else report.source
    provider=(src.get("pvr_provider") if isinstance(src,dict) else "") or ""
    origin=(src.get("source_origin") if isinstance(src,dict) else "") or ""
    if provider: return "provider",provider
    # pvr:// origins are usually generic routing namespaces (for example
    # pvr://channels), not a specific upstream source. Without provider metadata,
    # do not make a historical source-attribution claim from that coarse label.
    if origin and origin != "local-or-kodi-managed" and not origin.lower().startswith("pvr://"):
        return "origin",origin
    return None,None

def _codes(report):
    fs=(report.get("findings") or []) if isinstance(report,dict) else report.findings
    return {f.get("code") if isinstance(f,dict) else f.code for f in fs}

def apply_history(report: SessionReport, previous_reports):
    kind,key=_source_key(report)
    if not key or "delivery_starvation" not in _codes(report): return report
    same=[]; other_healthy=[]
    for r in previous_reports:
        k2,key2=_source_key(r)
        if key2==key: same.append(r)
        elif key2 and "delivery_starvation" not in _codes(r): other_healthy.append(r)
    repeats=sum(1 for r in same if "delivery_starvation" in _codes(r))
    if len(same) < 2 or repeats < 2 or repeats/len(same) < 0.67: return report
    confidence=min(95,78 + min(10,repeats*3) + (5 if other_healthy else 0))
    label=("provider " if kind=="provider" else "source origin ")+key
    f=Finding("source_pattern","delivery","high",confidence,
              "Delivery failures repeatedly cluster around the same source",
              "Historical Stream Doctor reports show repeated delivery-starvation events for the same source while comparison evidence is " + ("available from other sources." if other_healthy else "still limited."),
              [f"{repeats} of {len(same)} previous reports for {label} contained delivery starvation."] + ([f"{len(other_healthy)} report(s) from other identifiable sources did not contain delivery starvation."] if other_healthy else []),
              ["Prefer an alternate source/provider for this channel before changing CPU, RAM or Kodi cache.", "Continue comparing the same channel across providers to strengthen or weaken this conclusion."],[])
    report.findings.append(f)
    order={"high":0,"medium":1,"low":2,"info":3}; report.findings.sort(key=lambda x:(order.get(x.severity,9),-x.confidence,x.code))
    # History strengthens source attribution but must not discard or recreate
    # current-session component evidence without the original samples.
    detail=(report.metrics or {}).get("telemetry_coverage_detail_pct") or {}
    report.health_status=health_status(report.findings,report.telemetry_coverage_pct,detail)
    report.summary=report.findings[0].title+f" ({report.findings[0].confidence}% confidence)."
    return report
