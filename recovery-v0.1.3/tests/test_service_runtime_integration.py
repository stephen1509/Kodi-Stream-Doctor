import os,sys,tempfile,types,unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
LIB=os.path.join(ROOT,'service.streamdoctor','resources','lib')
sys.path.insert(0,LIB)
from streamdoctor import service_runtime
from streamdoctor.kodi_sensor import LABELS


class FakeState:
    def __init__(self,bad=False,source_switch=False,enabled=True,version='22.0-BETA1 (22.0.0)',internet_outage=False):
        self.tick=0; self.bad=bad; self.source_switch=source_switch; self.enabled=enabled; self.version=version; self.internet_outage=internet_outage; self.logs=[]; self.notifications=[]; self.props={}


def install_fake_kodi(state, store_reports=False):
    xbmc=types.ModuleType('xbmc'); xbmcaddon=types.ModuleType('xbmcaddon'); xbmcgui=types.ModuleType('xbmcgui'); xbmcvfs=types.ModuleType('xbmcvfs')
    xbmc.LOGWARNING=2; xbmc.LOGINFO=1

    class Monitor:
        def abortRequested(self): return state.tick>=15
        def waitForAbort(self,interval):
            state.tick+=1
            return state.tick>=15
    class Player:
        def isPlayingVideo(self): return state.tick<12
        def getTime(self):
            # A healthy advancing clock. Delivery failure is detected from queue/bitrate/cache.
            return state.tick*0.5
    xbmc.Monitor=Monitor; xbmc.Player=Player

    def get_info(label):
        bad_now=state.bad and 8<=state.tick<12
        switched=state.source_switch and state.tick>=6
        vals={
            'System.BuildVersion':state.version,
            LABELS['video_bitrate']:'.05 Mb/s' if bad_now else '8.5 Mb/s',
            LABELS['audio_bitrate']:'192 Kb/s',
            LABELS['video_queue_data']:'1' if bad_now else '90',
            LABELS['audio_queue_data']:'1' if bad_now else '90',
            LABELS['video_queue']:'1' if bad_now else '90',
            LABELS['audio_queue']:'1' if bad_now else '90',
            LABELS['video_decoder']:'ff-h264-d3d11va', LABELS['video_codec']:'h264',
            LABELS['video_fps']:'50.000', LABELS['video_width']:'1920', LABELS['video_height']:'1080',
            LABELS['scan_type']:'p', LABELS['deint_method']:'none', LABELS['pix_format']:'nv12',
            LABELS['cpu_usage']:'CPU0 20% CPU1 30%', LABELS['cpu_freq']:'3000 MHz',
            LABELS['free_memory']:'65%', LABELS['free_memory_mb']:'8000 MB', LABELS['temperature_units']:'°C', LABELS['gui_fps']:'50.0',
            LABELS['network_link']:'1 Gbit/s', LABELS['internet_state']:('not connected' if (bad_now and state.internet_outage) else 'connected'),
            LABELS['screen']:'1920x1080 @ 50.000', LABELS['pvr_provider']:'Test Provider',
            LABELS['player_path']:('https://example.invalid/live/channel-b.m3u8?token=do-not-store' if switched else 'https://example.invalid/live/channel-a.m3u8?token=do-not-store'),
            LABELS['channel_name']:('Test Channel B' if switched else 'Test Channel A'),
            LABELS['stream_title']:'Test Programme',
        }
        return vals.get(label,'')
    xbmc.getInfoLabel=get_info
    xbmc.getLocalizedString=lambda i: {13296:'connected',13297:'not connected'}.get(i,'')
    def cond(expr):
        if expr in ('Player.IsInternetStream','Player.IsLive','Player.Process(videohwdecoder)'): return True
        if expr=='Player.Caching': return state.bad and 8<=state.tick<12
        return False
    xbmc.getCondVisibility=cond
    xbmc.log=lambda msg,level=0: state.logs.append((level,msg))

    class Addon:
        def getSettingBool(self,key):
            return {'enabled':state.enabled,'notifications':True,'store_reports':store_reports}.get(key,False)
        def getSettingInt(self,key):
            return {'sample_interval_ms':500,'internet_plan_mbps':1000,'known_capacity_mbps':0,'retention_files':20}.get(key,0)
        def openSettings(self): pass
    xbmcaddon.Addon=Addon

    class Dialog:
        def notification(self,*args,**kwargs): state.notifications.append(args)
    class Window:
        def __init__(self,id): self.id=id
        def setProperty(self,k,v): state.props[k]=v
        def getProperty(self,k): return state.props.get(k,'')
    xbmcgui.Dialog=Dialog; xbmcgui.Window=Window
    xbmcgui.NOTIFICATION_WARNING=1; xbmcgui.NOTIFICATION_INFO=0

    temp=tempfile.TemporaryDirectory(); state._temp=temp
    xbmcvfs.translatePath=lambda p: os.path.join(temp.name,'reports')

    old={name:sys.modules.get(name) for name in ('xbmc','xbmcaddon','xbmcgui','xbmcvfs')}
    sys.modules.update({'xbmc':xbmc,'xbmcaddon':xbmcaddon,'xbmcgui':xbmcgui,'xbmcvfs':xbmcvfs})
    return old


def restore_modules(old,state):
    for name,val in old.items():
        if val is None: sys.modules.pop(name,None)
        else: sys.modules[name]=val
    state._temp.cleanup()


class ServiceIntegrationTests(unittest.TestCase):
    def test_disabled_service_exits_without_sampling(self):
        state=FakeState(enabled=False); old=install_fake_kodi(state)
        try: service_runtime.run()
        finally: restore_modules(old,state)
        self.assertEqual(state.tick,0); self.assertFalse(state.logs); self.assertFalse(state.notifications)

    def test_pre_kodi22_warns_but_fails_open(self):
        state=FakeState(version='21.3 (21.3.0)'); old=install_fake_kodi(state)
        try: service_runtime.run()
        finally: restore_modules(old,state)
        self.assertTrue(any('Kodi 22 Piers is required' in str(args) for args in state.notifications))
        self.assertTrue(any('No strong evidence' in msg for _,msg in state.logs))

    def test_healthy_stream_service_lifecycle(self):
        state=FakeState(False); old=install_fake_kodi(state)
        try: service_runtime.run()
        finally: restore_modules(old,state)
        self.assertTrue(any('No strong evidence' in msg for _,msg in state.logs))
        self.assertEqual(state.props.get('StreamDoctor.LiveText'),'No live/Internet stream is currently being monitored.')
        self.assertFalse(state.notifications)

    def test_starvation_reaches_live_notification_and_final_report_summary(self):
        state=FakeState(True); old=install_fake_kodi(state)
        try: service_runtime.run()
        finally: restore_modules(old,state)
        self.assertTrue(any('starved of incoming media' in msg for _,msg in state.logs))
        self.assertTrue(any('starved of incoming media' in str(args) for args in state.notifications))
        # Raw source token must not escape even in logs.
        self.assertFalse(any('do-not-store' in msg for _,msg in state.logs))

    def test_channel_change_rolls_to_a_new_session_without_waiting_for_stop(self):
        import glob
        state=FakeState(False,source_switch=True); old=install_fake_kodi(state,store_reports=True)
        try:
            service_runtime.run()
            files=glob.glob(os.path.join(state._temp.name,'reports','streamdoctor-*.json'))
            self.assertEqual(len(files),2)
            self.assertGreaterEqual(sum(1 for _,msg in state.logs if 'No strong evidence' in msg),2)
        finally:
            restore_modules(old,state)

    def test_localized_kodi_internet_outage_flows_into_network_diagnosis(self):
        import json,glob
        state=FakeState(True,internet_outage=True); old=install_fake_kodi(state,store_reports=True)
        try:
            service_runtime.run()
            files=glob.glob(os.path.join(state._temp.name,'reports','streamdoctor-*.json'))
            with open(files[-1],encoding='utf-8') as f: report=json.load(f)
            codes=[x.get('code') for x in report.get('findings',[])]
            self.assertIn('kodi_internet_unavailable',codes)
        finally:
            restore_modules(old,state)

    def test_persisted_report_is_bounded_and_redacted(self):
        import json,glob
        state=FakeState(True); old=install_fake_kodi(state,store_reports=True)
        try:
            service_runtime.run()
            files=glob.glob(os.path.join(state._temp.name,'reports','streamdoctor-*.json'))
            self.assertEqual(len(files),1)
            self.assertLess(os.path.getsize(files[0]),4*1024*1024)
            with open(files[0],encoding='utf-8') as f: report=json.load(f)
            blob=json.dumps(report)
            self.assertEqual(report.get('health_status'),'BAD')
            self.assertGreaterEqual(report.get('telemetry_coverage_pct',0),60)
            self.assertNotIn('do-not-store',blob)
            self.assertNotIn('/live?',blob)
            self.assertEqual(report.get('source',{}).get('source_origin'),'https://example.invalid')
        finally:
            restore_modules(old,state)

if __name__=='__main__': unittest.main()
