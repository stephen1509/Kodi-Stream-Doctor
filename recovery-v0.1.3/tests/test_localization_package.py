import os,re,unittest,xml.etree.ElementTree as ET
ROOT=os.path.dirname(os.path.dirname(__file__))
SETTINGS=os.path.join(ROOT,'service.streamdoctor','resources','settings.xml')
STRINGS=os.path.join(ROOT,'service.streamdoctor','resources','language','resource.language.en_gb','strings.po')

class LocalizationPackageTests(unittest.TestCase):
    def test_every_numeric_settings_label_and_help_has_english_string(self):
        root=ET.parse(SETTINGS).getroot()
        ids=set()
        for node in root.iter():
            for attr in ('label','help'):
                value=node.attrib.get(attr,'')
                if value.isdigit(): ids.add(value)
        text=open(STRINGS,encoding='utf-8').read()
        defined=set(re.findall(r'msgctxt "#(\d+)"',text))
        self.assertEqual(ids-defined,set())

    def test_settings_catalog_is_packaged_under_kodi_language_path(self):
        self.assertTrue(os.path.isfile(STRINGS))

if __name__=='__main__': unittest.main()
