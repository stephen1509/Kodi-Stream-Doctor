import os, sys, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample, SystemContext
from streamdoctor.diagnose import diagnose, compatible_refresh


def sample(t, **kw):
    base=dict(t=t, playing=True, playback_time_s=t, video_bitrate_mbps=8.0,
              audio_bitrate_kbps=192.0, video_queue_data_pct=90,
              audio_queue_data_pct=90, cpu_usage_pct=25, free_memory_pct=60,
              video_width=1920, video_height=1080, video_fps=50,
              refresh_hz=50, hw_decoder=True, audio_passthrough=False)
    base.update(kw)
    return TelemetrySample(**base)


class FalsePositiveTests(unittest.TestCase):
    def codes(self, samples, ctx=None, **kwargs):
        return [f.code for f in diagnose(samples, ctx or SystemContext(), **kwargs)]

    def test_ten_gigabit_plan_does_not_create_network_fault_on_healthy_stream(self):
        c=self.codes([sample(i) for i in range(30)], SystemContext(internet_plan_mbps=10000))
        self.assertNotIn('wan_capacity_margin', c)
        self.assertNotIn('delivery_starvation', c)
        self.assertNotIn('plan_speed_not_explanation', c)

    def test_100_mbit_link_has_ample_margin_for_10_mbit_stream(self):
        c=self.codes([sample(i,video_bitrate_mbps=9.8,audio_bitrate_kbps=192) for i in range(30)],
                     SystemContext(adapter_link_mbps=[100]))
        self.assertNotIn('lan_capacity_margin', c)

    def test_multiple_active_adapter_speeds_are_not_guessed(self):
        # Without Kodi's link label we do not know which of these routes carries playback.
        c=self.codes([sample(i,video_bitrate_mbps=20) for i in range(30)],
                     SystemContext(adapter_link_mbps=[10,1000]))
        self.assertNotIn('lan_capacity_margin', c)

    def test_one_parsed_speed_among_multiple_active_adapters_is_still_ambiguous(self):
        c=self.codes([sample(i,video_bitrate_mbps=20) for i in range(30)],
                     SystemContext(adapter_names=['Ethernet','VPN'],adapter_link_mbps=[10]))
        self.assertNotIn('lan_capacity_margin', c)

    def test_high_temperature_without_load_is_not_called_thermal_problem(self):
        c=self.codes([sample(i,cpu_temp_c=95,cpu_usage_pct=20) for i in range(30)],
                     SystemContext(cpu_max_mhz=4000))
        self.assertNotIn('thermal_risk', c)

    def test_passthrough_without_audio_marker_is_not_blame(self):
        c=self.codes([sample(i,audio_passthrough=True) for i in range(30)])
        self.assertNotIn('audio_passthrough_risk', c)

    def test_low_bitrate_without_picture_quality_marker_is_not_blame(self):
        c=self.codes([sample(i,video_bitrate_mbps=1.0) for i in range(30)])
        self.assertNotIn('source_compression_risk', c)

    def test_common_integer_refresh_multiples(self):
        self.assertTrue(compatible_refresh(25,50))
        self.assertTrue(compatible_refresh(50,100))
        self.assertTrue(compatible_refresh(29.97,59.94))
        self.assertTrue(compatible_refresh(23.976,119.88))


if __name__=='__main__': unittest.main()
