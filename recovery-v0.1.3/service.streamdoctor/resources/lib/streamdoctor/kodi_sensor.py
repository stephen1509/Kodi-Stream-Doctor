from datetime import datetime, timezone
from .model import TelemetrySample
from .parsing import (as_int, first_number, parse_bitrate_kbps, parse_bitrate_mbps,
                      parse_cpu_usage, parse_frequency_mhz, parse_link_mbps, parse_percent, parse_refresh_hz, parse_temperature_c)
from .redaction import safe_source_label, safe_text_label, source_identity_key

LABELS = {
    "video_bitrate": "Player.Process(VideoLiveBitrate)",
    "audio_bitrate": "Player.Process(AudioLiveBitrate)",
    "audio_decoder": "Player.Process(AudioDecoder)",
    "audio_channels": "Player.Process(AudioChannels)",
    "audio_samplerate": "Player.Process(AudioSamplerate)",
    "video_queue": "Player.Process(VideoQueueLevel)",
    "video_queue_data": "Player.Process(VideoQueueDataLevel)",
    "audio_queue": "Player.Process(AudioQueueLevel)",
    "audio_queue_data": "Player.Process(AudioQueueDataLevel)",
    "video_decoder": "Player.Process(VideoDecoder)",
    "video_codec": "VideoPlayer.VideoCodec",
    "video_fps": "Player.Process(VideoFPS)",
    "video_width": "Player.Process(VideoWidth)",
    "video_height": "Player.Process(VideoHeight)",
    "scan_type": "Player.Process(VideoScanType)",
    "deint_method": "Player.Process(DeintMethod)",
    "pix_format": "Player.Process(PixFormat)",
    "cpu_usage": "System.CpuUsage",
    "cpu_freq": "System.CpuFrequency",
    "free_memory": "System.Memory(free.percent)",
    "free_memory_mb": "System.FreeMemory",
    "cpu_temp": "System.CPUTemperature",
    "temperature_units": "System.TemperatureUnits",
    "gpu_temp": "System.GPUTemperature",
    "gui_fps": "System.FPS",
    "network_link": "Network.LinkState",
    "internet_state": "System.InternetState",
    "screen": "System.ScreenResolution",
    "pvr_provider": "PVR.ActStreamProviderName",
    "player_path": "Player.Folderpath",
    "channel_name": "VideoPlayer.ChannelName",
    "stream_title": "Player.Title",
    "pvr_status": "PVR.ActStreamStatus",
    "pvr_signal": "PVR.ActStreamSignal",
    "pvr_snr": "PVR.ActStreamSnr",
    "pvr_ber": "PVR.ActStreamBer",
    "pvr_unc": "PVR.ActStreamUnc",
}

class KodiTelemetryReader:
    def __init__(self, xbmc_module, player): self.xbmc=xbmc_module; self.player=player
    def label(self, key):
        try: return self.xbmc.getInfoLabel(LABELS[key]) or ""
        except Exception: return ""
    def cond(self, expr):
        try: return bool(self.xbmc.getCondVisibility(expr))
        except Exception: return False
    def cond_optional(self, expr):
        try: return bool(self.xbmc.getCondVisibility(expr))
        except Exception: return None
    def get_time(self):
        try: return float(self.player.getTime())
        except Exception: return None
    def is_playing_video(self):
        try: return bool(self.player.isPlayingVideo())
        except Exception: return False
    def internet_connected(self, state_text=None):
        state=(self.label("internet_state") if state_text is None else str(state_text or "")).strip()
        if not state:
            return None
        try:
            connected=str(self.xbmc.getLocalizedString(13296) or "").strip()
            disconnected=str(self.xbmc.getLocalizedString(13297) or "").strip()
        except Exception:
            return None
        folded=state.casefold()
        if connected and folded == connected.casefold(): return True
        if disconnected and folded == disconnected.casefold(): return False
        return None
    def sample(self, monotonic_time, playing=None):
        vb=self.label("video_bitrate"); ab=self.label("audio_bitrate"); raw_path=self.label("player_path"); internet_state=self.label("internet_state")
        video_decoder=self.label("video_decoder"); audio_decoder=self.label("audio_decoder")
        pvr_provider=safe_text_label(self.label("pvr_provider")); channel_name=safe_text_label(self.label("channel_name")); stream_title=safe_text_label(self.label("stream_title"))
        playing_state=self.is_playing_video() if playing is None else bool(playing)
        hw_decoder=self.cond_optional("Player.Process(videohwdecoder)")
        audio_passthrough=self.cond_optional("Player.Passthrough")
        # Official labels are localized strings (Mb/s and Kb/s). The numeric part is stable.
        return TelemetrySample(
            t=monotonic_time, wall_time=datetime.now(timezone.utc).isoformat(), playing=playing_state, paused=self.cond("Player.Paused"),
            is_live=self.cond("Player.IsLive"), is_internet_stream=self.cond("Player.IsInternetStream"), is_livetv_content=self.cond("VideoPlayer.Content(LiveTV)"), caching=self.cond("Player.Caching"), playback_time_s=self.get_time(),
            video_bitrate_mbps=parse_bitrate_mbps(vb), audio_bitrate_kbps=parse_bitrate_kbps(ab), audio_decoder=audio_decoder, audio_channels=self.label("audio_channels"), audio_sample_rate_hz=as_int(self.label("audio_samplerate")), audio_passthrough=audio_passthrough,
            video_queue_pct=parse_percent(self.label("video_queue")), video_queue_data_pct=parse_percent(self.label("video_queue_data")),
            audio_queue_pct=parse_percent(self.label("audio_queue")), audio_queue_data_pct=parse_percent(self.label("audio_queue_data")),
            video_decoder=video_decoder, hw_decoder=hw_decoder, video_codec=self.label("video_codec"),
            video_fps=first_number(self.label("video_fps")), video_width=as_int(self.label("video_width")), video_height=as_int(self.label("video_height")),
            scan_type=self.label("scan_type"), deint_method=self.label("deint_method"), pixel_format=self.label("pix_format"),
            cpu_usage_pct=parse_cpu_usage(self.label("cpu_usage")), cpu_frequency_mhz=parse_frequency_mhz(self.label("cpu_freq")), free_memory_pct=parse_percent(self.label("free_memory")), free_memory_mb=first_number(self.label("free_memory_mb")),
            cpu_temp_c=parse_temperature_c(self.label("cpu_temp"), self.label("temperature_units")), gpu_temp_c=parse_temperature_c(self.label("gpu_temp"), self.label("temperature_units")), gui_fps=first_number(self.label("gui_fps")),
            network_link_state=self.label("network_link"), link_mbps=parse_link_mbps(self.label("network_link")), internet_state=safe_text_label(internet_state), internet_connected=self.internet_connected(internet_state),
            screen_resolution=self.label("screen"), refresh_hz=parse_refresh_hz(self.label("screen")), pvr_provider=pvr_provider, source_origin=safe_source_label(raw_path), source_key=source_identity_key(raw_path, channel_name, pvr_provider), channel_name=channel_name, stream_title=stream_title, pvr_status=safe_text_label(self.label("pvr_status")), pvr_signal=first_number(self.label("pvr_signal")), pvr_snr=first_number(self.label("pvr_snr")), pvr_ber=first_number(self.label("pvr_ber")), pvr_unc=first_number(self.label("pvr_unc")))
