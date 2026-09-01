import os,sys,unittest
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.redaction import source_identity_key

class StreamIdentityTests(unittest.TestCase):
    def test_rotating_query_credentials_do_not_change_identity(self):
        a=source_identity_key('https://user:pw@example.invalid/live/ch42.m3u8?token=aaa&sig=111#x')
        b=source_identity_key('https://other:secret@example.invalid/live/ch42.m3u8?token=bbb&sig=222#y')
        self.assertEqual(a,b)
        self.assertNotIn('aaa',a); self.assertNotIn('ch42',a)

    def test_different_stream_paths_have_different_identity(self):
        self.assertNotEqual(source_identity_key('https://example.invalid/live/ch1.m3u8'),source_identity_key('https://example.invalid/live/ch2.m3u8'))

    def test_pvr_paths_are_distinguishable_without_exposing_path(self):
        a=source_identity_key('pvr://channels/tv/All channels/1@pvr')
        b=source_identity_key('pvr://channels/tv/All channels/2@pvr')
        self.assertNotEqual(a,b)
        self.assertEqual(len(a),20)

if __name__=='__main__': unittest.main()
