"""Synthetic log fixtures for the offline MTKClient DA phase classifier."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from classify_mtkclient_stage2 import classify

STAGE2_TIMEOUT = """
Port - Device detected :)
Preloader - HW code: 0x8167
DAXFlash - Uploading xflash stage 1 from MTK_DA_V5.bin
DAXFlash - Successfully uploaded stage 1, jumping ..
DAXFlash - Successfully received DA sync
DAXFlash - Sending emi data ...
DAXFlash - DRAM setup passed.
DAXFlash - Sending emi data succeeded.
DAXFlash - Uploading stage 2...
DAXFlash - Upload data was accepted. Jumping to stage 2...
DAXFlash - Stage was't executed. Maybe dram issue ?.
MTK - Failed to upload da.
"""


class DiagnosticTests(unittest.TestCase):
    def test_timeout_does_not_claim_dram_fault(self):
        flags, result, needs = classify(STAGE2_TIMEOUT)
        self.assertTrue(flags["hardware_8167"])
        self.assertTrue(flags["stage1_sync"])
        self.assertTrue(flags["emi_command_accepted"])
        self.assertTrue(flags["stage2_payload_accepted"])
        self.assertTrue(flags["stage2_status_exception"])
        self.assertFalse(flags["stage2_boot_success"])
        self.assertIn("unknown", result)
        self.assertIn("NOT a confirmed DRAM", result)
        self.assertGreater(len(needs), 0)

    def test_stage_two_ack_without_execution_proof(self):
        log = STAGE2_TIMEOUT.split("DAXFlash - Stage was't executed")[0]
        flags, result, _ = classify(log)
        self.assertTrue(flags["stage2_payload_accepted"])
        self.assertFalse(flags["stage2_status_exception"])
        self.assertIn("execution unverified", result)

    def test_explicit_success_never_proves_root(self):
        log = STAGE2_TIMEOUT.split("DAXFlash - Stage was't executed")[0]
        log += "DAXFlash - Boot to succeeded.\nDAXFlash - Successfully uploaded stage 2"
        flags, result, _ = classify(log)
        self.assertTrue(flags["stage2_boot_success"])
        self.assertIn("not evidence of unlock/root", result)

    def test_no_logs_no_status(self):
        flags, result, missing = classify("Device detected :)")
        self.assertFalse(flags["brom_explicit"])
        self.assertFalse(flags["stage2_boot_success"])
        self.assertIn("Insufficient", result)
        self.assertGreater(len(missing), 2)

    def test_security_failure_not_generic_timeout(self):
        flags, result, _ = classify("DA_IMAGE_SIG_VERIFY_FAIL (0x2001)")
        self.assertTrue(flags["signature_rejected"])
        self.assertFalse(flags["stage2_status_exception"])
        self.assertIn("signature rejection", result)

    def test_nand_info_only_if_explicitly_logged(self):
        flags, _, _ = classify(STAGE2_TIMEOUT)
        self.assertFalse(flags["daemon_nand_info"])
        flags, _, _ = classify(STAGE2_TIMEOUT + "\nNAND Pagesize: 0x1000")
        self.assertTrue(flags["daemon_nand_info"])


    def test_legacy_kamakiri_gpt_error_is_not_da2_status(self):
        raw = ("[2026-10-11 12:00] All good\n"
               "[2026-10-11 12:01] Check GPT\n"
               "RuntimeError: read fail (got 0 of 512 bytes)\n")
        flags, status, needs = classify(raw)
        self.assertTrue(flags["legacy_kamakiri_gpt_probe"])
        self.assertTrue(flags["legacy_kamakiri_read_failure"])
        self.assertFalse(flags["stage2_status_exception"])
        self.assertIn("NOT an MTKClient XFLASH DA2", status)
        self.assertTrue(any("exact Kamakiri" in n for n in needs))

    def test_legacy_marker_with_generic_read_fail(self):
        flags, status, _ = classify("All good\nCheck GPT\nRuntimeError: read fail\n")
        self.assertTrue(flags["legacy_kamakiri_read_failure"])
        self.assertIn("GPT-phase", status)

    def test_no_gpt_no_legacy_attribution(self):
        flags, status, _ = classify("Kamakiri: All good\nRuntimeError: read fail\n")
        self.assertFalse(flags["legacy_kamakiri_gpt_probe"])
        self.assertIn("Insufficient", status)

    def test_explicit_xflash_exception_takes_priority_when_mixed(self):
        raw = STAGE2_TIMEOUT + "\nAll good\nCheck GPT\nRuntimeError: read fail\n"
        flags, status, needs = classify(raw)
        self.assertTrue(flags["legacy_kamakiri_gpt_probe"])
        self.assertTrue(flags["stage2_status_exception"])
        self.assertIn("No Stage-2 status response", status)
        self.assertTrue(any("USB state" in n for n in needs))

    def test_legacy_marker_without_failure_is_not_success(self):
        flags, status, _ = classify("All good\nCheck GPT\n")
        self.assertTrue(flags["legacy_kamakiri_gpt_probe"])
        self.assertFalse(flags["stage2_boot_success"])
        self.assertIn("not an MTKClient", status)


if __name__ == "__main__":
    unittest.main()
