# KDH Bootloader Firmware Flasher

A cross-platform tool for flashing `.kdhx` firmware files to BTECH, Baofeng, Radtel, and other radios that use the KDH bootloader — no Wine or Windows VM needed.

Maintained by [FlintWave Radio Tools](https://github.com/FlintWave). Contact: flintwave@tuta.com

## Status

**Untested** — the protocol implementation has been verified via dry-run packet construction and CRC validation, but has not yet been confirmed on hardware due to a faulty programming cable. Community testing reports welcome — please open an issue.

## Supported Radios

| Radio | Manufacturer | Tested |
|-------|-------------|--------|
| BF-F8HP Pro | BTECH | No |
| UV-25 Plus / UV-25 Pro | Baofeng | No |
| UV-17 Pro | Baofeng | No |
| UV-18 Pro | Baofeng | No |
| UV-21 Pro | Baofeng | No |
| RT-470 | Radtel | No |
| RT-490 | Radtel | No |
| JC-8629 | JJCC | No |

Radio definitions live in `radios.json` — community contributions welcome via PR.

## Requirements

- Python 3.10+
- [pyserial](https://pypi.org/project/pyserial/) (`pip install pyserial`)
- [wxPython](https://pypi.org/project/wxPython/) (for the GUI; `pip install wxPython` or install via your distro's package manager)
- [requests](https://pypi.org/project/requests/) (for firmware download; `pip install requests`)
- A compatible FTDI programming cable (BTECH PC03 or similar K1 2-pin Kenwood cable)
- Linux/macOS: your user must be in the `dialout` group:
  ```
  sudo usermod -aG dialout $USER
  ```

## Usage

### GUI

```
python3 flash_firmware_gui.py
```

Features:
- Radio model selector with firmware download
- Port finder wizard with auto-detection of PC03 cables
- Dry run mode (verify firmware without flashing)
- Serial diagnostics
- Auto-update from GitHub on launch

### CLI: Flash firmware

1. Download the firmware bundle from your radio's manufacturer (or use the GUI's download button)
2. Put the radio in bootloader mode:
   - Power off the radio
   - Hold the bootloader keys (see `radios.json` for your model — e.g., SK1+SK2 for BF-F8HP Pro)
   - While holding, turn the power/volume knob to power on
   - Screen stays blank, green Rx LED lights up
3. Run:
   ```
   python3 flash_firmware.py /dev/ttyUSB0 firmware.kdhx
   ```

### CLI: Dry run

```
python3 flash_firmware.py --dry-run none firmware.kdhx
```

### CLI: Diagnostics

```
python3 flash_firmware.py --diag /dev/ttyUSB0
```

## Protocol

The KDH bootloader uses a packetized serial protocol at 115200 baud (8N1).

### Packet format

```
[0xAA][cmd][seed][lenH][lenL][data...][crcH][crcL][0xEF]
```

- **0xAA** — header
- **cmd** — command byte
- **seed** — sequence number / argument
- **lenH:lenL** — data length (big-endian 16-bit)
- **data** — payload
- **crcH:crcL** — CRC-16/CCITT over cmd+seed+len+data (poly 0x1021, init 0x0000)
- **0xEF** — trailer

### Manual download sequence

When the radio is already in bootloader mode:

| Step | Command | Byte | Payload |
|------|---------|------|---------|
| 1 | Handshake | 0x01 | `"BOOTLOADER"` (10 bytes) |
| 2 | Announce chunks | 0x04 | 1 byte: total number of 1024-byte chunks |
| 3 | Send data (repeat) | 0x03 | 1024 bytes of firmware per chunk |
| 4 | End | 0x45 | (none) |

Each command expects an ACK response: same packet format with `cmdArgs = 0x06`.

### Error codes

| Code | Meaning |
|------|---------|
| 0xE1 | Handshake code error (fatal) |
| 0xE2 | Data verification error (retryable, up to 5 attempts) |
| 0xE3 | Incorrect address error (fatal) |
| 0xE4 | Flash write error (fatal) |
| 0xE5 | Command error (fatal) |

## Contributing

- **Test reports** — if you successfully flash a radio, open an issue so we can mark it as tested
- **New radios** — add your radio to `radios.json` and submit a PR
- **Bug fixes** — always welcome

## License

MIT
