"""
Remote firmware manifest fetcher and local flash state tracker.

Fetches firmware_manifest.json from the GitHub repo to discover new
firmware versions without requiring an app update. Caches the manifest
locally and tracks which firmware versions have been flashed to each radio.
"""

import json
import os
import tempfile
import time
from datetime import datetime, timezone

import requests

MANIFEST_URL = (
    "https://raw.githubusercontent.com/FlintWave/flintwave-kdh-flasher"
    "/master/firmware_manifest.json"
)
USER_AGENT = "flintwave-kdh-flasher/1.0 (https://github.com/FlintWave/flintwave-kdh-flasher)"

STATE_DIR = os.path.join(os.path.expanduser("~"), ".flintwave-kdh-flasher")
STATE_FILE = os.path.join(STATE_DIR, "state.json")

MANIFEST_CACHE_TTL = 300  # 5 minutes


def _load_state():
    """Load state from disk. Returns empty dict on missing/corrupt file."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def _save_state(state):
    """Write state atomically (temp file + rename)."""
    os.makedirs(STATE_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=STATE_DIR, suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, STATE_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def fetch_manifest(force=False):
    """Fetch the remote firmware manifest, with caching.

    Returns the manifest dict (the "radios" key mapping radio IDs to info),
    or None if fetch fails and no cache exists.
    """
    state = _load_state()
    cache = state.get("manifest_cache", {})

    # Use cache if fresh enough
    if not force and cache.get("data") and cache.get("last_fetched"):
        try:
            age = time.time() - cache["last_fetched"]
            if age < MANIFEST_CACHE_TTL:
                return cache["data"]
        except (TypeError, ValueError):
            pass

    # Fetch from remote
    try:
        resp = requests.get(
            MANIFEST_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        manifest = resp.json()
        radios = manifest.get("radios", {})

        # Cache it
        state["manifest_cache"] = {
            "last_fetched": time.time(),
            "data": radios,
        }
        _save_state(state)
        return radios

    except Exception:
        # Return stale cache if available
        if cache.get("data"):
            return cache["data"]
        return None


def get_radio_firmware_info(radio_id, manifest=None):
    """Look up firmware info for a radio from the manifest.

    Returns dict with keys: firmware_version, firmware_url, firmware_sha256,
    release_notes. Returns None if radio not in manifest.
    """
    if manifest is None:
        manifest = fetch_manifest()
    if not manifest:
        return None
    return manifest.get(radio_id)


def record_flash(radio_id, version, sha256):
    """Record a successful flash to local state."""
    state = _load_state()
    if "last_flashed" not in state:
        state["last_flashed"] = {}
    state["last_flashed"][radio_id] = {
        "version": version,
        "firmware_sha256": sha256,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _save_state(state)


def get_last_flashed(radio_id):
    """Get the last-flashed firmware info for a radio.

    Returns dict with version, firmware_sha256, timestamp, or None.
    """
    state = _load_state()
    return state.get("last_flashed", {}).get(radio_id)
