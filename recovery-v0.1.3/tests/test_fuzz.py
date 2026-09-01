import os, sys, random, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import TelemetrySample, SystemContext
from streamdoctor.diagnose import diagnose
from streamdoctor.scoring import component_scores, overall_score


class FuzzTests(unittest.TestCase):
    def test_random_telemetry_is_bounded_and_does_not_crash(self):
        rng=random.Random(220022)
        severities={'high','medium','low','info'}
        for case in range(800):
            n=rng.randint(1,80)
            samples=[]
            playtime=0.0
            for i in range(n):
                # Some deliberately missing values model unsupported labels/platforms.
                def maybe(v): return None if rng.random()<0.18 else v
                if rng.random()>0.08: playtime += rng.uniform(0.0,1.2)
                samples.append(TelemetrySample(
                    t=i*0.5, playing=rng.random()>0.03, paused=rng.random()<0.03,
                    playback_time_s=maybe(playtime), caching=rng.random()<0.08,
                    video_bitrate_mbps=maybe(rng.uniform(0,120)),
                    audio_bitrate_kbps=maybe(rng.uniform(0,1500)),
                    video_queue_data_pct=maybe(rng.uniform(0,100)),
                    audio_queue_data_pct=maybe(rng.uniform(0,100)),
                    cpu_usage_pct=maybe(rng.uniform(0,100)), free_memory_pct=maybe(rng.uniform(0,100)),
                    video_width=rng.choice([0,640,1280,1920,3840]),
                    video_height=rng.choice([0,360,720,1080,2160]),
                    video_fps=maybe(rng.choice([23.976,25,29.97,50,59.94,60,120])),
                    refresh_hz=maybe(rng.choice([24,50,59.94,60,100,120,144])),
                    hw_decoder=rng.choice([True,False,None]), audio_passthrough=rng.choice([True,False,None]),
                    cpu_temp_c=maybe(rng.uniform(20,110)), gpu_temp_c=maybe(rng.uniform(20,110)),
                    cpu_frequency_mhz=maybe(rng.uniform(300,6000)), link_mbps=maybe(rng.choice([10,100,1000,2500,10000])),
                    pvr_signal=maybe(rng.uniform(0,100)), pvr_ber=maybe(rng.choice([0,0,0,1,5])),
                    pvr_unc=maybe(rng.choice([0,0,0,1,5]))))
            ctx=SystemContext(cpu_max_mhz=rng.choice([None,1800,3200,5000]),
                              internet_plan_mbps=rng.choice([None,100,1000,2000,10000]),
                              known_capacity_mbps=rng.choice([None,20,100,500,1000]))
            findings=diagnose(samples,ctx,user_reported=rng.random()<0.12,user_issue=rng.choice(['','freeze','video','audio','avsync','quality','other']))
            for f in findings:
                self.assertIn(f.severity,severities)
                self.assertGreaterEqual(f.confidence,0); self.assertLessEqual(f.confidence,100)
                self.assertTrue(f.code); self.assertTrue(f.title)
            scores=component_scores(samples,findings)
            self.assertTrue(all(0<=v<=100 for v in scores.values()))
            self.assertTrue(0<=overall_score(scores)<=100)

if __name__=='__main__': unittest.main()
