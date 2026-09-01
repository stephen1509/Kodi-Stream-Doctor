import json, os, sys, tempfile, types, unittest
ROOT=os.path.dirname(os.path.dirname(__file__)); LIB=os.path.join(ROOT,'service.streamdoctor','resources','lib'); sys.path.insert(0,LIB)
from streamdoctor import ui

class FakeUIState:
    def __init__(self,picks):
        self.picks=list(picks); self.viewers=[]; self.oks=[]; self.notifications=[]; self.props={}; self.settings_opened=0


def install_ui(state, profile):
    xbmcaddon=types.ModuleType('xbmcaddon'); xbmcgui=types.ModuleType('xbmcgui'); xbmcvfs=types.ModuleType('xbmcvfs')
    class Addon:
        def getAddonInfo(self,key): return profile if key=='profile' else ''
        def openSettings(self): state.settings_opened += 1
    xbmcaddon.Addon=Addon
    class Dialog:
        def select(self,title,choices): return state.picks.pop(0)
        def textviewer(self,title,text): state.viewers.append((title,text))
        def ok(self,*args): state.oks.append(args)
        def notification(self,*args,**kwargs): state.notifications.append(args)
    class Window:
        def __init__(self,_id): pass
        def getProperty(self,key): return state.props.get(key,'')
        def setProperty(self,key,value): state.props[key]=value
    xbmcgui.Dialog=Dialog; xbmcgui.Window=Window; xbmcgui.NOTIFICATION_INFO=0
    xbmcvfs.translatePath=lambda p:p
    old={n:sys.modules.get(n) for n in ('xbmcaddon','xbmcgui','xbmcvfs')}
    sys.modules.update({'xbmcaddon':xbmcaddon,'xbmcgui':xbmcgui,'xbmcvfs':xbmcvfs})
    return old

def restore(old):
    for n,v in old.items():
        if v is None: sys.modules.pop(n,None)
        else: sys.modules[n]=v

class UIActionTests(unittest.TestCase):
    def test_live_status_view(self):
        with tempfile.TemporaryDirectory() as d:
            st=FakeUIState([0]); st.props['StreamDoctor.LiveText']='Status: GOOD'
            old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertIn('Status: GOOD',st.viewers[0][1])

    def test_no_completed_report_message(self):
        with tempfile.TemporaryDirectory() as d:
            st=FakeUIState([1]); old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertTrue(st.oks)

    def test_completed_report_view(self):
        with tempfile.TemporaryDirectory() as d:
            reports=os.path.join(d,'reports'); os.makedirs(reports)
            payload={'health_status':'GOOD','health_score':100,'telemetry_coverage_pct':100,'summary':'ok','component_scores':{},'context':{},'source':{},'metrics':{},'findings':[]}
            with open(os.path.join(reports,'streamdoctor-20260817-000000-000000001.json'),'w',encoding='utf-8') as f: json.dump(payload,f)
            st=FakeUIState([1]); old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertIn('Status: GOOD',st.viewers[0][1])

    def test_problem_marker_sets_timestamp_and_type(self):
        with tempfile.TemporaryDirectory() as d:
            st=FakeUIState([2,1]); old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertEqual(st.props.get('StreamDoctor.MarkerType'),'video')
            self.assertTrue(float(st.props.get('StreamDoctor.UserMarker','0'))>0)
            self.assertTrue(st.notifications)

    def test_cancel_problem_marker_is_noop(self):
        with tempfile.TemporaryDirectory() as d:
            st=FakeUIState([2,-1]); old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertNotIn('StreamDoctor.UserMarker',st.props)

    def test_settings_action(self):
        with tempfile.TemporaryDirectory() as d:
            st=FakeUIState([3]); old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertEqual(st.settings_opened,1)

    def test_corrupt_latest_report_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            reports=os.path.join(d,'reports'); os.makedirs(reports)
            with open(os.path.join(reports,'streamdoctor-20260817-000000-000000001.json'),'w') as f: f.write('{bad')
            st=FakeUIState([1]); old=install_ui(st,d)
            try: ui.run()
            finally: restore(old)
            self.assertTrue(st.oks)

if __name__=='__main__': unittest.main()
