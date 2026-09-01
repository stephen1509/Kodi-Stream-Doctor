import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,"service.streamdoctor","resources","lib"))
from streamdoctor.model import TelemetrySample,SystemContext
from streamdoctor.session import SessionAnalyzer

def sample(t, bad=False):
    return TelemetrySample(t=t,playing=True,playback_time_s=t,video_bitrate_mbps=.05 if bad else 8,video_queue_data_pct=0 if bad else 90,audio_queue_data_pct=0 if bad else 90,caching=bad,cpu_usage_pct=30,free_memory_pct=60,video_fps=50,refresh_hz=50,hw_decoder=True,video_width=1920,video_height=1080)
class SessionTests(unittest.TestCase):
    def test_session_sample_buffer_is_bounded(self):
        a=SessionAnalyzer(SystemContext(),max_samples=10)
        for i in range(25):
            a.add(TelemetrySample(t=float(i),playing=True,video_bitrate_mbps=8,video_queue_data_pct=90,audio_queue_data_pct=90,cpu_usage_pct=20,free_memory_pct=70,hw_decoder=True,video_fps=50,refresh_hz=50))
        self.assertEqual(len(a.samples),10)
        self.assertEqual(a.samples[0].t,15.0)

    def test_brief_fault_survives_long_healthy_tail(self):
        a=SessionAnalyzer(SystemContext(),max_samples=10000)
        for i in range(20): a.add(sample(i))
        for i in range(20,30): a.add(sample(i,True))
        for i in range(30,400): a.add(sample(i))
        self.assertIn("delivery_starvation",[f.code for f in a.report().findings])
    def test_healthy_report(self):
        a=SessionAnalyzer(SystemContext())
        for i in range(50): a.add(sample(i))
        r=a.report();self.assertEqual(r.findings,[]);self.assertEqual(r.health_score,100);self.assertEqual(r.health_status,'GOOD')
if __name__=="__main__":unittest.main()
