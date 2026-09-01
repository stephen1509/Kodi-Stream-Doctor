#!/usr/bin/env python3
"""Repeatable local engineering gates for Stream Doctor."""
from __future__ import annotations

import compileall
import hashlib
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
ADDON=ROOT/'service.streamdoctor'
DIST=ROOT/'dist'


def fail(msg:str):
    raise SystemExit('QA FAIL: '+msg)


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def main():
    print('1/7 compile')
    if not compileall.compile_dir(str(ADDON),quiet=1): fail('Python compile')

    print('2/7 XML')
    for p in (ADDON/'addon.xml',ADDON/'resources/settings.xml'): ET.parse(p)

    print('3/7 tests')
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful(): fail('unit/integration suite')

    print('4/7 static safety')
    prod='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in ADDON.rglob('*.py'))
    forbidden_mutation=r'\b(Set-Net|Disable-Net|Enable-Net|Remove-Net|Restart-Net|netsh|powercfg|Set-CimInstance|Remove-CimInstance|Invoke-CimMethod)\b'
    forbidden_network=r'\b(requests|urllib\.request|http\.client|aiohttp|OPENAI_API_KEY|api\.openai\.com)\b'
    if re.search(forbidden_mutation,prod,re.I): fail('mutating Windows/network command found')
    if re.search(forbidden_network,prod,re.I): fail('outbound HTTP/OpenAI client found in v0.1')

    version=ET.parse(ADDON/'addon.xml').getroot().attrib['version']
    init_text=(ADDON/'resources/lib/streamdoctor/__init__.py').read_text(encoding='utf-8')
    m=re.search(r'__version__\s*=\s*["\']([^"\']+)',init_text)
    if not m or m.group(1) != version: fail('internal library version does not match addon.xml')

    print('5/7 build')
    subprocess.run([sys.executable,str(ROOT/'tools/build_zip.py')],check=True,cwd=ROOT)

    print('6/7 package')
    addon_zip=DIST/f'service.streamdoctor-{version}.zip'
    source_zip=DIST/f'kodi-stream-doctor-source-{version}.zip'
    for zpath in (addon_zip,source_zip):
        with ZipFile(zpath) as z:
            bad_member=z.testzip()
            if bad_member: fail(f'ZIP CRC failure in {zpath.name}: {bad_member}')
            names=z.namelist()
            if any('__pycache__' in n or n.endswith('.pyc') for n in names): fail(f'cache bytecode in {zpath.name}')
            if zpath==addon_zip:
                req={'service.streamdoctor/addon.xml','service.streamdoctor/LICENSE.txt','service.streamdoctor/service.py','service.streamdoctor/default.py','service.streamdoctor/resources/language/resource.language.en_gb/strings.po'}
                if not req.issubset(names): fail('install ZIP missing required files')
                if not all(n.startswith('service.streamdoctor/') for n in names): fail('wrong install ZIP root')

    print('7/7 checksums')
    print(' addon ',sha256(addon_zip))
    print(' source',sha256(source_zip))
    print(f'QA PASS: {result.testsRun} tests')

if __name__=='__main__': main()
