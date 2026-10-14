# Crumpet C78MP8: community NAND evidence and Amonet source delta (2026-10-14)

**Cutoff:** 2026-10-14 (public GitHub state). **Scope:** strictly read-only public-source review, based on previously captured statements and upstream Git history. No Echo Dot, flash chip, USB device, payload, or firmware was accessed or modified; no live Crumpet tests were performed. **No proven persistent root/unlock, working Crumpet DA2 or validated physical NAND restore.**

## Evidence levels

- **Directly checked:** public GitHub issue text, exact upstream commit metadata/diffs, a byte-for-byte comparison of the upstream `include/devices/crumpet.h` at `2a28fd0` and `da2070f`, and the upstream `build.sh` branch for `mt8173`.
- **Third-party reported, not independently reproduced:** chip acquisitions, raw file availability, data decoding, USB/device outcomes and the maintainer's progress statements.
- **Still unproven:** complete private raw captures with verifiable hashes/provenance; actual recorded layout, per-page ECC/BBT integrity, raw-image reproducibility, hardware writeback and cold boot; DA2 `SYNC` on C78MP8, persistent root, unlock or functional TWRP.

## 1. New primary-source NAND statement (2026-10-13)

Joost van de Wiel answered the existing [no-alexa issue #5](https://github.com/jvandewiel/no-alexa/issues/5#issuecomment-6141779362):

| Item | What the author reported | What we can actually conclude |
|---|---|---|
| Original captures | Raw pages remain available, approximately **132,000 files of ~4.4 KB** each | Original files are **reported to exist**, but are not available to us for independent inspection. Approximate counts/sizes cannot certify full-chip coverage. |
| Repeat reads | **2–3 reads of each page**, binary comparison **before writing to disk** | Reported within-acquisition repeat checking, **not** proof that two independent full raw datasets were preserved and cross-hashed. |
| Decoding | A **decoded image** exists; he reports that `gilderchuck` previously converted raw data into a readable/mountable image | First-hand report of an existing decoded image, second-hand attribution of mountability. Neither is an independent end-to-end reproduction or a physical restore. |
| Physical restore | He **never attempted writeback**, reballing the NAND, or a same-device cold-boot restoration test | **Restore remains unvalidated.** |
| Public verification materials | No public full-raw capture, whole-capture SHA-256, per-page validation report or complete independent decoder reproduction is provided in this reply | No new evidence to clear the recoverability gate. |

**Numerical discrepancy must remain open.** The reply says `4532 (4096 + 256)` bytes per page, yet **4096 + 256 = 4352**. Its separate description of **4 × 1088** bytes also yields **4352**. The older [raw NAND capture audit](crumpet-raw-nand-capture-integrity-gate-2026-10-11.md) independently checks the upstream decoder's **4 × (1024 data + 8 metadata + 56 BCH ECC) = 4352**-byte input expectation. That decoder expectation and the historical Macronix NAND geometry **do not prove the physical organization or exact size of these retained files**. The apparent swapped digits may be a typo, but this remains an inference pending non-sensitive actual file sizes and provenance. The approximate `~132000` count also should not be silently equated to the historical chip's **131072** nominal pages.

**Key separation:** `raw pre-decoding pages` → `decoded image` → `mountable filesystem` → `lossless restorable physical image` → `successfully written and cold-booted device` are **different claims**. Evidence at one stage does not imply later stages. The public decoding utilities discard or transform spare/ECC information; their output is not automatically a full, restorable physical capture.

**Low-risk follow-up:** examine only **already-existing**, appropriately authorized non-sensitive metadata: exact original page-file lengths, acquisition order, chip ID/board provenance, independently stored run-level hashes if available, ECC/bad-block/error counts, and a reproducible sanitized decoder test fixture. Keep whole-chip captures, account material, device IDs and keys private. Do **not** request fresh desoldering, shorting, DA uploads, NAND writes, erase tests or a restore trial.

## 2. Amonet-koboreru `2a28fd0...da2070f` (2026-10-11 to 2026-10-13)

[Direct compare](https://github.com/R0rt1z2/amonet-koboreru/compare/2a28fd0...da2070f): **8 commits** after the September 25 base; head **`da2070fb412ce9c7d35afaaa0617ba396e3d6eb1`** as checked on October 14. Selected source-level consequences:

| Commit (date, UTC) | Verified change | Relevance to Crumpet |
|---|---|---|
| [`4cc3192`](https://github.com/R0rt1z2/amonet-koboreru/commit/4cc3192db2acc7914d0bedc0437bc6c71c94d136) (Oct 13) | `PRELOADER_BASE` defined for `mt8163`, `mt8173` and `mt8516` (`mt8516 = 0x00201000`). | General platform metadata only; not a validated Crumpet RAM mapping or patch target. |
| [`db82cd5`](https://github.com/R0rt1z2/amonet-koboreru/commit/db82cd5e097a1dc8eeffd2bc6b89d1e9653a1f92) (Oct 13) | Payload-generation option to splice preloader `.text`, with `build.sh` passing `--preloader` **only for `PLATFORM=mt8173`**. | Crumpet's header still selects `mt8516`; therefore **not evidence of a Crumpet fix**. |
| [`c72c379`](https://github.com/R0rt1z2/amonet-koboreru/commit/c72c3798f4f479077928e2de57903ee6c310bc38) (Oct 13) | Platform headers include `device.h` to permit device-specific TEE/LK load address overrides. | Generic configurability; no demonstrated change to the Crumpet addresses or boot success. |
| [`e98cf37`](https://github.com/R0rt1z2/amonet-koboreru/commit/e98cf37a7d67d7185191e3480d9bbab80f554ca2) (Oct 13) | UART base override support in common UART source and `mt8173` platform header. | Not a Crumpet-specific runtime result. |
| [`710a4d1`](https://github.com/R0rt1z2/amonet-koboreru/commit/710a4d18579496cc9f1e1a96d14c23b2870aec10) (Oct 13) | Displays platform alongside device name. | Build output only. |
| [`da2070f`](https://github.com/R0rt1z2/amonet-koboreru/commit/da2070fb412ce9c7d35afaaa0617ba396e3d6eb1) (Oct 13) | Escapes `#` in Makefile for macOS. | Build compatibility only. |
| [`7f50614`](https://github.com/R0rt1z2/amonet-koboreru/commit/7f506140632a4fc722412995cf09c7f9ca0b503f), [`1e55aee`](https://github.com/R0rt1z2/amonet-koboreru/commit/1e55aeefa4c670b84dc23835aeabe194475f8745) (Oct 11) | Added LLM-contribution guidance and enforcement automation. | Project governance, **not** device functionality. |

**Crumpet-specific diff result:** `include/devices/crumpet.h` is **byte-identical** at `2a28fd0` and `da2070f`. Its `PLATFORM mt8516`, `LK_PART_NAME "expdb"`, and hardcoded patch addresses remain unchanged. The upstream `build.sh` still checks for `tees/tee_crumpet.img` before building; no donor image or working Crumpet package was demonstrated in this review. Therefore the [original fixed-address audit](amonet-hardcoded-patch-address-audit.md) and [unreached-LK/`expdb` audit](amonet-crumpet-unreachable-lk-and-expdb.md), pinned to `2a28fd0`, are **not invalidated** by these general changes; they must not be represented as live tests of the new head.

**Repository state on Oct 14:** only `main`, **no published releases**, and no new pull request; [PR #3](https://github.com/R0rt1z2/amonet-koboreru/pull/3) remains closed. The maintainer said [in issue #2](https://github.com/R0rt1z2/amonet-koboreru/issues/2#issuecomment-6108392942) on Oct 11 that he is **actively working** on device support, correcting the older historical description that support was simply on hold. This is an **announcement**, not released, boot-tested or independently validated C78MP8 support. The maintainer explicitly prohibited AI-generated upstream contributions and locked the issue; we do **not** post to that project.

## 3. Outstanding issue replies and evidence gates

- [gilderchuck/mtk-nand-utils issue #1](https://github.com/gilderchuck/mtk-nand-utils/issues/1): no substantive response verified by the October 14 check; the raw-to-mountable conversion mentioned in the Joost reply has no separately documented Crumpet-specific validation here.
- [R0rt1z2/amonet-koboreru issue #2](https://github.com/R0rt1z2/amonet-koboreru/issues/2): no newer DA2 status evidence after [alessionot97's recovered partial Kamakiri notes](https://github.com/R0rt1z2/amonet-koboreru/issues/2#issuecomment-6108930335). [Schebli](https://github.com/R0rt1z2/amonet-koboreru/issues/2#issuecomment-6108303288) said he would inspect old logs on return, with no verified follow-up yet. The Kamakiri `Check GPT`/512-byte-read error remains **distinct from MTKClient XFLASH DA2 `SYNC`** (see [protocol separation](crumpet-kamakiri-gpt-read-vs-mtkclient-da2-2026-10-12.md)).
- [jvandewiel/no-alexa issue #5](https://github.com/jvandewiel/no-alexa/issues/5): the October 13 reply above is the latest verified substantive reply as of this check.

| Required milestone | Status on Oct 14 |
|---|---|
| Author-reported retained original NAND data | **Reported**, not supplied/independently verified |
| Reproducibly decoded / mounted Crumpet image | **Reported**, no independent fixture or verification supplied in these threads |
| Two independent whole-chip raw captures and verified ECC/OOB/BBT | **Not demonstrated** |
| Physical NAND writeback **and cold boot** on the same unit | **Not demonstrated** |
| C78MP8 XFLASH DA2 framed `SYNC` | **Not demonstrated** |
| Functional persistent root, unlock, recovery/TWRP | **Not demonstrated** |

**Decision:** retain the established no-go gate for risky device experiments. Track exact, published Crumpet-specific upstream changes and new **already-existing** sanitized evidence. New generic build tooling or a maintainer intention should not trigger claims of a successful exploit or recovery.
