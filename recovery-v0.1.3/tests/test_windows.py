import json,os,sys,unittest
from unittest.mock import patch
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,os.path.join(ROOT,'service.streamdoctor','resources','lib'))
from streamdoctor import windows

class _CP:
    def __init__(self,returncode=0,stdout=''):
        self.returncode=returncode; self.stdout=stdout

class WindowsInspectorTests(unittest.TestCase):
    def test_non_windows_fails_open(self):
        with patch.object(windows.platform,'system',return_value='Linux'):
            ctx=windows.inspect_windows()
        self.assertEqual(ctx.platform,'linux')
        self.assertTrue(any('unavailable' in n.lower() for n in ctx.notes))

    def test_windows_inventory_parses_supported_read_only_fields(self):
        payload={
            'cpu':{'Name':'Example CPU','NumberOfCores':8,'NumberOfLogicalProcessors':16,'MaxClockSpeed':4200},
            'os':{'Caption':'Windows 11 Pro','Version':'10.0.26100','BuildNumber':'26100','TotalVisibleMemorySize':33554432,'FreePhysicalMemory':1000},
            'gpu':[{'Name':'Example GPU','DriverVersion':'31.0.1','DriverDate':'2026-01-02'}],
            'power_plan':'Power Scheme GUID: x (Balanced)',
            'net':[{'Name':'Ethernet','Description':'Example NIC','LinkSpeed':'2.5 Gbps','DriverVersion':'1.2','DriverDate':'2025-12-03','ReceivedPacketErrors':2,'OutboundPacketErrors':3,'ReceivedDiscardedPackets':4,'OutboundDiscardedPackets':5}],
        }
        with patch.object(windows.platform,'system',return_value='Windows'), patch.object(windows.subprocess,'run',return_value=_CP(0,json.dumps(payload))):
            ctx=windows.inspect_windows()
        self.assertEqual(ctx.cpu_name,'Example CPU')
        self.assertEqual(ctx.cpu_cores,8); self.assertEqual(ctx.logical_processors,16)
        self.assertEqual(ctx.cpu_max_mhz,4200.0)
        self.assertEqual(ctx.total_ram_gb,32.0)
        self.assertEqual(ctx.gpu_names,['Example GPU'])
        self.assertEqual(ctx.gpu_driver_versions,['31.0.1']); self.assertEqual(ctx.gpu_driver_dates,['2026-01-02'])
        self.assertEqual(ctx.adapter_names,['Ethernet'])
        self.assertEqual(ctx.adapter_driver_versions,['1.2']); self.assertEqual(ctx.adapter_driver_dates,['2025-12-03'])
        self.assertIn('Balanced',ctx.power_plan)
        self.assertEqual(ctx.adapter_link_mbps,[2500.0])
        self.assertEqual(ctx.adapter_rx_errors,2); self.assertEqual(ctx.adapter_tx_errors,3)
        self.assertEqual(ctx.adapter_rx_discards,4); self.assertEqual(ctx.adapter_tx_discards,5)

    def test_windows_command_failure_does_not_disable_kodi_telemetry(self):
        with patch.object(windows.platform,'system',return_value='Windows'), patch.object(windows.subprocess,'run',return_value=_CP(1,'')):
            ctx=windows.inspect_windows()
        self.assertTrue(any('failed' in n.lower() for n in ctx.notes))

    def test_windows_exception_is_contained(self):
        with patch.object(windows.platform,'system',return_value='Windows'), patch.object(windows.subprocess,'run',side_effect=TimeoutError):
            ctx=windows.inspect_windows()
        self.assertTrue(any('timeouterror' in n.lower() for n in ctx.notes))

if __name__=='__main__': unittest.main()
