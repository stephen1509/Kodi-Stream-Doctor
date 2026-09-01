import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.model import Finding,TelemetrySample
from streamdoctor.scoring import component_scores,overall_score

class ScoreTests(unittest.TestCase):
    def test_bounds(self):
        f=Finding('x','delivery','high',100,'','','',[],[])
        s=component_scores([], [f])
        self.assertTrue(all(0<=v<=100 for v in s.values()))
        self.assertTrue(0<=overall_score(s)<=100)

    def test_missing_component_is_not_silently_scored_perfect(self):
        sample=TelemetrySample(t=0,playing=True,video_bitrate_mbps=8,video_queue_data_pct=90)
        scores=component_scores([sample],[])
        self.assertEqual(scores.get('delivery'),100)
        self.assertNotIn('memory',scores)
        self.assertNotIn('device',scores)
        self.assertNotIn('decoder',scores)

    def test_observed_component_can_be_scored(self):
        sample=TelemetrySample(t=0,playing=True,cpu_usage_pct=20,free_memory_pct=70,hw_decoder=True,video_fps=50,refresh_hz=50,audio_queue_data_pct=90)
        scores=component_scores([sample],[])
        for key in ('device','memory','decoder','display','audio'):
            self.assertEqual(scores.get(key),100)

if __name__=='__main__':unittest.main()
