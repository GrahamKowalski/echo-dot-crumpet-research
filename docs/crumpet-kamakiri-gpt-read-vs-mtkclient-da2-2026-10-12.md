# A real evidence distinction: Kamakiri "Check GPT" is not MTKClient XFLASH DA2 status

**Date:** 2026-10-12. **Target:** Amazon Echo Dot 3 Refresh / C78MP8 / crumpet, MT8167/MT8516, raw NAND. **Method:** compare [alessionot97's partial recovered hardware notes (October 11)](https://github.com/R0rt1z2/amonet-koboreru/issues/2#issuecomment-6108930335) with independent original Kamakiri source, historical eMMC-platform logs, and the exact pinned [MTKClient cd25cf9 XFLASH host source](https://github.com/bkerler/mtkclient/blob/cd25cf9/mtkclient/Library/DA/xflash/xflash_lib.py). Nothing was uploaded to an Echo Dot, flashed, or tested electrically; the local owner device stays unopened. **This does not attribute a root cause or demonstrate DA2/root.**

## 1. Original report: distinguish two excerpts from two programs

The latest **partial recovered** C78MP8-owner record says:

- Host: Ubuntu/FireISO, MTKClient reported as V2.1.4 (exact revision unknown).
- USB BROM VID:PID `0e8d:0003` and `/dev/ttyACM0` seen; 150148-byte preloader dump, SHA-256 `d0d43eea2d5d52835007e375a3214fa4c6bf1a7c319e52ab442b7567e318992b`.
- Recovered *Kamakiri* fragment: `All good` → `Check GPT` → `RuntimeError: read fail (got 0 of 512 bytes)`.
- **Not recovered:** precise Kamakiri script/fork/revision or call stack, selected DA/patch identity, EMI mode and hash, distinct XFLASH DA1 ACK/DA2 status read, USB reconnection times.

The owner **explicitly says this is not an MTKClient DA2 status trace**. In contrast, an unrelated kind of Crumpet log discussed in [our earlier source audit](da1-sha1-status-vs-da2-sync-ack.md) shows `Upload data was accepted. Jumping to stage 2...` and `Stage was't executed. Maybe dram issue ?.`. Those are XFLASH messages from **MTKClient**, not from Kamakiri's separate boot payload.

## 2. Verified source chain in historical Kamakiri/Amonet (different device)

The public historical [`amonet-kamakiri/kamakiri` source](https://github.com/amonet-kamakiri/kamakiri), specifically [`modules/main.py`](https://github.com/amonet-kamakiri/kamakiri/blob/master/modules/main.py), contains exactly:

```python
log("Check GPT")
switch_user(dev)
gpt = parse_gpt(dev)
```

Its [`modules/functions.py`](https://github.com/amonet-kamakiri/kamakiri/blob/master/modules/functions.py) defines `switch_user(dev)` to call `dev.emmc_switch(0)`, then `dev.emmc_read(0)`, testing the usual `0x55AA` first-sector trailer. [`modules/common.py`](https://github.com/amonet-kamakiri/kamakiri/blob/master/modules/common.py) defines `emmc_read` as:

```python
self.dev.write(p32_be(0xf00dd00d))
self.dev.write(p32_be(0x1000))
self.dev.write(p32_be(idx))
data = self.dev.read(0x200)  # exactly 512 bytes
if len(data) != 0x200:
    raise RuntimeError("read fail")
```

[The Kamakiri `modules/load_payload.py`](https://github.com/amonet-kamakiri/kamakiri/blob/master/modules/load_payload.py) has **two distinct** `All good` messages after its own payload stage-1 and stage-2 4-byte ready responses; these names are NOT MTKClient XFLASH DA1/DA2. A string `All good` alone is not proof of NAND readback, XFLASH DA2 handshake, any secure-boot bypass, or full boot.

**Reasonable specific hypothesis:** If the 2026 Crumpet session used a fork/variant of this legacy Kamakiri flow, the shown zero-of-512 error could be the result of its `emmc_read(0)` probe in a **raw NAND** target lacking the expected eMMC interface. However the reporter's precise exception text includes `(got 0 of 512 bytes)`, while the linked older source emits simply `read fail`. We have *not* obtained its actual script revision, stack trace or device communications. Therefore we **cannot** claim source identity or that the device's NAND medium was conclusively the cause of the failed read.

An [older independent 2020 Amonet/Kamakiri example on an eMMC-style device](https://stackoverflow.com/questions/62181275/a-problem-with-compatibility-of-the-script-on-windows) shows *exactly* `Check GPT` → `switch_user` → `emmc_read(0)` → `RuntimeError: read fail`; the similar failure can occur **even on a device with eMMC**. This is useful counterevidence against treating `read fail` as a NAND-only fingerprint.

## 3. Different meaning of Stage 2 in the two codebases

| Observation | Historical Kamakiri/Amonet loader | MTKClient cd25cf9 XFLASH download agent |
|---|---|---|
| "All good" | 4-byte stage payload ready marker in the older script, possibly emitted twice | Not the expected MTKClient DA2 boot acknowledgment |
| "Check GPT" | eMMC partition switch then initial 512-byte sector read in older script | No evidence this belongs to XFLASH status |
| "read fail" | 512-byte `emmc_read` contract not met in older script | Not a verified XFLASH 12-byte status header failure |
| "Upload data was accepted..." | Not the older Kamakiri message above | Means earlier DA data transfer/DA1 status accepted; not DA2 execution |
| "Stage was't executed..." | Not the older Kamakiri message above | Host failed to obtain expected subsequent DA2 XFLASH status |
| "Stage 2" | Kamakiri's proprietary stage-2 payload | MTKClient's second Download Agent executable |

In original MTKClient [`send_data` and `boot_to`](https://github.com/bkerler/mtkclient/blob/cd25cf9/mtkclient/Library/DA/xflash/xflash_lib.py), upload acceptance checks the **first status**, then a separate `status()` must return the XFLASH boot `SYNC` value (`0x434E5953`) or zero; a thrown exception produces the reported generic stage failure. Those source-level facts are already known in [our DA1/DA2 report](da1-sha1-status-vs-da2-sync-ack.md).

## 4. Concrete advancement: offline log tool no longer conflates the paths

Rather than writing more speculative DA1 disassembly, the existing [`scripts/classify_mtkclient_stage2.py`](../scripts/classify_mtkclient_stage2.py) now marks:

- `legacy_kamakiri_gpt_probe`: standalone `Check GPT` line (including optional bracketed timestamp).
- `legacy_kamakiri_read_failure`: `read fail` and optional `(got N of 512 bytes)` suffix.

When the excerpt has a matching legacy GPT probe and read failure **without** explicit XFLASH markers, the outcome says it is **not an MTKClient XFLASH DA2 status result**, and asks for the *actual script and stack trace* instead of claiming DRAM/DA2/NAND failure. If a user concatenates logs and explicit XFLASH status appears, those explicit messages still take precedence.

**Five additional synthetic regression tests** cover the real message variant, old plain `read fail`, absence of `Check GPT`, mixed-stage priority, and `Check GPT` without failure. On `hermes`, the entire repository suite passed **255/255** tests, and a synthetic end-to-end CLI run produced the intended conservative distinction. No binary, NAND pages or real hardware were read.

## 5. Strict go/no-go research outcome

**Useful new conclusion:** The recovered 512-byte read failure does **not** fill the previously missing XFLASH DA2 trace. It describes a *different potential storage read stage*. Therefore **no new justification exists for resuming blind DA1 disassembly or testing an alternative DA on the unopened target**.

What could change this assessment:

1. The **exact original script/fork and traceback** corresponding to the `read fail (got 0 of 512 bytes)` message, recovered from a prior session.
2. One genuinely matching-session XFLASH USB log with separate DA1 ACK, selected DA and EMI, and actual DA2 `SYNC`/status read.
3. Independent old physical raw-NAND main+spare capture provenance and recovery data, from already-contacted researchers.

If none becomes available, the research gate remains closed; monitor original maintainer changes and existing research requests **read-only**. The upstream maintainer has explicitly requested **no further AI-generated comments/issues**, so **do not post to that project**.

**Bottom line:** A better phase distinction was achieved; **physical Crumpet DA2, recoverable NAND, custom boot and root remain unverified**.
