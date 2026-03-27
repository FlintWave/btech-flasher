# Usage Guide

## Getting Started

### Install dependencies

```
pip install pyserial wxPython requests
```

On Linux, add your user to the `dialout` group for serial port access:

```
sudo usermod -aG dialout $USER
```

Log out and back in for the group change to take effect.

### Launch the GUI

```
python3 flash_firmware_gui.py
```

Or search for "BTECH Firmware Flasher" in your desktop app launcher if a `.desktop` entry has been created.

## Flashing Firmware

### Step 1: Select your radio

Use the **Radio** dropdown at the top of the window to select your radio model. The info line below shows the bootloader key combination and connector type for your model.

### Step 2: Get the firmware file

**Option A — Automatic download:**
If your radio has a direct download URL (the "Download Latest" button is enabled), click it. The tool will download the firmware bundle from the manufacturer's website, extract the `.kdhx` file, and fill in the firmware path automatically.

**Option B — Manual download:**
Visit your radio manufacturer's website, download the firmware bundle (usually a `.zip`), extract it, and use the **Browse...** button to select the `.kdhx` file.

### Step 3: Select your serial port

Click **Find Cable...** to open the port finder wizard. It scans for connected USB serial devices and identifies known programming cable chips (FTDI, CH340, Prolific, etc.). The PC03 cable is auto-highlighted in green.

**Tip:** If your cable isn't listed, unplug it, click Rescan, plug it back in, and click Rescan again. The new entry is your cable.

### Step 4: Verify with a dry run

Click **Dry Run** to verify the firmware file without touching the radio. This checks:
- File size is within protocol limits
- ARM vector table has valid stack pointer and reset handler
- All data packets build correctly with valid CRCs
- SHA-256 hash is displayed for verification against published hashes

### Step 5: Test serial communication

With the radio in bootloader mode (see below), click **Run Diagnostics** to test whether the tool can communicate with the radio. If you see a response, you're good to flash.

### Step 6: Flash

1. Put the radio in **bootloader mode**:
   - Power off the radio
   - Hold the bootloader keys (shown in the radio info line — e.g., SK1 + SK2 for BF-F8HP Pro)
   - While holding, turn the power/volume knob to power on
   - The screen stays blank and the green Rx LED lights up

2. Click **Flash Firmware**. Confirm the warning dialog.

3. Wait for the progress bar to complete. Do not disconnect the cable or power off the radio during flashing.

4. When complete, power cycle the radio and verify the firmware version via **Menu > Radio Info**.

## Bootloader Mode Quick Reference

| Radio | Keys to Hold |
|-------|-------------|
| BTECH BF-F8HP Pro | SK1 (top) + SK2 (bottom) — not PTT |
| Baofeng UV-25 Plus/Pro | SK2 + SK3 |
| Others | Check your radio's manual or `radios.json` |

**Important:** The side keys are the small buttons above and below the large PTT button. Do not hold PTT itself.

## Themes and Accessibility

Use **View > Theme** to switch between:
- **System Default** — follows your OS theme
- **Latte** — Catppuccin light theme
- **Frappe** — Catppuccin medium-dark theme
- **Macchiato** — Catppuccin dark theme
- **Mocha** — Catppuccin darkest theme
- **High Contrast** — black background, yellow/green text

Use **View > Log Font Size** to adjust text size (8pt, 9pt, 11pt, or 14pt).

## Command Line Interface

The CLI provides the same functionality without the GUI.

### Flash firmware

```
python3 flash_firmware.py /dev/ttyUSB0 firmware.kdhx
```

### Dry run

```
python3 flash_firmware.py --dry-run none firmware.kdhx
```

### Diagnostics

```
python3 flash_firmware.py --diag /dev/ttyUSB0
```

## Auto-Updates

The GUI checks GitHub for updates on each launch. If a newer version is available, you'll be prompted to update. Updates are pulled via `git pull` and the app restarts automatically.

## Troubleshooting

### "No response from radio"

- Make sure the radio is in bootloader mode (blank screen, green LED)
- Check that the cable is plugged in and detected (use Find Cable)
- Try unplugging and replugging the cable
- Ensure your user is in the `dialout` group

### Radio powers off when sending data

- The cable's RX line may be faulty — try a different cable
- Some cables have direction control issues on Linux

### "Firmware too large" or "too many chunks"

- The protocol supports up to 255 chunks (261,120 bytes). Your firmware file may not be a valid `.kdhx` file.

### Themes don't apply to all widgets

- On Linux, GTK CSS is used for native widget theming. If some widgets don't respond, try switching back to System Default and then to your desired theme.
- On Windows/macOS, native widgets may not fully support custom theming.

## Adding New Radios

Edit `radios.json` to add your radio. Required fields:

```json
{
  "id": "your-radio-id",
  "name": "Radio Name",
  "manufacturer": "Brand",
  "model_type": "MODEL",
  "firmware_url": null,
  "firmware_page": "https://manufacturer.com/downloads",
  "firmware_filename_pattern": "*.kdhx",
  "bootloader_keys": "Key combination",
  "connector": "K1 Kenwood 2-pin",
  "tested": false,
  "notes": "Any relevant notes"
}
```

Submit a PR to share your addition with the community.
