import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import config_lib  # noqa: E402
import scan_text  # noqa: E402
import scan_ui  # noqa: E402


class ConfigTests(unittest.TestCase):
    def test_string_booleans_and_bad_version_are_normalized(self):
        data = config_lib._normalize(
            {
                "version": "bad",
                "always_on": "false",
                "scan_before_ship": "off",
                "surfaces": {"text": True},
            },
            "test",
        )
        self.assertEqual(data["version"], config_lib.CONFIG_VERSION)
        self.assertFalse(data["always_on"])
        self.assertFalse(data["scan_before_ship"])
        self.assertEqual(data["surfaces"], config_lib.DEFAULT_SURFACES)

    def test_save_clamps_threshold_and_rejects_empty_surfaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = os.environ.get("XDG_CONFIG_HOME")
            os.environ["XDG_CONFIG_HOME"] = tmp
            try:
                path, payload = config_lib.save_config(True, ["text"], threshold=999)
                self.assertEqual(payload["threshold"], 100)
                self.assertEqual(json.loads(path.read_text())["threshold"], 100)
                with self.assertRaises(ValueError):
                    config_lib.save_config(True, ["invalid"])
            finally:
                if old is None:
                    os.environ.pop("XDG_CONFIG_HOME", None)
                else:
                    os.environ["XDG_CONFIG_HOME"] = old

    def test_project_save_never_overwrites_discovered_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            child = parent / "packages" / "site"
            child.mkdir(parents=True)
            parent_config = parent / ".unmachined.json"
            parent_config.write_text('{"always_on": false}\n')

            path, _ = config_lib.save_config(True, scope="project", cwd=child)

            self.assertEqual(path, child.resolve() / ".unmachined.json")
            self.assertEqual(parent_config.read_text(), '{"always_on": false}\n')


class ScannerTests(unittest.TestCase):
    def test_code_is_masked_but_blockquoted_copy_is_scanned(self):
        self.assertEqual(scan_text.scan("`cutting-edge`"), [])
        findings = scan_text.scan("> Our cutting-edge platform")
        self.assertTrue(any(item["detail"] == "cutting-edge" for item in findings))

    def test_missing_text_file_is_a_usage_error_without_traceback(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scan_text.py"), "missing-file.md"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read missing-file.md", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_scanner_thresholds_must_match_score_range(self):
        for script, target in (("scan_text.py", "-"), ("scan_ui.py", str(ROOT))):
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / script), target, "--threshold", "101"],
                input="clean text" if target == "-" else None,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("between 1 and 100", result.stderr)

    def test_multiple_files_include_source_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.md"
            second = Path(tmp) / "second.md"
            first.write_text("Plain copy.\n", encoding="utf-8")
            second.write_text("Intro.\nOur cutting-edge tool.\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "scan_text.py"),
                    str(first),
                    str(second),
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            finding = next(item for item in payload["findings"] if item["detail"] == "cutting-edge")
            self.assertEqual(finding["file"], str(second))
            self.assertEqual(finding["line"], 2)
            self.assertEqual(finding["excerpt"], "Our cutting-edge tool.")

    def test_fenced_code_masking_preserves_later_line_numbers(self):
        text = "Before.\n```text\ncutting-edge\n```\nAfter seamless copy.\n"
        finding = next(item for item in scan_text.scan(text) if item["detail"] == "seamless")
        self.assertEqual(finding["line"], 5)

    def test_stdin_cannot_be_mixed_with_files(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "scan_text.py"), "-", str(ROOT / "README.md")],
            input="copy",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot be combined", result.stderr)


class UiScannerTests(unittest.TestCase):
    def make_project(self, version, source):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "src").mkdir()
        (root / "package.json").write_text(
            json.dumps({"devDependencies": {"tailwindcss": version}}),
            encoding="utf-8",
        )
        target = root / "src" / "app.tsx"
        target.write_text(source, encoding="utf-8")
        return temp, target

    def test_tailwind_v3_directive_is_valid_in_v3_project(self):
        temp, target = self.make_project("^3.4.17", "@tailwind base;\n")
        with temp:
            self.assertEqual(scan_ui.detect_tailwind_version(target), 3)
            findings = scan_ui.scan_file(target, tailwind_version=3)
            self.assertFalse(any(item["rule"] == "tailwind v3 directive" for item in findings))

    def test_tailwind_v3_directive_is_reported_in_v4_project(self):
        temp, target = self.make_project("^4.1.0", "@tailwind base;\n")
        with temp:
            self.assertEqual(scan_ui.detect_tailwind_version(target), 4)
            findings = scan_ui.scan_file(target, tailwind_version=4)
            self.assertTrue(any(item["rule"] == "tailwind v3 directive" for item in findings))

    def test_tailwind_detection_falls_back_to_workspace_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / "apps" / "web"
            source = app / "src" / "app.tsx"
            source.parent.mkdir(parents=True)
            (root / "package.json").write_text(
                json.dumps({"devDependencies": {"tailwindcss": "~4.1.0"}}),
                encoding="utf-8",
            )
            (app / "package.json").write_text(
                json.dumps({"dependencies": {"react": "19.1.0"}}),
                encoding="utf-8",
            )
            source.write_text("export default null;\n", encoding="utf-8")
            self.assertEqual(scan_ui.detect_tailwind_version(source), 4)

    def test_explicit_tailwind_override_works_without_package_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "styles.css"
            target.write_text("@tailwind utilities;\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "scan_ui.py"),
                    str(target),
                    "--tailwind-version",
                    "4",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["tailwind_versions"][str(target)], 4)
            self.assertTrue(any(item["rule"] == "tailwind v3 directive" for item in payload["findings"]))

    def test_multiline_centered_hero_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hero.tsx"
            target.write_text(
                '<section className="min-h-screen\n  flex items-center\n  justify-center">\n',
                encoding="utf-8",
            )
            findings = scan_ui.scan_file(target)
            self.assertTrue(any(item["rule"] == "centered 100vh hero" for item in findings))

    def test_dynamic_same_line_centered_hero_remains_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "hero.tsx"
            target.write_text(
                'const classes = cn("min-h-screen", active && "items-center");\n',
                encoding="utf-8",
            )
            findings = scan_ui.scan_file(target)
            self.assertTrue(any(item["rule"] == "centered 100vh hero" for item in findings))

    def test_multiline_icon_circle_is_detected_in_any_class_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tile.tsx"
            target.write_text(
                '<span className="p-2\n  rounded-full\n  bg-blue-100">Icon</span>\n',
                encoding="utf-8",
            )
            findings = scan_ui.scan_file(target)
            self.assertTrue(any(item["rule"] == "icon-in-colored-circle tile" for item in findings))

    def test_dynamic_same_line_icon_circle_remains_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tile.tsx"
            target.write_text(
                'const classes = cn("rounded-full", "bg-blue-100", "p-2");\n',
                encoding="utf-8",
            )
            findings = scan_ui.scan_file(target)
            self.assertTrue(any(item["rule"] == "icon-in-colored-circle tile" for item in findings))


class CatalogSyncTests(unittest.TestCase):
    """scan_text.py is the deterministic core; references/text-tells.md is the
    full catalog. Direction of truth: every phrase the scanner enforces must be
    documented in the catalog (scanner is a subset; the catalog may be broader
    for LLM judgment). Downstream consumers import the scanner directly, so an
    undocumented scanner rule would be a live production rule nobody can read
    about. If this test fails, document the new phrase in text-tells.md; do
    not delete it from the scanner (external repos pin
    CRITICAL_PHRASES/MAJOR_PHRASES)."""

    PHRASE_LISTS = (
        "CRITICAL_PHRASES",
        "MAJOR_PHRASES",
        "MINOR_WORDS",
        "ECHO_OPENERS",
        "BANNED_OPENERS",
    )

    @classmethod
    def setUpClass(cls):
        raw = (ROOT / "references" / "text-tells.md").read_text(encoding="utf-8")
        cls.doc = cls.normalize(raw)

    @staticmethod
    def normalize(text):
        # curly apostrophes, hyphen/space variants, and line wraps in the
        # catalog must not hide a match
        text = text.lower().replace("’", "'")
        text = re.sub(r"[-‑]+", " ", text)
        return re.sub(r"\s+", " ", text)

    def test_every_scanner_phrase_is_documented_in_text_tells(self):
        for list_name in self.PHRASE_LISTS:
            phrases = getattr(scan_text, list_name)
            missing = [p for p in phrases if self.normalize(p) not in self.doc]
            self.assertFalse(
                missing,
                "scan_text.{0} entries missing from references/text-tells.md: "
                "{1}. Document them in the catalog; the scanner and the "
                "catalog must not drift.".format(list_name, missing),
            )

    def test_rhythm_buckets_match_the_documented_thresholds(self):
        # text-tells.md documents the S/M/L rhythm buckets the scanner uses.
        raw = (ROOT / "references" / "text-tells.md").read_text(encoding="utf-8")
        self.assertIn("S (<=8 words), M (<=20), L (>20)", raw)


class OnboardCliTests(unittest.TestCase):
    def run_onboard(self, *args):
        env = dict(os.environ)
        with tempfile.TemporaryDirectory() as tmp:
            env["XDG_CONFIG_HOME"] = tmp
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "onboard.py"), *args],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

    def test_surfaces_option_matches_documented_command(self):
        result = self.run_onboard("--always-on", "--surfaces", "text,ui")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_surface_is_usage_error(self):
        result = self.run_onboard("--always-on", "--surfaces", "audio")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
