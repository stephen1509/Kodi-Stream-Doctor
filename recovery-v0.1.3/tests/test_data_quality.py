import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample,SystemContext
from streamdoctor.session import SessionAnalyzer
from streamdoctor.scoring import telemetry_coverage,health_status


def full(t,**kw):
    d=dict(t=t,playing=True,playback_time_s=t,video_bitrate_mbps=8,audio_bitrate_kbps=192,
           video_queue_data_pct=90,audio_queue_data_pct=90,cpu_usage_pct=25,free_memory_pct=60,
           video_decoder='ff-h264',hw_decoder=True,video_fps=50,refresh_hz=50,video_width=1920,video_height=1080)
    d.update(kw); return TelemetrySample(**d)

class DataQualityTests(unittest.TestCase):
    def test_full_healthy_stream_is_good(self):
        a=SessionAnalyzer(SystemContext())
        for i in range(30): a.add(full(i))
        r=a.report(); self.assertEqual(r.health_status,'GOOD'); self.assertGreaterEqual(r.telemetry_coverage_pct,95)
    def test_missing_core_telemetry_is_unknown_not_good(self):
        a=SessionAnalyzer(SystemContext())
        for i in range(30): a.add(TelemetrySample(t=i,playing=True,playback_time_s=i,video_fps=50,refresh_hz=50))
        r=a.report(); self.assertEqual(r.health_status,'UNKNOWN'); self.assertIsNone(r.health_score); self.assertLess(r.telemetry_coverage_pct,60)
    def test_known_bad_evidence_can_be_bad_even_with_some_missing_unrelated_signals(self):
        a=SessionAnalyzer(SystemContext())
        for i in range(20): a.add(full(i))
        for i in range(20,28): a.add(full(i,video_bitrate_mbps=.05,video_queue_data_pct=1,audio_queue_data_pct=0,caching=True))
        r=a.report(); self.assertEqual(r.health_status,'BAD'); self.assertIn('delivery_starvation',[f.code for f in r.findings])
    def test_coverage_never_uses_missing_as_zero_evidence(self):
        pct,detail=telemetry_coverage([TelemetrySample(t=0,playing=True)])
        self.assertEqual(pct,0); self.assertTrue(all(v==0 for v in detail.values()))
if __name__=='__main__': unittest.main()
