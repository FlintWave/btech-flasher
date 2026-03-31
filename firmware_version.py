"""
Firmware version parsing and comparison.

Handles version strings found in KDH radio firmware filenames:
  - "0.53", "V0.53"           → (0, 53, 0)
  - "1.27a", "V2.13A"        → (1, 27, 1) / (2, 13, 1)
  - None / unparseable       → (0, 0, 0)
"""

import re


def parse_version(version_str):
    """Parse a version string into a comparable tuple.

    Returns (major, minor, alpha_ordinal) where alpha_ordinal is 0 for
    no suffix, 1 for 'a', 2 for 'b', etc.
    """
    if not version_str:
        return (0, 0, 0)

    s = version_str.strip().lstrip("Vv")
    m = re.match(r'^(\d+)\.(\d+)([a-zA-Z])?$', s)
    if not m:
        return (0, 0, 0)

    major = int(m.group(1))
    minor = int(m.group(2))
    alpha = ord(m.group(3).lower()) - ord('a') + 1 if m.group(3) else 0
    return (major, minor, alpha)


def extract_version_from_filename(filename):
    """Extract a version string from a firmware filename.

    Examples:
        "BTECH_V0.53_260116.kdhx"         → "0.53"
        "UV25Pro_NRF_401+_V0.20_250217.kdhx" → "0.20"
        "RT-470_2.13A.rar"                 → "2.13A"
        "1.27a_firmware_240523.rar"        → "1.27a"
        "Firmware_Version_1.03.zip"        → "1.03"
        "random.kdhx"                      → None
    """
    if not filename:
        return None

    # Pattern 1: V/v prefix followed by version (e.g., V0.53, V0.20)
    m = re.search(r'[Vv](\d+\.\d+[a-zA-Z]?)', filename)
    if m:
        return m.group(1)

    # Pattern 2: _version_ or -version. (e.g., _2.13A.rar, _1.03.zip)
    m = re.search(r'[_\-](\d+\.\d+[a-zA-Z]?)(?:[_.\-]|$)', filename)
    if m:
        return m.group(1)

    # Pattern 3: starts with version (e.g., 1.27a_firmware)
    m = re.match(r'^(\d+\.\d+[a-zA-Z]?)[_\-]', filename)
    if m:
        return m.group(1)

    return None


def compare_versions(v1, v2):
    """Compare two version strings.

    Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2.
    Accepts raw version strings (will be parsed).
    """
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    if t1 < t2:
        return -1
    if t1 > t2:
        return 1
    return 0


def is_newer(candidate, baseline):
    """Return True if candidate version is strictly newer than baseline."""
    return compare_versions(candidate, baseline) > 0
