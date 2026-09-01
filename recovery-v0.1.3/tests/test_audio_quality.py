import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample,SystemContext
from streamdoctor.diagnose import diagnose

def base(t,**kw):
    x=dict(t=t,playing=True,playback_time_s=t,video_bitrate_mbps=8,audio_bitrate_kbps=192,video_queue_data_pct=90,audio_queue_data_pct=90,cpu_usage_pct=25,free_memory_pct=60,video_width=1920,video_height=1080,video_fps=50,refresh_hz=50,hw_decoder=True,audio_passthrough=False)
    x.update(kw);return TelemetrySample(**x)
class AudioQualityTests(unittest.TestCase):
    def codes(self,samples,**kw): return [x.code for x in diagnose(samples,SystemContext(),**kw)]
    def test_audio_only_starvation(self):
        self.assertIn('audio_queue_starvation',self.codes([base(i,audio_queue_data_pct=1,video_queue_data_pct=90) for i in range(20)]))
    def test_passthrough_risk_needs_user_audio_marker(self):
        x=[base(i,audio_passthrough=True) for i in range(20)]
        self.assertNotIn('audio_passthrough_risk',self.codes(x))
        self.assertIn('audio_passthrough_risk',self.codes(x,user_reported=True,user_issue='audio'))
    def test_low_bitrate_quality_advisory_requires_marker(self):
        x=[base(i,video_bitrate_mbps=1.0) for i in range(20)]
        self.assertNotIn('source_compression_risk',self.codes(x))
        self.assertIn('source_compression_risk',self.codes(x,user_reported=True,user_issue='quality'))
    def test_pvr_error(self):
        x=[base(i,pvr_ber=5,pvr_signal=20) for i in range(20)]
        self.assertIn('pvr_signal_problem',self.codes(x,user_reported=True,user_issue='freeze'))
if __name__=='__main__':unittest.main()
