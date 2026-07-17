import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scan_text  # noqa: E402
import voice_profile  # noqa: E402


FIXTURE_SAMPLES = [
    {"text": "Shipped the control plane today. It's live. Three agents, one loop,"
             " zero babysitting. don't sleep on orchestration!", "source": "x-posts"},
    {"text": "Most teams over-engineer agents. Wrong frame. The loop wins when"
             " context is cheap and the handoff is boring.", "source": "x-posts"},
    {"text": "Built the whole pipeline in a weekend. It's not pretty. It works."
             " Numbers tomorrow!", "source": "x-posts"},
    {"text": "Orchestration beats model tribalism. Steal the pattern, keep the"
             " receipts, ship the loop again.\n\nFull guide below.", "source": "voice-few-shot"},
    {"text": "can you check why the deploy gate fails on the second run? it's"
             " the same config both times and the loop only breaks after"
             " compaction.", "source": "transcripts"},
]


class ComputeProfileTests(unittest.TestCase):
    def test_fixture_corpus_produces_expected_fingerprint_shape(self):
        profile = voice_profile.compute_profile(FIXTURE_SAMPLES)
        corpus = profile["corpus"]
        self.assertEqual(corpus["samples"], 5)
        self.assertEqual(corpus["per_source"],
                         {"transcripts": 1, "voice-few-shot": 1, "x-posts": 3})
        lengths = profile["sentence_length"]
        self.assertAlmostEqual(lengths["S"] + lengths["M"] + lengths["L"], 1.0, places=2)
        self.assertGreater(lengths["S"], 0.3)  # staccato fixture is S-heavy
        self.assertGreater(profile["contractions"]["per_100_words"], 0)
        self.assertGreater(profile["punctuation"]["exclamation_per_1000_words"], 0)
        self.assertGreater(profile["casing"]["lowercase_sentence_start_rate"], 0)
        self.assertTrue(profile["exemplars"])
        for exemplar in profile["exemplars"]:
            self.assertLessEqual(len(exemplar["text"]), voice_profile.EXEMPLAR_MAX_CHARS)
            self.assertIn(exemplar["source"],
                          ("x-posts", "voice-few-shot", "transcripts", "paths"))
        self.assertIn("loop", [d["word"] for d in profile["vocabulary"]["distinctive"]])

    def test_empty_corpus_is_refused(self):
        with self.assertRaises(ValueError):
            voice_profile.compute_profile([])


class IngesterFilterTests(unittest.TestCase):
    def test_strip_noise_removes_code_urls_paths_and_shell_lines(self):
        raw = (
            "the profile idea is solid, learn from my real posts\n"
            "```python\nprint('cutting-edge')\n```\n"
            "run `pnpm test` first\n"
            "$ git push origin main\n"
            "see https://example.com/docs and /Users/example/dev/notes.md\n"
            "then tell me what breaks"
        )
        clean = voice_profile.strip_noise(raw)
        for gone in ("print", "pnpm", "git push", "https://", "/Users/example"):
            self.assertNotIn(gone, clean)
        self.assertIn("the profile idea is solid", clean)
        self.assertIn("then tell me what breaks", clean)

    def test_transcript_ingester_keeps_only_typed_human_prose(self):
        records = [
            # typed prose with code fence and URL: kept, noise stripped
            {"type": "user", "promptSource": "typed",
             "message": {"role": "user", "content":
                         "please rework the intro so it sounds like me and not"
                         " a press release\n```sh\nls -la\n```\n"
                         "reference: https://example.com/post"}},
            # sdk-driven automation: rejected
            {"type": "user", "promptSource": "sdk",
             "message": {"role": "user", "content":
                         "Draft one public X reply for venture acme and"
                         " return only the reply text please."}},
            # sidechain (agent-authored subagent prompt): rejected
            {"type": "user", "promptSource": "typed", "isSidechain": True,
             "message": {"role": "user", "content":
                         "You are a subagent, search the repository for the"
                         " config loader and report back."}},
            # tool result: rejected
            {"type": "user",
             "message": {"role": "user", "content":
                         [{"type": "tool_result", "content": "ok"}]}},
            # harness command wrapper: rejected
            {"type": "user",
             "message": {"role": "user", "content":
                         "<command-name>/status</command-name>"}},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "-Users-example-dev"
            project.mkdir()
            with (project / "session.jsonl").open("w", encoding="utf-8") as fh:
                for rec in records:
                    fh.write(json.dumps(rec) + "\n")
                fh.write("not json\n")
            samples = voice_profile.ingest_transcripts(projects_dir=tmp, days=1)
        self.assertEqual(len(samples), 1)
        text = samples[0]["text"]
        self.assertIn("rework the intro", text)
        self.assertNotIn("ls -la", text)
        self.assertNotIn("https://", text)

    def test_transcript_duplicates_from_compaction_are_removed(self):
        rec = {"type": "user", "promptSource": "typed",
               "message": {"role": "user", "content":
                           "walk me through the failure mode before you patch"
                           " anything, i want the story first"}}
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "proj"
            project.mkdir()
            for name in ("a.jsonl", "b.jsonl"):
                (project / name).write_text(json.dumps(rec) + "\n", encoding="utf-8")
            samples = voice_profile.ingest_transcripts(projects_dir=tmp, days=1)
        self.assertEqual(len(samples), 1)

    def test_voice_dir_ingests_own_voice_blocks_and_skips_generic(self):
        with tempfile.TemporaryDirectory() as tmp:
            few_shot = Path(tmp) / "few-shot"
            few_shot.mkdir()
            (few_shot / "pairs.md").write_text(
                "# pairs\n\n**GENERIC:**\n> Here's a thread on agents 🧵\n\n"
                "**OWNER:**\n> Stop building complex teams.\n>\n"
                "> Split the work. Keep the coherence.\n",
                encoding="utf-8",
            )
            samples = voice_profile.ingest_voice_dir(tmp)
        self.assertEqual(len(samples), 1)
        self.assertIn("Split the work", samples[0]["text"])
        self.assertNotIn("thread on agents", samples[0]["text"])

    def test_path_ingester_reads_prose_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "note.md"
            sample.write_text(
                "The launch went sideways twice before it went right, and the"
                " second failure taught us more than the win did.\n",
                encoding="utf-8",
            )
            samples = voice_profile.ingest_paths([str(Path(tmp) / "*.md")])
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0]["source"], "paths")


class PersonalScanTests(unittest.TestCase):
    BUBBLY = ("Shipped it! The gate held! The loop is faster now! "
              "Why does that work? What breaks next? Who reviews it?")

    def high_energy_profile(self):
        return {
            "punctuation": {"exclamation_per_1000_words": 150.0,
                            "question_per_1000_words": 200.0},
            "sentence_length": {"top_trigram_share": 0.6},
            "openers": {"favorites": ["most"]},
        }

    def test_scan_without_profile_matches_profile_none(self):
        text = "Our cutting-edge tool!! Really!"
        self.assertEqual(scan_text.scan(text), scan_text.scan(text, profile=None))

    def test_profile_relaxes_exclamation_and_question_budgets(self):
        without = scan_text.scan(self.BUBBLY)
        with_profile = scan_text.scan(self.BUBBLY, profile=self.high_energy_profile())
        rules_without = {f["rule"] for f in without}
        rules_with = {f["rule"] for f in with_profile}
        self.assertIn("exclamation budget", rules_without)
        self.assertIn("rhetorical questions", rules_without)
        self.assertNotIn("exclamation budget", rules_with)
        self.assertNotIn("rhetorical questions", rules_with)

    def test_personal_findings_are_a_subset_of_global_findings(self):
        texts = [
            self.BUBBLY,
            "Most days start slow. Most builds break once. Most fixes are"
            " boring. Most wins compound quietly.",
            "This is a testament to our seamless, cutting-edge platform!",
        ]
        for text in texts:
            base = {(f["severity"], f["rule"], f["detail"])
                    for f in scan_text.scan(text)}
            personal = {(f["severity"], f["rule"], f["detail"])
                        for f in scan_text.scan(text, profile=self.high_energy_profile())}
            self.assertTrue(personal.issubset(base), (text, personal - base))

    def test_critical_and_vocabulary_rules_never_personalize(self):
        text = ("A testament to our seamless platform — truly cutting-edge."
                " It's not just fast, it's a paradigm.")
        base = scan_text.scan(text)
        personal = scan_text.scan(text, profile=self.high_energy_profile())
        self.assertEqual(
            [(f["severity"], f["rule"], f["detail"]) for f in base],
            [(f["severity"], f["rule"], f["detail"]) for f in personal],
        )

    def test_favorite_opener_needs_four_repeats_others_still_three(self):
        text = ("Most days start slow. Most builds break once. Most fixes are"
                " boring. Ship anyway, always.")
        base_rules = {f["rule"] for f in scan_text.scan(text)}
        personal_rules = {f["rule"] for f in
                          scan_text.scan(text, profile=self.high_energy_profile())}
        self.assertIn("repetitive sentence opener", base_rules)
        self.assertNotIn("repetitive sentence opener", personal_rules)
        # a non-favorite opener stays at three repeats even with a profile
        other = ("Ship days start slow. Ship builds break once. Ship fixes are"
                 " boring. Rest anyway, always.")
        self.assertIn("repetitive sentence opener",
                      {f["rule"] for f in
                       scan_text.scan(other, profile=self.high_energy_profile())})


class ApiFreezeTests(unittest.TestCase):
    """Downstream consumers import scan, score, and the phrase lists directly
    via spec_from_file_location. The voice layer must stay additive: same
    names, same positional signature, no new required arguments, no
    non-stdlib imports."""

    def test_public_names_and_positional_signature_survive(self):
        import inspect

        for name in ("CRITICAL_PHRASES", "MAJOR_PHRASES", "scan", "score"):
            self.assertTrue(hasattr(scan_text, name))
        params = list(inspect.signature(scan_text.scan).parameters.values())
        self.assertEqual([p.name for p in params], ["text", "mode", "profile"])
        self.assertEqual(params[1].default, "prose")
        self.assertIsNone(params[2].default)
        # positional call shape used by external gates still works
        findings = scan_text.scan("delve into the tapestry", "prose")
        self.assertTrue(findings)
        self.assertIsInstance(scan_text.score(findings), int)

    def test_scan_text_loads_standalone_like_external_gates_do(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "unmachined_scan_freeze_check", SCRIPTS / "scan_text.py")
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.scan("plain copy."), [])

    def test_cli_without_profile_flags_is_unchanged_and_personal_flag_works(self):
        env = dict(os.environ)
        with tempfile.TemporaryDirectory() as tmp:
            env["XDG_CONFIG_HOME"] = tmp  # no profile exists there
            base = subprocess.run(
                [sys.executable, str(SCRIPTS / "scan_text.py"), "-", "--json"],
                input="Shipped it! Loved it! Named it!",
                text=True, capture_output=True, env=env, check=False,
            )
            payload = json.loads(base.stdout)
            self.assertFalse(payload["personal"])
            self.assertIn("exclamation budget",
                          {f["rule"] for f in payload["findings"]})

            profile_dir = Path(tmp) / "unmachined"
            profile_dir.mkdir(parents=True)
            (profile_dir / "voice-profile.json").write_text(json.dumps({
                "enabled": True,
                "punctuation": {"exclamation_per_1000_words": 400.0},
            }), encoding="utf-8")
            personal = subprocess.run(
                [sys.executable, str(SCRIPTS / "scan_text.py"), "-", "--json",
                 "--personal"],
                input="Shipped it! Loved it! Named it!",
                text=True, capture_output=True, env=env, check=False,
            )
            payload = json.loads(personal.stdout)
            self.assertTrue(payload["personal"])
            self.assertNotIn("exclamation budget",
                             {f["rule"] for f in payload["findings"]})

    def test_disabled_profile_is_ignored_by_personal_flag(self):
        env = dict(os.environ)
        with tempfile.TemporaryDirectory() as tmp:
            env["XDG_CONFIG_HOME"] = tmp
            profile_dir = Path(tmp) / "unmachined"
            profile_dir.mkdir(parents=True)
            (profile_dir / "voice-profile.json").write_text(json.dumps({
                "enabled": False,
                "punctuation": {"exclamation_per_1000_words": 400.0},
            }), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "scan_text.py"), "-", "--json",
                 "--personal"],
                input="Shipped it! Loved it! Named it!",
                text=True, capture_output=True, env=env, check=False,
            )
            payload = json.loads(result.stdout)
            self.assertFalse(payload["personal"])


class LearnCliTests(unittest.TestCase):
    def test_learn_status_off_on_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "x-posts.json"
            corpus.write_text(json.dumps([s["text"] for s in FIXTURE_SAMPLES]),
                              encoding="utf-8")
            output = Path(tmp) / "profile.json"
            base_args = ["--x-corpus", str(corpus), "--voice-dir", "",
                         "--no-transcripts", "--output", str(output)]

            def run(*verb):
                return subprocess.run(
                    [sys.executable, str(SCRIPTS / "learn.py"), *verb, *base_args],
                    text=True, capture_output=True, check=False,
                )

            built = run()
            self.assertEqual(built.returncode, 0, built.stderr)
            profile = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(profile["enabled"])
            self.assertEqual(profile["corpus"]["per_source"], {"x-posts": 5})

            self.assertEqual(run("status").returncode, 0)
            self.assertEqual(run("off").returncode, 0)
            self.assertFalse(json.loads(output.read_text())["enabled"])
            self.assertEqual(run("on").returncode, 0)
            self.assertTrue(json.loads(output.read_text())["enabled"])

    def test_default_sources_resolve_from_local_config_not_hardcoded_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "x-posts.json"
            corpus.write_text(json.dumps([s["text"] for s in FIXTURE_SAMPLES]),
                              encoding="utf-8")
            config_dir = Path(tmp) / "unmachined"
            config_dir.mkdir()
            (config_dir / "config.json").write_text(
                json.dumps({"voice_corpus": str(corpus)}), encoding="utf-8")
            output = Path(tmp) / "profile.json"
            env = dict(os.environ)
            env["XDG_CONFIG_HOME"] = str(tmp)
            env.pop("UNMACHINED_VOICE_CORPUS", None)
            env.pop("UNMACHINED_VOICE_DIR", None)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "learn.py"),
                 "--no-transcripts", "--output", str(output)],
                text=True, capture_output=True, env=env, check=False, cwd=tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(profile["corpus"]["per_source"], {"x-posts": 5})
            # the unconfigured source is skipped with a pointer, not an error
            self.assertIn("voice-dir: not configured", result.stderr)

    def test_env_var_overrides_config_for_corpus_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "env-posts.json"
            corpus.write_text(json.dumps([s["text"] for s in FIXTURE_SAMPLES]),
                              encoding="utf-8")
            output = Path(tmp) / "profile.json"
            env = dict(os.environ)
            env["XDG_CONFIG_HOME"] = str(tmp)  # no config file there
            env["UNMACHINED_VOICE_CORPUS"] = str(corpus)
            env.pop("UNMACHINED_VOICE_DIR", None)
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "learn.py"),
                 "--voice-dir", "", "--no-transcripts", "--output", str(output)],
                text=True, capture_output=True, env=env, check=False, cwd=tmp,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(profile["corpus"]["per_source"], {"x-posts": 5})


if __name__ == "__main__":
    unittest.main()
