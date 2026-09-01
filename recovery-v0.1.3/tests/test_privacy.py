import os, sys, unittest
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.kodi_sensor import KodiTelemetryReader, LABELS
from streamdoctor.model import SystemContext
from streamdoctor.session import SessionAnalyzer

SECRET='super-secret-token-92741'
RAW=f'https://alice:password@example.invalid/live/channel42.m3u8?token={SECRET}&sig=abc#fragment'

class FakeXBMC:
    @staticmethod
    def getInfoLabel(key):
        vals={
            LABELS['player_path']: RAW,
            LABELS['stream_title']: f'News token={SECRET} https://example.invalid/path?sig={SECRET}',
            LABELS['channel_name']: f'Channel password={SECRET}',
            LABELS['video_bitrate']:'8.5 Mb/s', LABELS['audio_bitrate']:'192 Kb/s',
            LABELS['video_queue_data']:'90', LABELS['audio_queue_data']:'90',
            LABELS['video_width']:'1920', LABELS['video_height']:'1080',
            LABELS['video_fps']:'50', LABELS['screen']:'1920x1080 @ 50.000',
            LABELS['free_memory']:'60%', LABELS['cpu_usage']:'CPU0 20% CPU1 20%',
        }
        return vals.get(key,'')
    @staticmethod
    def getLocalizedString(i): return {13296:'Connected',13297:'Not connected'}.get(i,'')
    @staticmethod
    def getCondVisibility(key):
        return key in ('Player.IsInternetStream','Player.Process(videohwdecoder)')

class FakePlayer:
    def isPlayingVideo(self): return True
    def getTime(self): return 1.0

class PrivacyTests(unittest.TestCase):
    def test_raw_stream_credentials_and_tokens_do_not_enter_sample_or_report(self):
        reader=KodiTelemetryReader(FakeXBMC,FakePlayer())
        a=SessionAnalyzer(SystemContext())
        for i in range(10):
            s=reader.sample(float(i)); s.playback_time_s=float(i); a.add(s)
        self.assertEqual(a.samples[-1].source_origin,'https://example.invalid')
        blob=str(a.report().to_dict())
        self.assertNotIn(SECRET, blob)
        self.assertNotIn('alice:password', blob)
        self.assertNotIn('/live/channel42.m3u8', blob)
        self.assertNotIn('sig=abc', blob)
        self.assertNotIn('password='+SECRET, blob)
        self.assertNotIn('/path?sig=', blob)
        self.assertIn('[REDACTED]', blob)

if __name__=='__main__': unittest.main()
