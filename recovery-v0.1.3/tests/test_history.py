import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.history import apply_history
from streamdoctor.model import SessionReport,SystemContext,Finding

def rep(provider,codes):
    fs=[Finding(c,'delivery','high',85,c,c,[],[],[]) for c in codes]
    return SessionReport('a','b',20,50,{'delivery':50},fs,SystemContext(),'x',{}, {'pvr_provider':provider})
class HistoryTests(unittest.TestCase):
    def test_repeated_provider_pattern(self):
        cur=rep('Provider A',['delivery_starvation'])
        prev=[rep('Provider A',['delivery_starvation']),rep('Provider A',['delivery_starvation']),rep('Provider B',[])]
        out=apply_history(cur,[x.to_dict() for x in prev])
        self.assertIn('source_pattern',[f.code for f in out.findings])
    def test_not_enough_history(self):
        cur=rep('A',['delivery_starvation']); out=apply_history(cur,[rep('A',['delivery_starvation']).to_dict()])
        self.assertNotIn('source_pattern',[f.code for f in out.findings])
    def test_history_preserves_current_component_scores(self):
        r=rep('A',['delivery_starvation'])
        r.component_scores={'delivery':42,'device':97,'memory':100}
        r.health_score=60
        prev=[rep('A',['delivery_starvation']).to_dict(),rep('A',['delivery_starvation']).to_dict(),rep('B',[]).to_dict()]
        out=apply_history(r,prev)
        self.assertEqual(out.component_scores,{'delivery':42,'device':97,'memory':100})
        self.assertEqual(out.health_score,60)
        self.assertIn('source_pattern',{f.code for f in out.findings})

if __name__=='__main__': unittest.main()
