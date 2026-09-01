import hashlib, re
from urllib.parse import urlsplit, urlunsplit

_SECRET_KEYS = re.compile(r"(?i)\b(token|auth|authorization|cookie|api[_-]?key|key|signature|sig|expires|expiry|jwt|session|password|passwd|credential)\b")
_SECRET_ASSIGNMENT = re.compile(r"(?i)\b(token|auth|authorization|cookie|api[_-]?key|key|signature|sig|expires|expiry|jwt|session|password|passwd|credential)\s*[:=]\s*[^\s,;]+")
_URL = re.compile(r"(?i)\b(?:https?|rtmp|rtsp|udp)://\S+")
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")


def redact_text(text: str) -> str:
    text = _BEARER.sub("Bearer [REDACTED]", str(text or ""))
    text = _URL.sub("[REDACTED_URL]", text)
    return _SECRET_ASSIGNMENT.sub(lambda m: m.group(1) + "=[REDACTED]", text)


def safe_text_label(text: str, max_length: int = 120) -> str:
    """Redact URL/credential-like material from user-facing Kodi metadata."""
    cleaned = redact_text(str(text or "")).replace("\r", " ").replace("\n", " ").replace("\x00", " ").strip()
    return cleaned[:max(0, int(max_length))]


def safe_source_label(path: str) -> str:
    """Return scheme/host only; never path, query, fragment, credentials or tokens."""
    try:
        p = urlsplit(path or "")
        if p.scheme and p.hostname:
            return f"{p.scheme.lower()}://{p.hostname.lower()}"
    except Exception:
        pass
    return "local-or-kodi-managed"



def source_identity_key(path: str, *fallback_parts: str) -> str:
    """Return a stable, non-reversible key for stream-session boundaries.

    Query strings, fragments and URL credentials are removed before hashing so
    rotating access tokens do not create false source changes. The normalized
    path is never persisted or returned. For Kodi-managed schemes (for example
    pvr://) the same rule applies.
    """
    raw = str(path or "").strip()
    normalized = ""
    if raw:
        try:
            p = urlsplit(raw)
            if p.scheme:
                host = (p.hostname or "").lower()
                # p.port may raise ValueError for malformed input. Invalid ports are
                # ignored rather than falling back to hashing raw credential-bearing text.
                try:
                    port_value = p.port
                except ValueError:
                    port_value = None
                if ":" in host and not host.startswith("["):
                    host = f"[{host}]"
                port = f":{port_value}" if port_value else ""
                # Preserve scheme, host and path only. Never retain userinfo/query/fragment.
                normalized = urlunsplit((p.scheme.lower(), host + port, p.path or "", "", ""))
            else:
                # Kodi-managed/local paths can still contain query/fragment-like suffixes.
                normalized = raw.split("#",1)[0].split("?",1)[0]
        except Exception:
            # Last-resort normalization intentionally discards common credential and
            # URL suffix material before hashing. The value is never persisted.
            normalized = redact_text(raw).split("#",1)[0].split("?",1)[0]
    fallback = "|".join(safe_text_label(x, 160) for x in fallback_parts if str(x or "").strip())
    identity_material = normalized + ("|" + fallback if fallback else "")
    if not identity_material:
        return ""
    return hashlib.sha256(identity_material.encode("utf-8", "replace")).hexdigest()[:20]

def contains_secretish(text: str) -> bool:
    return bool(_SECRET_KEYS.search(str(text or "")) or _BEARER.search(str(text or "")))
