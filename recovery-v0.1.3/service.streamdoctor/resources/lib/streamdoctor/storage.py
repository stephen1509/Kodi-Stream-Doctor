import json, os, re, time
from typing import Dict, List
from .redaction import redact_text, safe_source_label

MAX_FILES_HARD = 20
MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024


_SECRET_FIELD = re.compile(r"(?i)^(?:token|auth|authorization|cookie|api[_-]?key|signature|sig|jwt|session|password|passwd|credential)$")

def _sanitize_for_storage(obj, key=""):
    if isinstance(obj, dict):
        out={}
        for k,v in obj.items():
            sk=str(k)
            if sk == "source_key":
                continue
            if _SECRET_FIELD.match(sk):
                out[k]="[REDACTED]"
            else:
                out[k]=_sanitize_for_storage(v,sk)
        return out
    if isinstance(obj, list):
        return [_sanitize_for_storage(v,key) for v in obj]
    if isinstance(obj, tuple):
        return [_sanitize_for_storage(v,key) for v in obj]
    if isinstance(obj, str):
        if key == "source_origin":
            return safe_source_label(obj)
        return redact_text(obj)
    return obj

def _safe_json_bytes(obj: Dict) -> bytes:
    obj=_sanitize_for_storage(obj)
    raw = json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    if len(raw) > MAX_FILE_BYTES:
        # Reports deliberately omit raw sample dumps; this should almost never trigger.
        slim = dict(obj)
        slim["storage_warning"] = "Report exceeded privacy size cap; nonessential detail omitted."
        slim.pop("samples", None)
        raw = json.dumps(slim, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("report exceeds 4 MiB hard cap")
    return raw


def write_report(directory: str, report: Dict, max_files: int = 20) -> str:
    os.makedirs(directory, exist_ok=True)
    max_files = max(1, min(MAX_FILES_HARD, int(max_files or MAX_FILES_HARD)))
    raw = _safe_json_bytes(report)
    ns = time.time_ns()
    name = time.strftime("streamdoctor-%Y%m%d-%H%M%S", time.localtime(ns / 1_000_000_000)) + f"-{ns % 1_000_000_000:09d}.json"
    path = os.path.join(directory, name)
    # Some filesystems/platform clocks have coarse timestamp resolution. Never
    # overwrite a prior report if two stream sessions finish effectively at once.
    collision = 0
    while os.path.exists(path):
        collision += 1
        path = os.path.join(directory, name[:-5] + f"-{collision:02d}.json")
    temp = path + ".tmp"
    try:
        with open(temp, "wb") as f:
            f.write(raw)
            f.flush()
            try: os.fsync(f.fileno())
            except OSError: pass
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            try: os.remove(temp)
            except OSError: pass
    enforce_retention(directory, max_files)
    return path


def enforce_retention(directory: str, max_files: int = 20) -> None:
    max_files = max(1, min(MAX_FILES_HARD, int(max_files)))
    files: List[str] = []
    for n in os.listdir(directory):
        p = os.path.join(directory, n)
        if n.startswith("streamdoctor-") and n.endswith(".json") and os.path.isfile(p): files.append(p)
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    total = 0
    for idx, p in enumerate(files):
        size = os.path.getsize(p)
        keep = idx < max_files and total + size <= MAX_TOTAL_BYTES and size <= MAX_FILE_BYTES
        if keep: total += size
        else:
            try: os.remove(p)
            except OSError: pass


def load_reports(directory: str, limit: int = 20):
    if not os.path.isdir(directory): return []
    files=[os.path.join(directory,n) for n in os.listdir(directory) if n.startswith("streamdoctor-") and n.endswith(".json")]
    files.sort(key=lambda p:os.path.getmtime(p), reverse=True)
    out=[]
    wanted=max(0,min(MAX_FILES_HARD,int(limit)))
    for p in files:
        if len(out) >= wanted:
            break
        try:
            # Never ingest an unexpectedly large/corrupt report file placed in the
            # profile directory by another process. Stream Doctor's own reports are capped.
            if os.path.getsize(p) > MAX_FILE_BYTES:
                continue
            with open(p,encoding="utf-8") as f:
                report=json.load(f)
            if isinstance(report,dict):
                out.append(report)
        except Exception:
            continue
    return out
