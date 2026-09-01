import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample,SystemContext
from streamdoctor.session import SessionAnalyzer
class MarkerTests(unittest.TestCase):
    def test_user_marker_can_corroborate_cpu_decode_problem(self):
        a=SessionAnalyzer(SystemContext())
        for i in range(20):
            a.add(TelemetrySample(t=i,playing=True,playback_time_s=i,video_bitrate_mbps=20,video_queue_data_pct=90,audio_queue_data_pct=90,cpu_usage_pct=98,free_memory_pct=60,video_width=3840,video_height=2160,video_fps=60,refresh_hz=60,hw_decoder=False))
        self.assertNotIn('software_decode_pressure',[f.code for f in a.live_findings()])
        a.mark_problem("video")
        self.assertIn('software_decode_pressure',[f.code for f in a.live_findings()])
        self.assertEqual(a.report().metrics['user_marker_count'],1)
if __name__=='__main__': unittest.main()
