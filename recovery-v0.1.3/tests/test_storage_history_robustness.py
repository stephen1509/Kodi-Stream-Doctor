import json, os, sys, tempfile, time, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.storage import load_reports, write_report
from streamdoctor.history import apply_history
from streamdoctor.model import Finding, SessionReport, SystemContext


def report(provider, starvation=False):
    fs=[]
    if starvation:
        fs=[Finding('delivery_starvation','delivery','high',85,'x','x',[],[],[])]
    return SessionReport('a','b',20,100 if not fs else 50,{'delivery':100 if not fs else 50},fs,SystemContext(),'x',{}, {'pvr_provider':provider})

class RobustnessTests(unittest.TestCase):
    def test_corrupt_saved_report_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            write_report(d, {'good':True})
            bad=os.path.join(d,'streamdoctor-99999999-999999-999.json')
            with open(bad,'w',encoding='utf-8') as f: f.write('{ definitely not json')
            os.utime(bad,(time.time()+10,time.time()+10))
            rows=load_reports(d,20)
            self.assertEqual(len(rows),1); self.assertTrue(rows[0]['good'])

    def test_history_does_not_blame_source_when_most_same_source_reports_are_healthy(self):
        cur=report('Provider A',True)
        prev=[report('Provider A',True), report('Provider A',False), report('Provider A',False), report('Provider A',False)]
        out=apply_history(cur,[r.to_dict() for r in prev])
        self.assertNotIn('source_pattern',[f.code for f in out.findings])

if __name__=='__main__': unittest.main()
