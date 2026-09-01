from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
addon=root/'service.streamdoctor'
out=root/'dist'; out.mkdir(exist_ok=True)
version=ET.parse(addon/'addon.xml').getroot().attrib['version']
zip_path=out/f'service.streamdoctor-{version}.zip'
source_path=out/f'kodi-stream-doctor-source-{version}.zip'
FIXED=(2026,1,1,0,0,0)


def write_entry(z, arcname, data):
    info=ZipInfo(str(arcname).replace('\\','/'), FIXED)
    info.compress_type=ZIP_DEFLATED
    info.external_attr=(0o644 & 0xFFFF) << 16
    z.writestr(info,data)


def build_addon():
    with ZipFile(zip_path,'w') as z:
        for p in sorted(addon.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                write_entry(z,Path('service.streamdoctor')/p.relative_to(addon),p.read_bytes())


def build_source():
    ignored={'dist','.git','.pytest_cache','__pycache__'}
    with ZipFile(source_path,'w') as z:
        for p in sorted(root.rglob('*')):
            rel=p.relative_to(root)
            if not p.is_file() or p.name=='.coverage' or any(part in ignored for part in rel.parts) or p.suffix=='.pyc':
                continue
            write_entry(z,Path('kodi-stream-doctor')/rel,p.read_bytes())


def checksum(path):
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    (out/(path.name+'.sha256')).write_text(h+'  '+path.name+'\n',encoding='utf-8')
    return h

build_addon(); build_source()
for p in (zip_path,source_path):
    print(p); print(checksum(p))
