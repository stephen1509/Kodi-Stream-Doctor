import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.ui import _render
class UIRenderTests(unittest.TestCase):
    def test_unknown_score_renders_not_rated(self):
        text=_render({'health_status':'UNKNOWN','health_score':None,'telemetry_coverage_pct':20,'summary':'insufficient','component_scores':{},'context':{},'source':{},'metrics':{},'findings':[]})
        self.assertIn('Health score: not rated',text);self.assertIn('Status: UNKNOWN',text)
    def test_rich_context_does_not_misalign_ambiguous_adapter_speeds(self):
        text=_render({'health_status':'GOOD','health_score':100,'telemetry_coverage_pct':100,'summary':'ok','component_scores':{},'context':{'adapter_names':['Ethernet','VPN'],'adapter_link_mbps':[1000]},'source':{},'metrics':{},'findings':[]})
        self.assertIn('Adapter 1: Ethernet',text);self.assertIn('Adapter 2: VPN',text);self.assertIn('Reported active link speed(s): 1000 Mbps',text)
    def test_malformed_or_partial_metric_stats_do_not_crash_report_view(self):
        text=_render({'health_status':'UNKNOWN','health_score':None,'telemetry_coverage_pct':40,'summary':'partial','component_scores':{},'context':{},'source':{},'metrics':{'video_bitrate_mbps':{'min':None,'median':8.5,'max':9.0}},'findings':[]})
        self.assertIn('Status: UNKNOWN',text)

    def test_false_boolean_source_values_are_visible(self):
        text=_render({'health_status':'DEGRADED','health_score':80,'telemetry_coverage_pct':90,'summary':'x','component_scores':{},'context':{},'source':{'hardware_decoder_active':False,'internet_connected':False,'video_codec':'hevc'},'metrics':{},'findings':[]})
        self.assertIn('Hardware Decoder Active: False',text)
        self.assertIn('Internet Connected: False',text)

if __name__=='__main__':unittest.main()
