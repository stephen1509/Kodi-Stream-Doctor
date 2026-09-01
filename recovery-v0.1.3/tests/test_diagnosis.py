import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample,SystemContext
from streamdoctor.diagnose import diagnose,compatible_refresh

def s(t,**kw):
    base=dict(playing=True,playback_time_s=t,video_bitrate_mbps=8,video_queue_data_pct=90,audio_queue_data_pct=90,cpu_usage_pct=30,free_memory_pct=60,video_fps=50,refresh_hz=50,video_width=1920,video_height=1080,hw_decoder=True)
    base.update(kw);return TelemetrySample(t=t,**base)
class DiagnosisTests(unittest.TestCase):
    def codes(self,x,ctx=None): return [f.code for f in diagnose(x,ctx or SystemContext())]
    def test_healthy(self): self.assertEqual(self.codes([s(i) for i in range(30)]),[])
    def test_delivery_starvation(self):
        x=[s(i) for i in range(20)]+[s(20+i,video_bitrate_mbps=.05,video_queue_data_pct=2,audio_queue_data_pct=0,caching=True) for i in range(5)]
        self.assertIn('delivery_starvation',self.codes(x))
    def test_cpu_overload(self):
        x=[s(i,cpu_usage_pct=98,video_queue_data_pct=90,playback_time_s=10) for i in range(20)]
        self.assertIn('cpu_overload',self.codes(x))
    def test_software_decode(self):
        x=[s(i,cpu_usage_pct=98,hw_decoder=False,video_height=2160,video_width=3840,video_fps=60,refresh_hz=60,playback_time_s=10) for i in range(20)]
        c=self.codes(x);self.assertIn('software_decode_pressure',c);self.assertIn('cpu_overload',c)
    def test_memory(self): self.assertIn('memory_pressure',self.codes([s(i,free_memory_pct=3) for i in range(20)]))
    def test_refresh(self):
        self.assertFalse(compatible_refresh(50,59.94));self.assertTrue(compatible_refresh(25,50))
        self.assertIn('refresh_mismatch',self.codes([s(i,refresh_hz=59.94) for i in range(20)]))
    def test_nominal_plan_not_blame(self):
        x=[s(i) for i in range(10)]+[s(10+i,video_bitrate_mbps=.05,video_queue_data_pct=0,caching=True) for i in range(5)]
        c=self.codes(x,SystemContext(internet_plan_mbps=1000));self.assertIn('plan_speed_not_explanation',c)
    def test_lan_margin(self):
        ctx=SystemContext(adapter_link_mbps=[10]); c=self.codes([s(i,video_bitrate_mbps=8) for i in range(20)],ctx);self.assertIn('lan_capacity_margin',c)
    def test_no_ram_advice_without_pressure(self):
        fs=diagnose([s(i,cpu_usage_pct=98,free_memory_pct=70,playback_time_s=10) for i in range(20)],SystemContext())
        self.assertNotIn('memory_pressure',[f.code for f in fs])
    def test_high_cpu_alone_not_called_fault(self):
        c=self.codes([s(i,cpu_usage_pct=98,playback_time_s=i) for i in range(20)])
        self.assertNotIn('cpu_overload',c)
    def test_software_decode_without_stall_is_risk_not_cause(self):
        c=self.codes([s(i,cpu_usage_pct=95,hw_decoder=False,video_height=2160,video_width=3840,video_fps=60,refresh_hz=60,playback_time_s=i) for i in range(20)])
        self.assertIn('software_decode_headroom',c); self.assertNotIn('software_decode_pressure',c)
    def test_starvation_with_missing_cpu_memory_is_still_detected_but_not_ruled_out(self):
        x=[s(i,cpu_usage_pct=None,free_memory_pct=None) for i in range(10)] + [s(10+i,cpu_usage_pct=None,free_memory_pct=None,video_bitrate_mbps=.05,video_queue_data_pct=1,audio_queue_data_pct=0,caching=True) for i in range(5)]
        fs=diagnose(x,SystemContext())
        f=next(y for y in fs if y.code=='delivery_starvation')
        self.assertFalse(any('RAM' in z for z in f.exclusions))
        self.assertFalse(any('CPU' in z for z in f.exclusions))

    def test_starvation_and_cpu_saturation_are_reported_as_concurrent_not_cpu_causal(self):
        x=[s(i,cpu_usage_pct=98) for i in range(10)] + [s(10+i,cpu_usage_pct=98,video_bitrate_mbps=.05,video_queue_data_pct=1,audio_queue_data_pct=0,caching=True,playback_time_s=10) for i in range(6)]
        c=[f.code for f in diagnose(x,SystemContext())]
        self.assertIn('delivery_starvation',c)
        self.assertIn('concurrent_cpu_pressure',c)
        self.assertNotIn('cpu_overload',c)
        self.assertNotIn('software_decode_pressure',c)

    def test_capacity_margin_without_observed_fault_is_advisory_not_high(self):
        fs=diagnose([s(i,video_bitrate_mbps=8) for i in range(20)],SystemContext(adapter_link_mbps=[10]))
        f=next(x for x in fs if x.code=='lan_capacity_margin')
        self.assertEqual(f.severity,'medium')
if __name__=='__main__':unittest.main()
