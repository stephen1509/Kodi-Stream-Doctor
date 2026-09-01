from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class TelemetrySample:
    t: float
    wall_time: str = ""
    playing: bool = False
    paused: bool = False
    is_live: bool = False
    is_internet_stream: bool = False
    is_livetv_content: bool = False
    caching: bool = False
    playback_time_s: Optional[float] = None
    video_bitrate_mbps: Optional[float] = None
    audio_bitrate_kbps: Optional[float] = None
    audio_decoder: str = ""
    audio_channels: str = ""
    audio_sample_rate_hz: Optional[int] = None
    audio_passthrough: Optional[bool] = None
    video_queue_pct: Optional[float] = None
    video_queue_data_pct: Optional[float] = None
    audio_queue_pct: Optional[float] = None
    audio_queue_data_pct: Optional[float] = None
    video_decoder: str = ""
    hw_decoder: Optional[bool] = None
    video_codec: str = ""
    video_fps: Optional[float] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None
    scan_type: str = ""
    deint_method: str = ""
    pixel_format: str = ""
    cpu_usage_pct: Optional[float] = None
    cpu_frequency_mhz: Optional[float] = None
    free_memory_pct: Optional[float] = None
    free_memory_mb: Optional[float] = None
    cpu_temp_c: Optional[float] = None
    gpu_temp_c: Optional[float] = None
    gui_fps: Optional[float] = None
    network_link_state: str = ""
    link_mbps: Optional[float] = None
    internet_state: str = ""
    internet_connected: Optional[bool] = None
    screen_resolution: str = ""
    refresh_hz: Optional[float] = None
    pvr_provider: str = ""
    source_origin: str = ""
    source_key: str = ""
    channel_name: str = ""
    stream_title: str = ""
    pvr_status: str = ""
    pvr_signal: Optional[float] = None
    pvr_snr: Optional[float] = None
    pvr_ber: Optional[float] = None
    pvr_unc: Optional[float] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SystemContext:
    platform: str = "unknown"
    kodi_version: str = ""
    os_version: str = ""
    cpu_name: str = ""
    cpu_cores: Optional[int] = None
    logical_processors: Optional[int] = None
    cpu_max_mhz: Optional[float] = None
    total_ram_gb: Optional[float] = None
    gpu_names: List[str] = field(default_factory=list)
    gpu_driver_versions: List[str] = field(default_factory=list)
    gpu_driver_dates: List[str] = field(default_factory=list)
    adapter_names: List[str] = field(default_factory=list)
    adapter_driver_versions: List[str] = field(default_factory=list)
    adapter_driver_dates: List[str] = field(default_factory=list)
    adapter_link_mbps: List[float] = field(default_factory=list)
    adapter_rx_errors: Optional[int] = None
    adapter_tx_errors: Optional[int] = None
    adapter_rx_discards: Optional[int] = None
    adapter_tx_discards: Optional[int] = None
    internet_plan_mbps: Optional[float] = None
    known_capacity_mbps: Optional[float] = None
    power_plan: str = ""
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Finding:
    code: str
    category: str
    severity: str
    confidence: int
    title: str
    explanation: str
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SessionReport:
    started_at: str
    ended_at: str
    sample_count: int
    health_score: Optional[int]
    component_scores: Dict[str, int]
    findings: List[Finding]
    context: SystemContext
    summary: str
    metrics: Dict[str, object] = field(default_factory=dict)
    source: Dict[str, object] = field(default_factory=dict)
    health_status: str = "UNKNOWN"
    telemetry_coverage_pct: int = 0

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["findings"] = [f.to_dict() for f in self.findings]
        return d
