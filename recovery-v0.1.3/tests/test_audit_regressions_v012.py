import json, os, sys, tempfile, time, unittest
from pathlib import Path
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))

import streamdoctor
from streamdoctor.diagnose import diagnose
from streamdoctor.history import _source_key
from streamdoctor.kodi_sensor import KodiTelemetryReader, LABELS
from streamdoctor.model import TelemetrySample, SystemContext
from streamdoctor.redaction import source_identity_key
from streamdoctor.scoring import health_status, telemetry_coverage
from streamdoctor.service_runtime import kodi_major_version
from streamdoctor.storage import MAX_FILE_BYTES, load_reports
from streamdoctor.ui import _latest_report


def sample(t, **kw):
    base=dict(t=t, playing=True, playback_time_s=t, video_bitrate_mbps=8.0,
              audio_bitrate_kbps=192.0, video_queue_data_pct=90,
              audio_queue_data_pct=90, cpu_usage_pct=25, free_memory_pct=60,
              video_width=1920, video_height=1080, video_fps=50,
              refresh_hz=50, hw_decoder=True)
    base.update(kw)
    return TelemetrySample(**base)


class _X:
    vals={
        LABELS['video_bitrate']:'8 Mb/s', LABELS['audio_bitrate']:'192 Kb/s',
        LABELS['video_decoder']:'ff-h264', LABELS['player_path']:'',
        LABELS['channel_name']:'Channel A', LABELS['pvr_provider']:'Provider A',
    }
    @classmethod
    def getInfoLabel(cls,k): return cls.vals.get(k,'')
    @staticmethod
    def getCondVisibility(k): return k == 'Player.Process(videohwdecoder)'
    @staticmethod
    def getLocalizedString(i): return ''

class _CountPlayer:
    def __init__(self): self.calls=0
    def isPlayingVideo(self):
        self.calls += 1
        if self.calls > 0: raise RuntimeError('must not be called when runtime already knows state')
    def getTime(self): return 1.0

class _Vfs:
    @staticmethod
    def translatePath(p): return p


class AuditRegressionTests(unittest.TestCase):
    def test_internal_version_matches_package(self):
        self.assertEqual(streamdoctor.__version__,'0.1.3')
        text=Path(ROOT,'service.streamdoctor','addon.xml').read_text(encoding='utf-8')
        self.assertIn('version="0.1.3"',text)

    def test_runtime_can_supply_known_playback_state_without_second_player_check(self):
        p=_CountPlayer()
        s=KodiTelemetryReader(_X,p).sample(1.0,playing=True)
        self.assertTrue(s.playing)
        self.assertEqual(p.calls,0)

    def test_conditional_exception_yields_unknown_hw_state_not_false(self):
        class BadX(_X):
            @staticmethod
            def getCondVisibility(k): raise RuntimeError('unsupported')
        class P:
            def isPlayingVideo(self): return True
            def getTime(self): return 1.0
        s=KodiTelemetryReader(BadX,P()).sample(1.0)
        self.assertIsNone(s.hw_decoder)

    def test_single_transient_queue_and_bitrate_dip_is_not_high_starvation(self):
        xs=[sample(i*0.5) for i in range(20)]
        xs[10]=sample(5.0,video_bitrate_mbps=.05,video_queue_data_pct=1,audio_queue_data_pct=1,caching=False)
        codes=[f.code for f in diagnose(xs,SystemContext())]
        self.assertNotIn('delivery_starvation',codes)
        self.assertNotIn('audio_queue_starvation',codes)

    def test_sustained_starvation_still_detects(self):
        xs=[sample(i*0.5) for i in range(20)]
        for i in (10,11,12):
            xs[i]=sample(i*0.5,video_bitrate_mbps=.05,video_queue_data_pct=1,audio_queue_data_pct=1,caching=True)
        self.assertIn('delivery_starvation',[f.code for f in diagnose(xs,SystemContext())])

    def test_low_memory_without_playback_problem_is_risk_not_degraded(self):
        xs=[sample(i*0.5,free_memory_pct=4) for i in range(20)]
        fs=diagnose(xs,SystemContext())
        mem=next(f for f in fs if f.code=='memory_pressure')
        self.assertEqual(mem.severity,'low')
        coverage,detail=telemetry_coverage(xs)
        self.assertEqual(health_status(fs,coverage,detail),'GOOD')

    def test_low_memory_with_user_problem_is_elevated(self):
        xs=[sample(i*0.5,free_memory_pct=4) for i in range(20)]
        mem=next(f for f in diagnose(xs,SystemContext(),user_reported=True,user_issue='video') if f.code=='memory_pressure')
        self.assertEqual(mem.severity,'medium')

    def test_identity_falls_back_to_channel_when_path_missing(self):
        a=source_identity_key('', 'Channel A', 'Provider')
        b=source_identity_key('', 'Channel B', 'Provider')
        self.assertTrue(a); self.assertNotEqual(a,b)

    def test_malformed_port_does_not_break_identity_or_include_rotating_credentials(self):
        a=source_identity_key('https://user:one@example.invalid:bad/live.m3u8?token=aaa','Channel','Provider')
        b=source_identity_key('https://user:two@example.invalid:bad/live.m3u8?token=bbb','Channel','Provider')
        self.assertEqual(a,b)

    def test_kodi_major_parser_is_robust(self):
        self.assertEqual(kodi_major_version('22.0-BETA1 (22.0.0)'),22)
        self.assertEqual(kodi_major_version('Kodi 22 Piers'),22)
        self.assertEqual(kodi_major_version(''),0)

    def test_load_reports_skips_oversized_and_corrupt_and_finds_valid(self):
        with tempfile.TemporaryDirectory() as d:
            valid=os.path.join(d,'streamdoctor-1.json')
            bad=os.path.join(d,'streamdoctor-2.json')
            huge=os.path.join(d,'streamdoctor-3.json')
            with open(valid,'w',encoding='utf-8') as f: json.dump({'health_status':'GOOD'},f)
            with open(bad,'w',encoding='utf-8') as f: f.write('{bad')
            with open(huge,'wb') as f: f.truncate(MAX_FILE_BYTES+1)
            now=time.time(); os.utime(valid,(now,now)); os.utime(bad,(now+1,now+1)); os.utime(huge,(now+2,now+2))
            reports=load_reports(d,1)
            self.assertEqual(reports,[{'health_status':'GOOD'}])

    def test_ui_latest_report_falls_back_to_latest_valid(self):
        with tempfile.TemporaryDirectory() as d:
            reports=os.path.join(d,'reports'); os.makedirs(reports)
            valid=os.path.join(reports,'streamdoctor-1.json')
            bad=os.path.join(reports,'streamdoctor-2.json')
            with open(valid,'w',encoding='utf-8') as f: json.dump({'summary':'older valid'},f)
            with open(bad,'w',encoding='utf-8') as f: f.write('{bad')
            now=time.time(); os.utime(valid,(now,now)); os.utime(bad,(now+1,now+1))
            class Addon:
                def getAddonInfo(self,k): return d
            self.assertEqual(_latest_report(_Vfs,Addon()).get('summary'),'older valid')

    def test_history_does_not_treat_generic_pvr_namespace_as_specific_source(self):
        report={'source':{'pvr_provider':'','source_origin':'pvr://channels'},'findings':[]}
        self.assertEqual(_source_key(report),(None,None))

if __name__=='__main__': unittest.main()

class AdditionalEvidenceTests(unittest.TestCase):
    def test_low_percentage_but_multiple_gb_free_is_not_memory_pressure(self):
        xs=[sample(i*0.5,free_memory_pct=4,free_memory_mb=4096) for i in range(20)]
        self.assertNotIn('memory_pressure',[f.code for f in diagnose(xs,SystemContext())])

    def test_nonconsecutive_internet_blips_do_not_become_high_outage_diagnosis(self):
        xs=[sample(i*0.5,is_internet_stream=True) for i in range(20)]
        for i in (5,15):
            xs[i]=sample(i*0.5,is_internet_stream=True,internet_connected=False,video_queue_data_pct=1,caching=True)
        self.assertNotIn('kodi_internet_unavailable',[f.code for f in diagnose(xs,SystemContext())])

    def test_report_boolean_tie_is_unknown(self):
        from streamdoctor.session import SessionAnalyzer
        a=SessionAnalyzer(SystemContext())
        a.add(sample(0,hw_decoder=True,internet_connected=True))
        a.add(sample(.5,hw_decoder=False,internet_connected=False))
        src=a._source()
        self.assertIsNone(src['hardware_decoder_active'])
        self.assertIsNone(src['internet_connected'])

class StorageDefenseInDepthTests(unittest.TestCase):
    def test_report_writer_redacts_future_accidental_secret_fields(self):
        from streamdoctor.storage import write_report
        with tempfile.TemporaryDirectory() as d:
            p=write_report(d,{
                'summary':'token=super-secret https://user:pw@example.invalid/path?sig=abc',
                'source':{'source_origin':'https://user:pw@example.invalid/path?token=abc','source_key':'ephemeral-hash'},
                'authorization':'Bearer very-secret-value',
            },20)
            text=Path(p).read_text(encoding='utf-8')
            self.assertNotIn('super-secret',text)
            self.assertNotIn('user:pw',text)
            self.assertNotIn('very-secret-value',text)
            self.assertNotIn('ephemeral-hash',text)
            payload=json.loads(text)
            self.assertEqual(payload['source']['source_origin'],'https://example.invalid')
            self.assertEqual(payload['authorization'],'[REDACTED]')
