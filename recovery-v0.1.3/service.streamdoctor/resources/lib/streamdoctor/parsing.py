import re
from typing import Iterable, Optional

_NUMBER = re.compile(r"[-+]?\d+(?:\.\d+)?")
_LINK = re.compile(r"(\d+(?:\.\d+)?)\s*([GMK]?)(?:bit|bps)", re.I)
_REFRESH = re.compile(r"@\s*(\d+(?:[.,]\d+)?)")
_BITRATE = re.compile(r"([-+]?\d[\d.,]*)\s*([KMG]?)\s*(?:bit|b)(?:/s|ps)?", re.I)


def first_number(value) -> Optional[float]:
    if value is None:
        return None
    text=str(value).strip()
    m=re.search(r"[-+]?\d[\d.,]*", text)
    if not m: return None
    token=m.group(0)
    sign=""
    if token[:1] in "+-": sign,token=token[0],token[1:]
    if "." in token and "," in token:
        # Treat the right-most separator as decimal and the other as grouping.
        if token.rfind(".") > token.rfind(","):
            token=token.replace(",","")
        else:
            token=token.replace(".","").replace(",",".")
    elif "," in token:
        parts=token.split(",")
        if len(parts)==2 and 1 <= len(parts[1]) <= 2:
            token=parts[0]+"."+parts[1]
        else:
            token="".join(parts)
    try: return float(sign+token)
    except ValueError: return None


def as_int(value) -> Optional[int]:
    n = first_number(value)
    return int(round(n)) if n is not None else None



def _scaled_rate(value, target_unit: str) -> Optional[float]:
    """Parse localized K/M/G bit-rate text and return Kb/s or Mb/s.

    Kodi 22's process labels currently format live video bitrate in Mb/s and
    audio bitrate in Kb/s, but explicit unit parsing keeps the collector safe
    if formatting or localization changes.
    """
    if value is None:
        return None
    text = str(value).strip()
    m = _BITRATE.search(text)
    if not m:
        return first_number(text)
    n = first_number(m.group(1))
    if n is None:
        return None
    unit = (m.group(2) or "").upper()
    # Convert to bits/s first. Empty unit retains Kodi's expected label unit
    # via caller fallback; explicit units are always converted.
    scale = {"K": 1_000.0, "M": 1_000_000.0, "G": 1_000_000_000.0}.get(unit)
    if scale is None:
        return n
    bps = n * scale
    return bps / (1_000.0 if target_unit == "K" else 1_000_000.0)


def parse_bitrate_mbps(value) -> Optional[float]:
    return _scaled_rate(value, "M")


def parse_bitrate_kbps(value) -> Optional[float]:
    return _scaled_rate(value, "K")



def parse_frequency_mhz(value) -> Optional[float]:
    if value is None:
        return None
    text=str(value).strip()
    n=first_number(text)
    if n is None:
        return None
    compact=text.lower().replace(" ","")
    if "ghz" in compact: return n*1000.0
    if "khz" in compact: return n/1000.0
    # Kodi commonly reports MHz; an explicit Hz unit is uncommon but safe to handle.
    if re.search(r"(?<![kmg])hz",compact): return n/1_000_000.0
    return n


def parse_temperature_c(value, units_hint="") -> Optional[float]:
    if value is None:
        return None
    text=str(value).strip()
    n=first_number(text)
    if n is None:
        return None
    hint=(str(units_hint or "")+" "+text).lower()
    # Kodi's configured temperature unit can be Fahrenheit. Never feed a raw
    # Fahrenheit number to Celsius thresholds.
    if "°f" in hint or re.search(r"(?:^|[^a-z])f(?:ahrenheit)?(?:$|[^a-z])",hint):
        return (n-32.0)*5.0/9.0
    return n

def parse_percent(value) -> Optional[float]:
    n = first_number(value)
    if n is None:
        return None
    return max(0.0, min(100.0, n))


def parse_cpu_usage(value) -> Optional[float]:
    if not value:
        return None
    nums = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*%", str(value))]
    if not nums:
        n = first_number(value)
        return max(0.0, min(100.0, n)) if n is not None else None
    return max(0.0, min(100.0, sum(nums) / len(nums)))


def parse_link_mbps(value) -> Optional[float]:
    if not value:
        return None
    m = _LINK.search(str(value).replace(" ", ""))
    if not m:
        return None
    n = float(m.group(1)); unit = m.group(2).upper()
    if unit == "G": return n * 1000.0
    if unit == "K": return n / 1000.0
    return n


def parse_refresh_hz(value) -> Optional[float]:
    if not value:
        return None
    m = _REFRESH.search(str(value))
    if m: return first_number(m.group(1))
    for token in re.findall(r"\d+(?:[.,]\d+)?", str(value)):
        n = first_number(token)
        if n is None: continue
        if 20.0 <= n <= 500.0:
            return n
    return None


def median(values: Iterable[Optional[float]]) -> Optional[float]:
    vals = sorted(float(v) for v in values if v is not None)
    if not vals: return None
    mid = len(vals) // 2
    if len(vals) % 2: return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0
