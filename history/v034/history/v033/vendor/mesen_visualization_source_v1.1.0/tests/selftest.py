#!/usr/bin/env python3
import importlib.util
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mesen_visual", ROOT / "scripts" / "mesen_visual.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("MESEN_TEMP_DIR"))
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_png_is_decoded(self):
        path = self.root / "valid.png"
        Image.new("RGB", (224, 144), "blue").save(path)
        self.assertEqual(module.png_geometry(path), (224, 144))

    def test_truncated_png_is_rejected(self):
        path = self.root / "truncated.png"
        path.write_bytes(module.PNG_SIGNATURE + b"\0" * 16)
        with self.assertRaises(module.MesenError):
            module.png_geometry(path)

    def test_capture_rejects_truncated_png_and_creates_profile(self):
        mesen = self.root / "Mesen"
        mesen.write_bytes(b"\x7fELF\x02placeholder")
        mesen.chmod(0o755)
        rom = self.root / "test.wsc"
        rom.write_bytes(b"ROM")
        lua = self.root / "test.lua"
        lua.write_text("-- test")
        output = self.root / "capture.png"
        args = module.build_parser().parse_args([
            "capture", "--mesen", str(mesen), "--rom", str(rom),
            "--lua", str(lua), "--output", str(output),
        ])
        def fake_run(*unused):
            output.write_bytes(module.PNG_SIGNATURE + b"\0" * 16)
            return subprocess.CompletedProcess([], 0, "", ""), False
        with patch.object(module, "run_process", side_effect=fake_run):
            with contextlib.redirect_stdout(io.StringIO()):
                result = module.capture(args)
        self.assertEqual(result, 2)
        self.assertEqual((self.root / "settings.json").read_text(), "{}\n")
        self.assertFalse(__import__("json").loads(output.with_suffix(".json").read_text())["passed"])

    def test_unknown_wonderswan_geometry_is_not_cropped(self):
        path = self.root / "unknown.png"
        Image.new("RGB", (300, 144), "blue").save(path)
        with self.assertRaises(module.MesenError):
            module.normalize_wonderswan(path)
        self.assertTrue(path.exists())

    def test_output_collision_cannot_delete_lua(self):
        mesen = self.root / "Mesen"
        mesen.write_bytes(b"\x7fELF\x02placeholder")
        mesen.chmod(0o755)
        (self.root / "settings.json").write_text("{}")
        rom = self.root / "test.wsc"
        rom.write_bytes(b"ROM")
        lua = self.root / "collision.lua.json"
        lua.write_text("-- preserve")
        args = module.build_parser().parse_args([
            "capture", "--mesen", str(mesen), "--rom", str(rom),
            "--lua", str(lua), "--output", str(self.root / "collision.png"),
            "--overwrite",
        ])
        with self.assertRaises(module.MesenError):
            module.capture(args)
        self.assertEqual(lua.read_text(), "-- preserve")

    def test_probe_rejects_non_elf(self):
        fake = self.root / "Mesen"
        fake.write_text("not an executable")
        fake.chmod(0o755)
        ok, detail = module.executable_format(fake)
        self.assertFalse(ok)
        self.assertIn("ELF", detail)

    def test_supervisor_timeout_returns_log_and_124(self):
        result, timed_out = module.run_process(
            [sys.executable, "-c", "import time; print('started', flush=True); time.sleep(30)"],
            self.root, os.environ.copy(), 1,
        )
        self.assertTrue(timed_out)
        self.assertEqual(result.returncode, 124)
        self.assertIn("started", result.stdout)

if __name__ == "__main__":
    unittest.main(verbosity=2)
