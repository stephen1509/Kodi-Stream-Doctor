from typing import Dict, Sequence
from .model import Finding, TelemetrySample


def component_scores(samples: Sequence[TelemetrySample], findings: Sequence[Finding]) -> Dict[str, int]:
    data=[s for s in samples if s.playing]
    def any_value(*attrs):
        return any(any(getattr(s,a) is not None and getattr(s,a) != "" for a in attrs) for s in data)
    supported={
        "delivery": any_value("video_bitrate_mbps","video_queue_data_pct","video_queue_pct"),
        "network": any_value("link_mbps") or any(s.internet_connected is False for s in data),
        "device": any_value("cpu_usage_pct","cpu_temp_c","gpu_temp_c","cpu_frequency_mhz"),
        "memory": any_value("free_memory_pct","free_memory_mb"),
        "decoder": any_value("hw_decoder","video_decoder"),
        "display": any_value("video_fps","refresh_hz"),
        "audio": any_value("audio_bitrate_kbps","audio_queue_data_pct","audio_queue_pct","audio_decoder"),
    }
    # A component is only scored if the session contained relevant evidence.
    # Missing telemetry is omitted rather than silently represented as 100/100.
    scores={name:100 for name,known in supported.items() if known}
    penalty = {"high": 55, "medium": 30, "low": 15, "info": 0}
    for f in findings:
        if f.category not in supported:
            continue
        scores.setdefault(f.category,100)  # the finding itself is evidence for that layer
        scores[f.category] = max(0, scores[f.category] - int(penalty.get(f.severity, 10) * max(0.4, f.confidence / 100.0)))
    return scores


def overall_score(scores: Dict[str, int]) -> int:
    if not scores: return 0
    vals = list(scores.values())
    weighted_avg = sum(vals) / len(vals)
    # A single critical layer should materially affect overall health without hiding other healthy layers.
    return int(round(0.55 * weighted_avg + 0.45 * min(vals)))


def telemetry_coverage(samples: Sequence[TelemetrySample]):
    """Return overall core-telemetry coverage and per-signal percentages.

    Coverage measures whether evidence exists, not whether the values are healthy.  This
    prevents unsupported/missing InfoLabels from being mistaken for a healthy stream.
    """
    data=[s for s in samples if s.playing]
    if not data:
        return 0, {}
    checks={
        "playback_time": lambda s: s.playback_time_s is not None,
        "video_bitrate": lambda s: s.video_bitrate_mbps is not None,
        "video_queue": lambda s: s.video_queue_data_pct is not None or s.video_queue_pct is not None,
        "audio_queue": lambda s: s.audio_queue_data_pct is not None or s.audio_queue_pct is not None,
        "cpu": lambda s: s.cpu_usage_pct is not None,
        "memory": lambda s: s.free_memory_pct is not None,
        "decoder": lambda s: s.hw_decoder is not None or bool(s.video_decoder),
        "video_fps": lambda s: s.video_fps is not None,
        "display_refresh": lambda s: s.refresh_hz is not None,
    }
    detail={name: round(100.0*sum(1 for s in data if pred(s))/len(data),1) for name,pred in checks.items()}
    return int(round(sum(detail.values())/len(detail))), detail


def health_status(findings: Sequence[Finding], coverage_pct: int, coverage_detail=None) -> str:
    # A supported high-confidence bad finding can still be valid even when unrelated
    # telemetry is missing, so known-bad evidence takes precedence over UNKNOWN.
    if any(f.severity == "high" and f.confidence >= 80 for f in findings):
        return "BAD"
    coverage_detail=coverage_detail or {}
    delivery_ok=coverage_detail.get("video_bitrate",0) >= 50 and coverage_detail.get("video_queue",0) >= 50
    if coverage_pct < 60 or not delivery_ok:
        return "UNKNOWN"
    if any(f.severity in ("high","medium") for f in findings):
        return "DEGRADED"
    return "GOOD"
