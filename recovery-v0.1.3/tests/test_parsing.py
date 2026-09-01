import os, sys, unittest
ROOT=os.path.dirname(os.path.dirname(__file__)); sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor.parsing import parse_link_mbps, parse_refresh_hz, parse_cpu_usage, first_number, parse_bitrate_mbps, parse_bitrate_kbps, parse_temperature_c, parse_frequency_mhz
class ParsingTests(unittest.TestCase):
    def test_link(self):
        self.assertEqual(parse_link_mbps('1 Gbit/s'),1000); self.assertEqual(parse_link_mbps('100mbit'),100)
    def test_refresh(self):
        self.assertAlmostEqual(parse_refresh_hz('1920x1080 @ 59.940 - Full Screen'),59.94)
        self.assertAlmostEqual(parse_refresh_hz('1920x1080 @ 59,94 - Full Screen'),59.94)
    def test_cpu(self): self.assertAlmostEqual(parse_cpu_usage('CPU0: 20% CPU1: 40%'),30)
    def test_localized_decimal(self):
        self.assertEqual(first_number('8,5 Mb/s'),8.5)
        self.assertEqual(first_number('1,000 MB'),1000)
        self.assertEqual(first_number('1.234,5 MB'),1234.5)
    def test_bitrate_units(self):
        self.assertAlmostEqual(parse_bitrate_mbps('8500 Kb/s'),8.5)
        self.assertAlmostEqual(parse_bitrate_mbps('8,5 Mb/s'),8.5)
        self.assertAlmostEqual(parse_bitrate_mbps('0.01 Gbit/s'),10.0)
        self.assertAlmostEqual(parse_bitrate_kbps('0.192 Mb/s'),192.0)
        self.assertAlmostEqual(parse_bitrate_kbps('192 Kb/s'),192.0)
    def test_temperature_units(self):
        self.assertAlmostEqual(parse_temperature_c('90 C','°C'),90.0)
        self.assertAlmostEqual(parse_temperature_c('194 °F','°F'),90.0)
        self.assertAlmostEqual(parse_temperature_c('194','Fahrenheit'),90.0)

    def test_frequency_units(self):
        self.assertAlmostEqual(parse_frequency_mhz('3.20 GHz'),3200.0)
        self.assertAlmostEqual(parse_frequency_mhz('3200 MHz'),3200.0)
        self.assertAlmostEqual(parse_frequency_mhz('3200000 KHz'),3200.0)

if __name__=='__main__': unittest.main()
