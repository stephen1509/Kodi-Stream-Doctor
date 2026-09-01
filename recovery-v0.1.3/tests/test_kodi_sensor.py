import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.kodi_sensor import KodiTelemetryReader,LABELS
class X:
    vals={LABELS['video_bitrate']:'8.5 Mb/s',LABELS['audio_bitrate']:'192 Kb/s',LABELS['video_queue_data']:'88',LABELS['video_fps']:'50.000',LABELS['video_width']:'1920',LABELS['video_height']:'1080',LABELS['cpu_usage']:'CPU0 20% CPU1 40%',LABELS['cpu_freq']:'3.2 GHz',LABELS['free_memory']:'63%',LABELS['cpu_temp']:'194 °F',LABELS['gpu_temp']:'176 °F',LABELS['temperature_units']:'°F',LABELS['network_link']:'1 Gbit/s',LABELS['internet_state']:'Connected',LABELS['screen']:'1920x1080 @ 50.000'}
    @classmethod
    def getInfoLabel(cls,k): return cls.vals.get(k,'')
    @staticmethod
    def getCondVisibility(k): return k in ('Player.IsLive','Player.IsInternetStream','Player.Process(videohwdecoder)')
    @staticmethod
    def getLocalizedString(i): return {13296:'Connected',13297:'Not connected'}.get(i,'')
class P:
    def isPlayingVideo(self):return True
    def getTime(self):return 123.5
class BadP:
    def isPlayingVideo(self): raise RuntimeError('boom')
    def getTime(self): raise RuntimeError('boom')

class SensorTests(unittest.TestCase):
    def test_sample(self):
        a=KodiTelemetryReader(X,P()).sample(1.0);self.assertEqual(a.video_bitrate_mbps,8.5);self.assertEqual(a.link_mbps,1000);self.assertEqual(a.cpu_usage_pct,30);self.assertTrue(a.hw_decoder);self.assertEqual(a.refresh_hz,50);self.assertEqual(a.cpu_frequency_mhz,3200);self.assertAlmostEqual(a.cpu_temp_c,90);self.assertAlmostEqual(a.gpu_temp_c,80); self.assertTrue(a.internet_connected)
    def test_localized_disconnected_state_is_false(self):
        old=X.vals.get(LABELS['internet_state']); X.vals[LABELS['internet_state']]='Not connected'
        try: a=KodiTelemetryReader(X,P()).sample(1.0)
        finally: X.vals[LABELS['internet_state']]=old
        self.assertFalse(a.internet_connected)
    def test_unknown_localized_state_is_not_guessed(self):
        old=X.vals.get(LABELS['internet_state']); X.vals[LABELS['internet_state']]='Mystery'
        try: a=KodiTelemetryReader(X,P()).sample(1.0)
        finally: X.vals[LABELS['internet_state']]=old
        self.assertIsNone(a.internet_connected)
    def test_player_exceptions_fail_closed_in_sensor(self):
        a=KodiTelemetryReader(X,BadP()).sample(1.0)
        self.assertFalse(a.playing); self.assertIsNone(a.playback_time_s)
if __name__=='__main__':unittest.main()
