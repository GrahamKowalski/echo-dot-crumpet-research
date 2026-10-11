# Request for existing Crumpet hardware evidence (C78MP8) — 2026-10-11

This is an **evidence request**, not instructions to run an exploit. Researchers: please **do not perform new unsafe DA uploads, memory writes, shorting, flash/TEE operations or desoldering on your only working unit** for this project.

## A. For people who previously reached BROM/Kamakiri but failed at DA2

If you still have logs **from existing sessions**, the most useful contribution is a **redacted chronology from a single capture/session**:

1. Exact confirmed model `C78MP8 / crumpet`, firmware/preloader build string (if known), board revision (if known); do **not** provide serial numbers.
2. Host OS, MTKClient version and ideally exact source revision; selected DA **filename and SHA-256** (not binary); original/patched status, without distributing patched binaries.
3. BootROM USB `0e8d:0003` versus Preloader USB `0e8d:2000`, **recorded phase and relative timestamps**, plus whether any disconnect or re-enumeration occurred around DA1 acknowledgement and DA2 startup.
4. Previously recorded DA1 sync and setup outcomes, whether a proper 400-byte Crumpet EMI was used, **first transfer ACK**, and exact subsequent 12-byte XFLASH status read outcome (bytes, short read, timeout or endpoint error). A previous packet capture (`pcapng`/usbmon) or a redacted host stack trace is ideal.
5. Only for a genuinely recorded success: proof of DA2 framed `SYNC`, NAND ID/reads and how the result was obtained; do not assume a generic "Upload data was accepted" line proves DA2 started.

Please check your proposed logs for sensitive material (serials, DSN, unique IDs, per-device keys, private partitions and complete command payloads) **before publication**. A simple sanitized text summary with selected offsets/status and timestamps may suffice. Avoid running a new exploit simply to answer this.

## B. For people who previously physically read Crumpet raw NAND

We would like to know whether **original pre-decoding captures** remain available (not merely main-data-only decoded output), without requesting public posting of secrets:

1. The actual NAND chip **part number and ID** and recorded board revision, separate from the assumed historical `MX30LF4G28AD`.
2. Capture hardware/software and provenance; exact saved raw file sizes; whether captures include **spare/OOB**, whether bytes are arranged `4096+256` or four `1024+8+56` subrecords.
3. Whether **two independently acquired full raw captures** from the **same chip** were saved; do their full SHA-256 values and page comparisons agree? Please do not imply that copied files count as independent captures.
4. Which PRBS, ECC, ECC-failure, bad-block-table and boot-copy checks have actually been validated and with what tested configuration; report **counts/metadata**, not the private raw content.
5. Whether anyone has **successfully restored the same hardware and cold-booted it**, on a spare device, after a controlled test. A working reader/decoder alone does not demonstrate writeback or secure boot.

The historical 4Gb `MX30LF4G28AD` raw main+OOB file has `131072 × 4352 = 570425344` bytes, **but the length alone proves no completeness, authenticity or restore viability**. A full raw capture may contain private account-related data and secrets; no full binary or serial-bearing logs should be attached publicly without owner approval and proper privacy review.

## Starting references

- Early actual Crumpet physical reader: https://github.com/jvandewiel/no-alexa/wiki/Dumping-NAND-flash
- Historic UART and board testpad documents: https://github.com/jvandewiel/no-alexa/wiki/UART-logs and https://github.com/jvandewiel/no-alexa/wiki/Interfacing
- MT8167 NAND PRBS/BCH decoder: https://github.com/gilderchuck/mtk-nand-utils
- Owner BROM/Kamakiri reports (same-model but differing hardware access): https://github.com/R0rt1z2/amonet-koboreru/issues/2
- Our existing read-only raw capture verifier: [compare_crumpet_raw_nand_captures.py](../scripts/compare_crumpet_raw_nand_captures.py)
- Research decision gates: [crumpet-root-strategy-decision-2026-10-11.md](../docs/crumpet-root-strategy-decision-2026-10-11.md)

**Current facts:** the public `no-alexa/dumped_files/` folder contains `brhgptpl_0.bin` (196608 bytes), **not a publicly hosted full 570425344-byte NAND+OOB backup**. A separate 131072-byte BROM file is **not** NAND. Previously reported Crumpet preloader reads are not full NAND access. No validated DA2, restore, or root is claimed.

## Outgoing requests sent 2026-10-11

All three were **published from the `Manantra` GitHub account**, with the device kept unopened and no new tests requested:

- [jvandewiel/no-alexa issue #5](https://github.com/jvandewiel/no-alexa/issues/5) — asked whether existing original full-chip Crumpet predecode NAND+OOB captures, geometry, independent reads and real restore evidence are still retained (no public private dumps).
- [gilderchuck/mtk-nand-utils issue #1](https://github.com/gilderchuck/mtk-nand-utils/issues/1) — asked whether the originally tested MT8516B board was actually Crumpet, the source byte layout/BCH parameters, safe sample metadata and whether any restoration was validated.
- [R0rt1z2/amonet-koboreru issue #2 comment](https://github.com/R0rt1z2/amonet-koboreru/issues/2#issuecomment-6108190362) — tagged `@schebli` and `@alessionot97` requesting **already-recorded** selected DA/EMI information, distinct DA1 ACK / DA2 status, USB connection timing and redacted logs.

**Status:** Requests posted successfully; **no replies verified yet**. Receiving answers, hardware data or a genuine Root/Unlock is not implied. Review those threads before treating any claim as a new experiment result.
