# Mochi updates

Robot firmware, Android app and iPhone app releases for Mochi, the desk robot by Bot Engineers. Every version stays here, so older ones are always available too.

## For Mochi owners

You don't need to do anything here. The Mochi Android app checks this page every few hours, tells you when there is something new, and installs it with one tap: open your robot in the app, then **⋮ → Updates** (or **Settings → Firmware → Check for updates**). The same list lets you go back to an older robot version.

Without the Android app: download `mochi-firmware-vN.bin` from [Releases](https://github.com/NOXUSTIC/mochi-updates/releases), open the robot's web app, and use **Settings → Firmware → Update from a file**.

**iPhone:** download `Mochi-X.Y-unsigned.ipa` from the newest `ios-vX.Y` release and follow its steps: it is installed from a computer with Sideloadly and your own Apple ID (iPhones can't install apps straight from a download).

Only files from this page work. Robots running firmware v6 or newer check Bot Engineers' signature and refuse any other file.

## What's here

- [Releases](https://github.com/NOXUSTIC/mochi-updates/releases): `firmware-vN` (robot firmware, signed) `app-vX.Y` (the Android app, `Mochi-X.Y.apk`) and `ios-vX.Y` (the iPhone app, unsigned `Mochi-X.Y-unsigned.ipa`; not in `updates.json`).
- `updates.json`: the list the app reads, newest first. Each entry has the file's `size` and `sha256`; the app refuses a download that doesn't match.

## Publishing (Bot Engineers)

From the Mochi source repo, on the PC that holds the signing keys (`~/mochi-keys`):

```
python tools/publish.py firmware --notes "What changed"   # raise FW_VER in c3_mochi_pro.ino first
python tools/publish.py app --notes "What changed"        # raise VERSION_CODE and VERSION_NAME in android/build_apk.py first
```

The script builds, signs, creates the release and adds it to `updates.json`. Avoid editing `updates.json` by hand.
