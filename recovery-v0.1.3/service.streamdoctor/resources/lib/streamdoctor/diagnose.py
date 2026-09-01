from typing import List, Sequence
from .model import Finding, SystemContext, TelemetrySample
from .parsing import median


def _vals(samples, attr):
    return [getattr(s, attr) for s in samples if getattr(s, attr) is not None]

def _max(samples, attr):
    v = _vals(samples, attr); return max(v) if v else None

def _min(samples, attr):
    v = _vals(samples, attr); return min(v) if v else None

def _avg(samples, attr):
    v = _vals(samples, attr); return sum(v)/len(v) if v else None

def _pct(samples, pred):
    if not samples: return 0.0
    return 100.0 * sum(1 for s in samples if pred(s)) / len(samples)

def _fmt(v, suffix=""):
    return "unknown" if v is None else f"{v:.1f}{suffix}"

def _sustained(samples, pred, threshold_s=0.5):
    start_t = None
    run_count = 0
    for s in samples:
        if pred(s):
            if start_t is None:
                start_t = s.t
                run_count = 1
            else:
                run_count += 1
            # Three consecutive samples protects high-rate telemetry from a
            # one-sample blip; two samples also suffice when they span the
            # requested wall-clock duration.
            if run_count >= 3 or (run_count >= 2 and s.t - start_t >= threshold_s):
                return True
        else:
            start_t = None
            run_count = 0
    return False

def _has_playback_stall(samples, threshold_s=1.5):
    start_t = None
    last_time = None
    for s in samples:
        if s.paused or s.playback_time_s is None:
            start_t = None; last_time = s.playback_time_s; continue
        if last_time is not None and abs(s.playback_time_s - last_time) < 0.08:
            if start_t is None: start_t = s.t
            if s.t - start_t >= threshold_s: return True
        else:
            start_t = None
        last_time = s.playback_time_s
    return False


def compatible_refresh(video_fps, refresh_hz):
    if not video_fps or not refresh_hz or video_fps <= 0: return None
    ratio = refresh_hz / video_fps
    nearest = round(ratio)
    if nearest < 1: return False
    return abs(ratio - nearest) <= 0.025


def diagnose(samples: Sequence[TelemetrySample], ctx: SystemContext, user_reported: bool = False, user_issue: str = "") -> List[Finding]:
    samples = [s for s in samples if s.playing]
    if not samples: return []
    findings: List[Finding] = []

    cpu_peak = _max(samples, "cpu_usage_pct")
    cpu_avg = _avg(samples, "cpu_usage_pct")
    free_mem_min = _min(samples, "free_memory_pct")
    free_mem_mb_min = _min(samples, "free_memory_mb")
    vq_min = _min(samples, "video_queue_data_pct")
    if vq_min is None: vq_min = _min(samples, "video_queue_pct")
    aq_min = _min(samples, "audio_queue_data_pct")
    if aq_min is None: aq_min = _min(samples, "audio_queue_pct")
    bitrate_med = median(_vals(samples, "video_bitrate_mbps"))
    bitrate_min = _min(samples, "video_bitrate_mbps")
    caching_pct = _pct(samples, lambda s: s.caching)
    hw_values = [s.hw_decoder for s in samples if s.hw_decoder is not None]
    hw = (sum(1 for x in hw_values if x) >= len(hw_values)/2) if hw_values else None
    width = max(_vals(samples, "video_width") or [0])
    height = max(_vals(samples, "video_height") or [0])
    fps = median(_vals(samples, "video_fps"))
    refresh = median(_vals(samples, "refresh_hz"))
    scan_values=[(s.scan_type or "").strip().lower() for s in samples if (s.scan_type or "").strip()]
    interlaced=bool(scan_values and sum(1 for x in scan_values if x.startswith("i")) >= len(scan_values)/2)
    deint_values=[(s.deint_method or "").strip() for s in samples if (s.deint_method or "").strip()]
    deint=deint_values[-1] if deint_values else ""
    internet_values=[s.internet_connected for s in samples if s.internet_connected is not None]
    def internet_outage_sample(s):
        return bool(s.is_internet_stream and s.internet_connected is False and (s.caching or (s.video_queue_data_pct is not None and s.video_queue_data_pct <= 8) or (s.video_queue_pct is not None and s.video_queue_pct <= 8)))
    internet_outage_overlap=sum(1 for s in samples if internet_outage_sample(s))
    internet_outage_sustained=_sustained(samples, internet_outage_sample, 0.5)
    sample_links = _vals(samples, "link_mbps")
    if sample_links:
        # Kodi's own link label is preferred because it represents the link Kodi sees.
        link = median(sample_links)
    elif len(ctx.adapter_link_mbps or []) == 1 and len(ctx.adapter_names or []) <= 1:
        # A single active Windows adapter is sufficiently unambiguous for a capacity warning.
        link = ctx.adapter_link_mbps[0]
    else:
        # Multiple active adapters require route-aware attribution; guessing would be unsafe.
        link = None
    stream_mbps = (bitrate_med or 0) + ((median(_vals(samples, "audio_bitrate_kbps")) or 0) / 1000.0)
    playback_stall = _has_playback_stall(samples)

    def starving_sample(s):
        return bool(s.caching or (s.video_queue_data_pct is not None and s.video_queue_data_pct <= 8) or (s.video_queue_data_pct is None and s.video_queue_pct is not None and s.video_queue_pct <= 8) or (s.audio_queue_data_pct is not None and s.audio_queue_data_pct <= 5) or (s.audio_queue_data_pct is None and s.audio_queue_pct is not None and s.audio_queue_pct <= 5))
    starvation_seen = any(starving_sample(s) for s in samples)
    starvation = _sustained(samples, starving_sample, 0.5) or (user_reported and starvation_seen)
    collapse_threshold = max(0.15, bitrate_med * 0.12) if bitrate_med and bitrate_med >= 1.0 else None
    collapse_seen = bool(collapse_threshold is not None and any(s.video_bitrate_mbps is not None and s.video_bitrate_mbps <= collapse_threshold for s in samples))
    bitrate_collapse = bool(collapse_threshold is not None and (_sustained(samples, lambda s: s.video_bitrate_mbps is not None and s.video_bitrate_mbps <= collapse_threshold, 0.5) or (user_reported and collapse_seen)))
    cpu_known = cpu_peak is not None
    mem_known = free_mem_min is not None
    cpu_comfortable = cpu_known and cpu_peak < 80
    mem_comfortable = mem_known and free_mem_min > 10

    if starvation and (bitrate_collapse or caching_pct >= 5):
        evidence = [f"Caching observed in {caching_pct:.1f}% of playback samples."]
        if vq_min is not None: evidence.append(f"Video queue/data level reached {vq_min:.1f}%.")
        if aq_min is not None: evidence.append(f"Audio queue/data level reached {aq_min:.1f}%.")
        if bitrate_med is not None and bitrate_min is not None: evidence.append(f"Video live bitrate median {bitrate_med:.1f} Mb/s, minimum {bitrate_min:.1f} Mb/s.")
        if cpu_peak is not None: evidence.append(f"CPU peak was {cpu_peak:.1f}%.")
        if free_mem_min is not None: evidence.append(f"Minimum free memory was {free_mem_min:.1f}%.")
        if cpu_comfortable and mem_comfortable:
            confidence = 88 if bitrate_collapse else 82
            context_text = "CPU and memory were also measured and remained comfortable, making a local compute bottleneck unlikely for this event."
        elif cpu_known or mem_known:
            confidence = 82 if bitrate_collapse else 78
            context_text = "The queue/cache evidence establishes media-delivery starvation, but device context is mixed or incomplete, so Stream Doctor will not pretend this alone identifies the upstream component."
        else:
            confidence = 78 if bitrate_collapse else 74
            context_text = "The queue/cache evidence establishes media-delivery starvation, but CPU/RAM telemetry is missing, so those components are not ruled out independently."
        findings.append(Finding(
            "delivery_starvation", "delivery", "high", confidence,
            "Playback was starved of incoming media data",
            "Kodi's media queues/cache ran low and/or live bitrate collapsed. " + context_text + " The starvation can originate from the stream server/CDN, Internet path, router/Wi-Fi/Ethernet, input-stream layer, or another upstream interruption.",
            evidence,
            ["Compare another source/provider for the same channel.", "Run a deliberate network stability diagnostic (latency/jitter/loss) rather than a bulk speed test during playback.", "If the problem affects only one provider while other streams remain healthy, prefer changing source/provider before changing hardware or Kodi cache."],
            ["More RAM is not supported by this event's evidence." if mem_comfortable else "", "A faster CPU is not supported by this event's evidence." if cpu_comfortable else ""]
        ))

    if starvation and cpu_peak is not None and cpu_peak >= 94:
        findings.append(Finding(
            "concurrent_cpu_pressure", "device", "medium", 72,
            "CPU saturation occurred at the same time as media starvation",
            "The stream ran short of queued media while CPU usage was also near saturation. Because two problems overlap, the telemetry cannot honestly assign the visible symptom to CPU alone. Delivery should be stabilized and the same stream retested before considering a hardware conclusion.",
            [f"CPU peak {cpu_peak:.1f}%.", f"Caching observed in {caching_pct:.1f}% of samples."] + ([f"Video queue/data minimum {vq_min:.1f}%."] if vq_min is not None else []),
            ["Fix or isolate the delivery-starvation path first, then repeat the same stream and see whether CPU saturation remains.", "Check hardware decoding status, but do not buy a CPU solely from this overlapping event."],
            []
        ))

    if starvation and internet_outage_overlap >= 2 and (internet_outage_sustained or user_reported):
        findings.append(Finding(
            "kodi_internet_unavailable", "network", "high", 88,
            "Kodi reported no Internet connectivity during an Internet-stream starvation event",
            "The player starved and Kodi's own system Internet condition was false during Internet-stream playback. This is stronger evidence for a local-network/router/ISP connectivity interruption than for a weak CPU or a single bad channel source, although the exact failing hop still needs isolation.",
            [f"Kodi System.InternetState was false in {internet_outage_overlap} starvation-overlap samples.", "The item was identified as an Internet stream."] + ([f"Video queue/data minimum {vq_min:.1f}%."] if vq_min is not None else []),
            ["Check whether other Internet services on the same device failed at the same time.", "Check router/ONT/modem and Ethernet/Wi-Fi stability before changing Kodi cache or buying faster hardware."],
            ["A CPU upgrade is not supported by an Internet-connectivity failure."]
        ))

    if cpu_peak is not None and cpu_peak >= 94 and not starvation and (playback_stall or user_reported):
        findings.append(Finding(
            "cpu_overload", "device", "high", 86,
            "CPU saturation is limiting playback",
            "Playback input remained available while CPU usage reached saturation" + (" during a user-marked problem window." if user_reported and not playback_stall else " while playback time stopped advancing.") + " This pattern is consistent with decode/render/system load rather than insufficient stream delivery.",
            [f"CPU average {_fmt(cpu_avg, '%')}; peak {_fmt(cpu_peak, '%')}.", f"Video queue minimum {_fmt(vq_min, '%')}."],
            ["Close CPU-heavy background programs and retest.", "Verify hardware video acceleration is enabled and actually active.", "If hardware decode is unavailable for this codec/profile, try a lower-resolution/lower-frame-rate or more compatible source before upgrading hardware."],
            ["A faster Internet plan is not supported when the input queue remains healthy."]
        ))

    demanding = (height >= 2160 and (fps or 0) >= 50) or (height >= 1080 and (fps or 0) >= 50)
    if hw is False and demanding and (cpu_peak or 0) >= 75 and (playback_stall or user_reported) and not starvation:
        findings.append(Finding(
            "software_decode_pressure", "decoder", "high", 90,
            "Demanding video stalled while hardware decoding was inactive",
            "The stream is demanding, the hardware-decoder flag is off, CPU pressure is high, and a playback problem was directly observed" + (" by the user marker." if user_reported and not playback_stall else " as a playback-time stall.") + " This strongly points to a decoder/driver/capability/configuration path rather than source bandwidth alone.",
            [f"Video {width}x{height} at {_fmt(fps, ' fps')}.", f"CPU peak {_fmt(cpu_peak, '%')}.", "Kodi did not report an active hardware video decoder."] + (["GPU: " + ", ".join(ctx.gpu_names)] if ctx.gpu_names else []) + (["Installed GPU driver version(s): " + ", ".join(ctx.gpu_driver_versions)] if ctx.gpu_driver_versions else []) + [("User marked a visible/audible playback problem in this window." if user_reported and not playback_stall else "Playback-time stall was observed.")],
            ["Check Kodi hardware-acceleration settings for the platform.", "Check the GPU/video driver and codec support.", "Retest with a 1080p or lower-frame-rate source; if that succeeds, hardware decode capability is the likely limit."],
            ["Do not buy more RAM unless separate memory-pressure evidence exists."]
        ))
    elif hw is False and demanding and (cpu_peak or 0) >= 85:
        findings.append(Finding(
            "software_decode_headroom", "decoder", "medium", 70,
            "Software decoding is using substantial CPU headroom",
            "Kodi reports no active hardware video decoder for a demanding stream and CPU load is high, but the captured telemetry does not prove a playback stall. Treat this as a risk, not a confirmed cause.",
            [f"Video {width}x{height} at {_fmt(fps, ' fps')}.", f"CPU peak {_fmt(cpu_peak, '%')}.", "No confirmed playback-time stall in this window."],
            ["Verify hardware acceleration and driver/codec support before problems occur.", "Do not replace hardware based on this risk finding alone."], []
        ))

    memory_low = False
    if free_mem_mb_min is not None and free_mem_mb_min <= 512:
        memory_low = True
    elif free_mem_min is not None and free_mem_min <= 5:
        # On large-memory systems a small percentage can still represent several
        # gigabytes of available RAM. If absolute MB is known, require <= 1 GiB.
        memory_low = free_mem_mb_min is None or free_mem_mb_min <= 1024
    if memory_low:
        memory_problem_observed = playback_stall or user_reported
        findings.append(Finding(
            "memory_pressure", "memory", "medium" if memory_problem_observed else "low", 82 if memory_problem_observed else 70,
            "Very low free memory coincided with a playback problem" if memory_problem_observed else "Very low free memory leaves little playback headroom",
            ("Available memory was very low in the same window as an observed/reported playback problem, so paging or allocation pressure is a plausible contributor." if memory_problem_observed else "Available memory was very low, but no playback problem was established in this window. Treat this as a headroom risk rather than a proven cause."),
            ([f"Minimum free memory {free_mem_min:.1f}%."] if free_mem_min is not None else []) + ([f"Minimum free memory {free_mem_mb_min:.0f} MB."] if free_mem_mb_min is not None else []) + (["A playback stall or user problem marker was present in the same window."] if memory_problem_observed else ["No playback stall or user problem marker was present in the same window."]),
            ["Close memory-heavy background applications and retest.", "Check whether memory pressure persists across multiple streams.", "Only consider adding RAM if the pressure is repeatable while playback problems occur."], []
        ))

    # Audio-only starvation: audio queue collapses while the video queue remains healthy.
    audio_starvation_seen = aq_min is not None and aq_min <= 5 and vq_min is not None and vq_min >= 50 and caching_pct < 2
    audio_starvation_sustained = _sustained(samples, lambda s: ((s.audio_queue_data_pct if s.audio_queue_data_pct is not None else s.audio_queue_pct) is not None and (s.audio_queue_data_pct if s.audio_queue_data_pct is not None else s.audio_queue_pct) <= 5 and (s.video_queue_data_pct if s.video_queue_data_pct is not None else s.video_queue_pct) is not None and (s.video_queue_data_pct if s.video_queue_data_pct is not None else s.video_queue_pct) >= 50 and not s.caching), 0.5)
    if audio_starvation_seen and (audio_starvation_sustained or user_reported):
        findings.append(Finding(
            "audio_queue_starvation", "audio", "high", 83,
            "The audio path starved while video delivery remained healthy",
            "Kodi's audio queue fell to an empty/near-empty state while the video queue retained data. That isolates the problem more toward the audio track, demux/decoder path, or source audio delivery than a whole-stream bandwidth failure.",
            [f"Audio queue/data minimum {aq_min:.1f}%.", f"Video queue/data minimum {vq_min:.1f}%.", f"General caching observed in only {caching_pct:.1f}% of samples."],
            ["Try another audio track or another source for the same channel if available.", "If the problem follows one source/track, prefer changing the source before changing Internet or RAM settings.", "If queues stay healthy during a reported sound problem, test audio passthrough/output settings separately."], []
        ))

    passthrough_values=[s.audio_passthrough for s in samples if s.audio_passthrough is not None]
    passthrough=bool(passthrough_values and sum(1 for x in passthrough_values if x) > len(passthrough_values)/2)
    if user_reported and user_issue in ("audio","avsync") and passthrough and (aq_min is None or aq_min >= 40) and not starvation:
        findings.append(Finding(
            "audio_passthrough_risk", "audio", "medium", 66,
            "Audio output/passthrough is a plausible contributor",
            "You marked an audio/A-V problem while Kodi's media queues remained healthy and audio passthrough was active. This does not prove passthrough is the cause, but it moves the investigation downstream toward HDMI/AVR/audio-driver/output configuration.",
            ["User marked an audio or A/V-sync problem.", "Audio/video media queues did not show starvation.", "Kodi reported audio passthrough active."],
            ["Temporarily test the same stream with passthrough disabled, then compare.", "Check the selected Kodi audio output device and Windows/Android audio path before changing network settings."], []
        ))

    pvr_ber=_max(samples,"pvr_ber"); pvr_unc=_max(samples,"pvr_unc"); pvr_signal=_min(samples,"pvr_signal")
    pvr_error=bool((pvr_ber or 0)>0 or (pvr_unc or 0)>0 or (pvr_signal is not None and 0 <= pvr_signal < 30))
    if pvr_error and (user_reported or starvation):
        ev=[]
        if pvr_signal is not None: ev.append(f"PVR signal quality reached {pvr_signal:.1f}.")
        if pvr_ber is not None: ev.append(f"PVR BER reported {pvr_ber:.0f}.")
        if pvr_unc is not None: ev.append(f"PVR UNC reported {pvr_unc:.0f}.")
        findings.append(Finding(
            "pvr_signal_problem", "delivery", "high", 88,
            "The PVR input itself reports signal/error problems",
            "Kodi's active PVR stream telemetry reports poor signal quality and/or transport errors. For tuner-backed Live TV this is stronger evidence than generic Internet or CPU guesses.",
            ev, ["Investigate the PVR/tuner/input signal path, backend and cabling/antenna as applicable.", "Do not treat this as a CPU/RAM problem unless separate device-pressure evidence also appears."], []
        ))

    if user_reported and user_issue == "quality" and bitrate_med is not None:
        very_low = (height >= 2160 and bitrate_med < 5.0) or (height >= 1080 and bitrate_med < 1.5) or (height >= 720 and bitrate_med < 0.7)
        if very_low:
            findings.append(Finding(
                "source_compression_risk", "delivery", "medium", 65,
                "The source bitrate is unusually low for the displayed resolution",
                "You marked poor picture quality and the live bitrate is extremely low for the frame size. Codec efficiency and scene complexity vary, so this is evidence of heavy source compression rather than a definitive perceptual-quality measurement.",
                [f"Resolution up to {width}x{height}; median live video bitrate {bitrate_med:.2f} Mb/s."],
                ["Compare a higher-bitrate source for the same channel.", "Do not buy faster hardware solely for a low-bitrate/compressed source; the device cannot restore detail that is absent upstream."], []
            ))

    if user_reported and user_issue in ("video", "quality") and interlaced and deint:
        d=deint.lower()
        if d in ("none", "off", "disabled") or "none" in d or "disabled" in d:
            findings.append(Finding(
                "deinterlace_disabled", "display", "medium", 82,
                "Interlaced video was reported problematic while deinterlacing appears disabled",
                "The stream is identified as interlaced and Kodi reports a disabled/no deinterlacing method in the same user-marked picture-problem window. This can cause combing or motion artifacts independently of Internet buffering.",
                [f"Scan type: {scan_values[-1] if scan_values else 'interlaced'}.", f"Deinterlace method: {deint}."],
                ["Review Kodi's deinterlacing/video processing setting for this content and retest the same channel.", "Do not change Internet speed or buffer settings solely for interlace artifacts when delivery queues remain healthy."], []
            ))

    compat = compatible_refresh(fps, refresh)
    if compat is False:
        findings.append(Finding(
            "refresh_mismatch", "display", "medium", 84,
            "Video frame rate and display refresh rate do not match cleanly",
            "A non-integer frame-to-refresh cadence can create regular judder even when network delivery and decoding are healthy.",
            [f"Video approximately {_fmt(fps, ' fps')}; display approximately {_fmt(refresh, ' Hz')}."],
            ["Enable or review Kodi's Adjust display refresh rate setting.", "Use a display mode that is an integer multiple of the content frame rate when supported."],
            ["Increasing the network buffer will not correct refresh-rate judder."]
        ))

    temp_peak = max([x for x in (_max(samples, "cpu_temp_c"), _max(samples, "gpu_temp_c")) if x is not None] or [0])
    current_mhz = _min(samples, "cpu_frequency_mhz")
    throttling_evidence = bool(ctx.cpu_max_mhz and current_mhz and current_mhz < ctx.cpu_max_mhz * 0.60 and (cpu_peak or 0) >= 85)
    if temp_peak >= 90 and (throttling_evidence or (cpu_peak or 0) >= 90):
        findings.append(Finding(
            "thermal_risk", "device", "medium", 75 if not throttling_evidence else 88,
            "High temperature may be reducing sustained performance",
            "High temperature occurred under heavy load" + (" together with a large clock-frequency reduction." if throttling_evidence else ". Temperature alone does not prove throttling, so this remains a risk finding."),
            [f"Peak reported temperature {temp_peak:.1f} °C."] + ([f"Observed CPU frequency {current_mhz:.0f} MHz vs reported max {ctx.cpu_max_mhz:.0f} MHz."] if throttling_evidence else []),
            ["Improve device cooling/airflow and retest the same stream.", "Check Windows/OS power mode if clocks remain unexpectedly low."], []
        ))

    plan = ctx.internet_plan_mbps or None
    capacity = ctx.known_capacity_mbps or None
    if stream_mbps > 0:
        if link and link < stream_mbps * 1.5:
            capacity_problem = starvation or user_reported
            findings.append(Finding(
                "lan_capacity_margin", "network", "high" if capacity_problem else "medium", 91 if capacity_problem else 78,
                "Local network link has too little capacity margin",
                "The active link speed is close to the media bitrate. Protocol overhead and normal bitrate bursts can exhaust that margin.",
                [f"Approximate stream bitrate {stream_mbps:.1f} Mb/s; link {link:.1f} Mb/s."],
                ["Check Ethernet negotiation/cable/switch or Wi-Fi link quality before buying a faster Internet plan."], []
            ))
        if capacity and capacity < stream_mbps * 1.5:
            capacity_problem = starvation or user_reported
            findings.append(Finding(
                "wan_capacity_margin", "network", "high" if capacity_problem else "medium", 90 if capacity_problem else 78,
                "Measured Internet capacity has too little margin for this stream",
                "A deliberate speed test result is close to the media bitrate, leaving insufficient headroom for peaks and competing traffic.",
                [f"Approximate stream bitrate {stream_mbps:.1f} Mb/s; known tested capacity {capacity:.1f} Mb/s."],
                ["Retest the Internet connection while Kodi is idle.", "Investigate ISP/router/Wi-Fi capacity before changing Kodi cache."], []
            ))
        elif plan and plan >= stream_mbps * 8 and starvation:
            # Subscription speed cannot prove delivered quality; deliberately weak conclusion.
            findings.append(Finding(
                "plan_speed_not_explanation", "network", "info", 95,
                "Subscribed Internet speed is not, by itself, the explanation",
                "The nominal service tier has ample raw capacity for the observed stream bitrate. Short outages, jitter, packet loss, routing, Wi-Fi/LAN problems or the source server can still cause starvation.",
                [f"Plan {plan:.0f} Mb/s vs stream around {stream_mbps:.1f} Mb/s."],
                ["Measure stability and the actual path instead of upgrading the headline plan solely because of this event."], []
            ))

    # Remove blank exclusions and sort high-confidence/severity first.
    for f in findings: f.exclusions = [x for x in f.exclusions if x]
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda f: (order.get(f.severity, 9), -f.confidence, f.code))
    return findings
