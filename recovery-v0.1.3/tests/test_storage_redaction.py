import os,sys,tempfile,unittest,json
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.redaction import redact_text,safe_source_label,safe_text_label
from streamdoctor.storage import write_report,MAX_FILES_HARD
class StorageTests(unittest.TestCase):
    def test_redact(self):
        self.assertNotIn('secret',redact_text('Bearer secret'))
        self.assertEqual(safe_source_label('https://user:pw@example.com/a?token=secret'),'https://example.com')
        self.assertNotIn('abc123',safe_text_label('Sports token=abc123'))
        self.assertNotIn('/secret',safe_text_label('https://example.com/secret?sig=abc'))
    def test_retention(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(25): write_report(d,{'i':i},20)
            self.assertLessEqual(len(os.listdir(d)),MAX_FILES_HARD)
    def test_report_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=write_report(d,{'ok':True},20)
            with open(p, encoding='utf-8') as f: self.assertTrue(json.load(f)['ok'])
    def test_back_to_back_reports_never_overwrite_each_other(self):
        with tempfile.TemporaryDirectory() as d:
            p1=write_report(d,{'i':1},20)
            p2=write_report(d,{'i':2},20)
            self.assertNotEqual(p1,p2)
            self.assertEqual(len([n for n in os.listdir(d) if n.endswith('.json')]),2)

    def test_atomic_write_leaves_no_temp_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=write_report(d,{'ok':True},20)
            self.assertTrue(os.path.exists(p))
            self.assertFalse(any(name.endswith('.tmp') for name in os.listdir(d)))
if __name__=='__main__':unittest.main()
