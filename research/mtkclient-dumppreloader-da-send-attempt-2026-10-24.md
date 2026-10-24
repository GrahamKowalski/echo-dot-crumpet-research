# mtkclient dumppreloader attempt, 2026-10-24

Following the `--skipwdt` follow up in [mtkclient-gettargetconfig-attempt-2026-10-24.md](mtkclient-gettargetconfig-attempt-2026-10-24.md), I tried mtkclient's `dumppreloader` command against the same unit, over the same Raspberry Pi 3 forced full speed connection. This note corrects something from that earlier file: I had assumed `dumppreloader` stays at the register read level, the way `gettargetconfig` does. It does not. It attempts a real DA send as part of reading back the preloader's own code. I'm recording that plainly, along with what came of it.

Before the results, some context on why this step happened at all. This was one more incremental step on hardware set aside for this kind of testing, following directly from this repo's own [root strategy decision](../docs/crumpet-root-strategy-decision-2026-10-11.md), which asks for new, discriminating, real device evidence before continuing DA level work, rather than more speculative static analysis on its own. The clean, repeatable `--skipwdt` result already recorded is what I'd call that kind of evidence. Every attempt here was logged on both ends, the board's own UART and mtkclient's live session output, and I checked for a full recovery after each session before doing anything further.

## Setup

Same mtkclient install, same pinned commit `cd25cf9`, same Raspberry Pi 3 with `dwc_otg.speed=1` forcing full speed, as described in the earlier notes. Ran as `mtk.py dumppreloader --skipwdt --debugmode --filename <path>`, across three power cycles that caught the device.

## What happened (observed)

1. The handshake, identification, and target config read completed identically to the `--skipwdt` result already recorded: HW code `0x8167`, subcode `0x8a00`, HW Ver `0xcb00`, SW Ver `1`, target config `0x0` with every flag false.
2. mtkclient then attempted to send a DA. The device replied with an explicit two byte status code, `7004`, which mtkclient decodes as `DA_INVALID_LENGTH`. This happened on two of the three boots that caught a device.
3. No dump file was ever created on any attempt. Zero bytes were read from or written to the device's flash. I checked this directly, the output file mtkclient would have written simply does not exist.
4. After the DA send was rejected, mtkclient returned to waiting for a device, and the board's own boot stalled the same way recorded in the earlier `--skipwdt` note: no LED ring, no further UART progress past repeated `USB_HANDSHAKE`/`usb receive timeout` lines, on the boots where this happened.

## One boot that did not show the stall

Of three boots, one completed a fully normal boot to kernel console, with the LED ring, `BOOT_TIME: 3867`. I do not think this means `dumppreloader` avoided the problem. That boot shows zero DA related log lines and zero stuck loop lines on either side, which best matches a boot that mtkclient's polling loop simply did not catch in time, the same pattern this project's earlier full speed captures showed before mtkclient was used at all. I'm recording it as an observation, not a success.

## Recovery (observed, confirmed with UART captures)

Disconnecting USB and power cycling after a session like this produces a normal boot, the same baseline as every earlier recovery check in this project: `BOOT_TIME: 1344`, `sec params sbc_enabled = 1`, `Detect production device: True`, LED ring, LK finished, kernel console enabled, zero `USB_HANDSHAKE` or timeout lines. I confirmed this directly from a UART capture of the recovery boot itself, taken right after this specific session.

## How this fits what's already documented here

This repo's existing docs on DA1/DA2 handoff and DA2 Stage 2 failure are built on static disassembly and host side source review, explicitly without a real device trace. This is, as far as I can tell, the first entry in this project with an actual live DA send attempt against real hardware, and an actual device reported status code in response, rather than silence, a timeout, or a hypothesis. `DA_INVALID_LENGTH` is a specific, named status, not an unexplained short read. I think that is worth recording precisely, without claiming it explains or resolves this project's broader DA2 questions, which remain open.

## Not established

- Which DA mtkclient selected or attempted to send, or why its length was rejected.
- Whether a differently selected or sized DA would behave differently. I did not try one.
- Whether `DA_INVALID_LENGTH` here is the same underlying cause as this project's existing DA2/XFLASH short read hypotheses, or a separate issue.
- Anything about flash contents. No flash read or write of any kind occurred, and nothing was ever successfully dumped.

## Handling

No DA, certificate, or device-specific key material was used or produced, and none was selected successfully enough to be meaningful even if it had been. The status code and hex values above came from mtkclient's own live session output. Raw debug logs and UART logs are not included here, for the same reasons as the earlier capture notes.
