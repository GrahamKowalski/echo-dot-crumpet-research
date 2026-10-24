# mtkclient gettargetconfig attempt, 2026-10-24

I used mtkclient (pinned at commit `cd25cf9`, the same commit this repo's own audit scripts already trust) to run its `gettargetconfig` command against the same unit, over the Raspberry Pi 3's forced-full-speed USB connection described in [usb-preloader-capture-2026-10-24.md](usb-preloader-capture-2026-10-24.md). Unlike everything in that note, this is an active step: `gettargetconfig` sends real commands to the live preloader, including a register write. I'm recording what happened plainly, including what went wrong and what I don't know.

## Setup

- mtkclient cloned from github.com/bkerler/mtkclient and checked out at commit `cd25cf9`. Installed in a Python venv on the Raspberry Pi 3, omitting the GUI (`pyside6`/`shiboken6`) and exploit-payload-assembly (`keystone-engine`, `unicorn`) dependencies, since `gettargetconfig` needs none of them.
- Checked as of 2026-10-24: zero commits to the files this command actually exercises (`mtk_preloader.py`, `devicehandler.py`) between the pinned commit and upstream `main`, and no open or closed mtkclient issue matching this failure for this chip family. This isn't a stale-tool artifact.
- Ran as `mtk.py gettargetconfig`, and later `mtk.py gettargetconfig --debugmode` for a fuller trace. This command reads back the preloader's security configuration (secure boot check, DA authentication, etc.). It sends no DA, no flash read or write, no exploit payload.
- UART (921600 baud, host-timestamped) and a passive descriptor watcher ([usbwatch.py](../scripts/usbwatch.py)) ran throughout, as in the earlier capture.

## What happened (observed, reproduced across 8 separate power-cycles)

1. mtkclient's low-level handshake with the preloader needed one retry (a first-byte echo mismatch), then succeeded, every time.
2. The preloader correctly identified itself: CPU family MT8167/MT8516/MT8362, HW version 0x0, watchdog register `0x10007000`, UART `0x11005000`, BROM payload address `0x100a00`, DA payload address `0x201000`, Var1 `0xcc`.
3. mtkclient's first subsequent action, disabling the watchdog timer via a register write, sent and got a correct echo for every part of the exchange: the one-byte command, the 4-byte register address (`10007000`, matching step 2), and the 4-byte value (`00000001`).
4. **The read of the write's acknowledgment never came back.** 18 to 24 consecutive `Timed out` reads, then a hard `USBError(5, 'Input/Output Error')`, and mtkclient exits.
5. This exact sequence, byte for byte, repeated identically across every attempt that caught the device — confirmed directly for 3 of them with `--debugmode` on.
6. The board's own UART log independently confirms the same failure from its side: `USB_HANDSHAKE: should be 2 bytes less than 512 bytes`, followed by the board itself looping on `usb receive timeout`.

## Effect on the device (observed, and what I don't know)

- **On the boot where this happens:** the preloader does not proceed to LK. No LED ring runs (that's a LK-stage animation), and the UART log shows no further progress past the repeating `usb receive timeout` line.
- **This is not persistent.** Disconnecting the USB cable and power-cycling the unit produces a completely normal boot: `BOOT_TIME: 1340` (the short, no-interaction baseline), LED ring, LK, and kernel console all present, with zero `USB_HANDSHAKE`/timeout lines. I verified this directly, twice, on separate occasions in this session, including once confirmed visually (the LED ring returning) before I checked the log.
- **I don't know whether the watchdog-disable write actually took effect before the acknowledgment read failed.** The address and value were both transmitted and echoed back correctly, which tells me the device received and understood the command, not whether it executed the write before, or instead of, sending a reply. I'm not claiming either way.
- I attempted nothing beyond `gettargetconfig`. No DA was selected or uploaded, no flash was read or written, no exploit payload was run.

## How this fits what's already documented here

This repo's existing docs (STATUS.md, [mtkclient-stage2-nand-profile-transport.md](../docs/mtkclient-stage2-nand-profile-transport.md), and others) describe a recurring pattern at the DA2/XFLASH layer: a transfer completes, but the status or acknowledgment read that should follow it comes back short or times out. What I found here is the same shape of failure, one layer earlier, in the preloader's own basic register read/write protocol, before any DA is even selected. I think it's worth recording as a distinct, confirmed instance of that general symptom, not a new theory about its cause.

## Not established

- Why the acknowledgment read fails. I have observed it, not diagnosed it.
- Whether this is specific to this preloader build (`20231103_072325`), this chip revision, or general to MT8167-family devices against current mtkclient.
- Whether the watchdog-disable write had any effect before failing to acknowledge.
- Everything past this one command. `gettargetconfig` was the only command run.

## Handling

No DA, certificate, or device-specific key material was used or produced. The hex bytes and register values recorded above came from mtkclient's own live session output, not from its source code. Raw debug logs, UART logs, and watcher output are not included here, for the same reasons as the earlier capture note.
