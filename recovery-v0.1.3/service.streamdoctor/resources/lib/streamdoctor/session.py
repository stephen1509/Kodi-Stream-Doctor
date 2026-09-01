from collections import deque
from datetime import datetime, timezone
from typing import List
from .diagnose import diagnose
from .model import SessionReport, SystemContext, TelemetrySample
from .scoring import component_scores, overall_score, telemetry_coverage, health_status
from .parsing import median

class SessionAnalyzer:
    def __init__(self, context: SystemContext, max_samples=7200):
        self.context=context; self.samples=deque(maxlen=max_samples); self.started_at=datetime.now(timezone.utc).isoformat(); self._historical={}; self.marker_count=0; self._last_marker_t=None; self._last_marker_type=""; self.marker_types=[]
    def add(self, sample: TelemetrySample):
        self.samples.append(sample)
        if len(self.samples) >= 8:
            for f in diagnose(self.recent(30.0), self.context):
                old=self._historical.get(f.code)
                if old is None or f.confidence > old.confidence: self._historical[f.code]=f
    def mark_problem(self, issue_type="other"):
        self.marker_count += 1
        self._last_marker_type=issue_type or "other"
        self.marker_types.append(self._last_marker_type)
        if self.samples:
            self._last_marker_t=self.samples[-1].t
            for f in diagnose(self.recent(30.0), self.context, user_reported=True, user_issue=self._last_marker_type):
                old=self._historical.get(f.code)
                if old is None or f.confidence > old.confidence: self._historical[f.code]=f
    def recent(self, seconds=30.0) -> List[TelemetrySample]:
        if not self.samples: return []
        cutoff=self.samples[-1].t-seconds
        return [s for s in self.samples if s.t>=cutoff]
    def live_findings(self):
        user_reported=bool(self._last_marker_t is not None and self.samples and self.samples[-1].t-self._last_marker_t <= 15.0)
        return diagnose(self.recent(30.0), self.context, user_reported=user_reported, user_issue=(self._last_marker_type if user_reported else ""))
    def _metrics(self):
        data=list(self.samples)
        def stat(attr):
            vals=[getattr(x,attr) for x in data if getattr(x,attr) is not None]
            return {"min":min(vals),"median":median(vals),"max":max(vals)} if vals else None
        return {k:v for k,v in {
            "video_bitrate_mbps":stat("video_bitrate_mbps"),
            "audio_bitrate_kbps":stat("audio_bitrate_kbps"),
            "video_queue_data_pct":stat("video_queue_data_pct"),
            "audio_queue_data_pct":stat("audio_queue_data_pct"),
            "cpu_usage_pct":stat("cpu_usage_pct"),
            "free_memory_pct":stat("free_memory_pct"),
            "free_memory_mb":stat("free_memory_mb"),
            "cpu_temp_c":stat("cpu_temp_c"),
            "gpu_temp_c":stat("gpu_temp_c"),
            "video_fps":stat("video_fps"),
            "refresh_hz":stat("refresh_hz"),
            "link_mbps":stat("link_mbps"),
            "cpu_frequency_mhz":stat("cpu_frequency_mhz"),
            "gui_fps":stat("gui_fps"),
            "caching_sample_pct": (100.0*sum(1 for x in data if x.caching)/len(data)) if data else 0.0,
            "user_marker_count": self.marker_count,
            "user_marker_types": list(self.marker_types),
        }.items() if v is not None}
    def _source(self):
        data=list(self.samples)
        def mode(attr):
            vals=[getattr(x,attr) for x in data if getattr(x,attr)]
            return max(set(vals),key=vals.count) if vals else ""
        def bool_mode(attr):
            vals=[getattr(x,attr) for x in data if getattr(x,attr) is not None]
            if not vals: return None
            yes=sum(1 for v in vals if v)
            if yes * 2 == len(vals): return None
            return yes * 2 > len(vals)
        return {
            "pvr_provider":mode("pvr_provider"), "source_origin":mode("source_origin"), "channel_name":mode("channel_name"), "stream_title":mode("stream_title"), "video_codec":mode("video_codec"), "video_decoder":mode("video_decoder"),
            "audio_decoder":mode("audio_decoder"), "scan_type":mode("scan_type"), "deinterlace_method":mode("deint_method"), "hardware_decoder_active":bool_mode("hw_decoder"), "internet_connected":bool_mode("internet_connected"),
            "is_live":any(x.is_live for x in data), "is_internet_stream":any(x.is_internet_stream for x in data), "is_livetv_content":any(x.is_livetv_content for x in data),
            "max_width":max([x.video_width for x in data if x.video_width is not None] or [0]),
            "max_height":max([x.video_height for x in data if x.video_height is not None] or [0]),
        }
    def report(self):
        merged=dict(self._historical)
        for f in diagnose(list(self.samples), self.context):
            old=merged.get(f.code)
            if old is None or f.confidence > old.confidence: merged[f.code]=f
        findings=list(merged.values())
        order={"high":0,"medium":1,"low":2,"info":3}; findings.sort(key=lambda f:(order.get(f.severity,9),-f.confidence,f.code))
        data=list(self.samples)
        scores=component_scores(data, findings); overall=overall_score(scores)
        coverage_pct, coverage_detail=telemetry_coverage(data)
        status=health_status(findings,coverage_pct,coverage_detail)
        if status == "UNKNOWN": overall=None
        metrics=self._metrics(); metrics["telemetry_coverage_detail_pct"]=coverage_detail
        if status == "UNKNOWN":
            summary="Insufficient core telemetry to classify this stream confidently; no unsupported good/bad claim was made."
        elif not findings:
            summary="No strong evidence of a playback fault was detected in the captured telemetry."
        else:
            summary=findings[0].title + f" ({findings[0].confidence}% confidence)."
        return SessionReport(self.started_at, datetime.now(timezone.utc).isoformat(), len(self.samples), overall, scores, findings, self.context, summary, metrics, self._source(), status, coverage_pct)
