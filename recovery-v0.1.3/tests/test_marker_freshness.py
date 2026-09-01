import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.service_runtime import marker_is_fresh
class MarkerFreshnessTests(unittest.TestCase):
    def test_fresh_marker(self): self.assertTrue(marker_is_fresh('1000',now=1010,max_age=20))
    def test_stale_marker(self): self.assertFalse(marker_is_fresh('1000',now=1100,max_age=20))
    def test_invalid_marker(self): self.assertFalse(marker_is_fresh('not-a-time',now=1010,max_age=20))
if __name__=='__main__': unittest.main()
