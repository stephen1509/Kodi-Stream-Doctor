import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample,SystemContext
from streamdoctor.diagnose import diagnose

def s(t,**kw):
    d=dict(t=t,playing=True,playback_time_s=t,is_internet_stream=True,video_bitrate_mbps=8,audio_bitrate_kbps=192,video_queue_data_pct=90,audio_queue_data_pct=90,cpu_usage_pct=25,free_memory_pct=60,video_width=1920,video_height=1080,video_fps=50,refresh_hz=50,hw_decoder=True,internet_connected=True)
    d.update(kw); return TelemetrySample(**d)
class NetworkDeinterlaceTests(unittest.TestCase):
    def test_kodi_internet_state_corroborates_starvation(self):
        x=[s(i) for i in range(10)] + [s(10+i,video_bitrate_mbps=.05,video_queue_data_pct=0,audio_queue_data_pct=0,caching=True,internet_connected=False) for i in range(6)]
        c=[f.code for f in diagnose(x,SystemContext())]
        self.assertIn('delivery_starvation',c); self.assertIn('kodi_internet_unavailable',c)
    def test_internet_false_without_starvation_not_called_fault(self):
        c=[f.code for f in diagnose([s(i,internet_connected=False) for i in range(20)],SystemContext())]
        self.assertNotIn('kodi_internet_unavailable',c)
    def test_interlaced_problem_with_deinterlace_disabled(self):
        x=[s(i,scan_type='i',deint_method='none') for i in range(20)]
        c=[f.code for f in diagnose(x,SystemContext(),user_reported=True,user_issue='video')]
        self.assertIn('deinterlace_disabled',c)
    def test_interlaced_without_user_problem_does_not_blame_deinterlace(self):
        x=[s(i,scan_type='i',deint_method='none') for i in range(20)]
        c=[f.code for f in diagnose(x,SystemContext())]
        self.assertNotIn('deinterlace_disabled',c)
if __name__=='__main__':unittest.main()
