#!/usr/bin/env python3
"""Personal voice profile: computed statistics + exemplars. Zero dependencies.

Builds a deterministic fingerprint of the user's own writing from pluggable
ingesters (X posts corpus, voice few-shot files, Claude Code transcript
user messages, arbitrary path globs). No LLM calls. The profile is plain
JSON stored next to the unmachined config; `scan_text.py --personal` reads
it to relax a small documented set of stylistic budgets toward the personal
baseline. Honesty rules and critical vocabulary never personalize.

The scan-facing contract is the JSON shape, not this module: scan_text.py
never imports voice_profile, it only reads the profile dict.
"""
from __future__ import absolute_import, print_function

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import scan_text  # same directory; reuses sentences() and mask_code()

PROFILE_VERSION = 1
PROFILE_FILENAME = "voice-profile.json"
EXEMPLAR_MAX_CHARS = 300
EXEMPLAR_TARGET = 16

# words too common to be a personal signature
STOPWORDS = frozenset("""
a about above after again all also am an and any are as at be because been
before being below between both but by can cannot could did do does doing
down during each few for from further had has have having he her here hers
him his how i if in into is it its itself just me more most my myself no nor
not now of off on once only or other our ours out over own same she should so
some such than that the their theirs them then there these they this those
through to too under until up very was we were what when where which while
who whom why will with would you your yours yourself
one two three like get got make made new way still even much many going
doesn't don't it's i'm that's there's can't won't isn't aren't didn't
""".split())

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_PATHISH_RE = re.compile(r"(?:^|\s)(?:~?/[\w.@-]+(?:/[\w.@-]+)+|[\w.-]+\.(?:py|js|ts|tsx|jsx|md|json|yaml|yml|toml|sh|rs|go|css|html))(?=\s|$|[,.)])")
_SHELL_LINE_RE = re.compile(
    r"^\s*(?:\$|#!|>>>|(?:sudo\s+)?(?:git|cd|ls|cat|head|tail|grep|find|mkdir|rm|mv|cp|chmod|curl|wget|python3?|pip3?|uv|pnpm|npm|npx|node|cargo|go|make|docker|kubectl|brew|ssh|tar|echo|export)\b)"
)
_HARNESS_TAG_RE = re.compile(
    r"<(?:command-name|command-message|command-args|local-command-stdout|system-reminder|task-notification|ide_context|tool_use_error)"
)
_CONTRACTION_RE = re.compile(r"\b\w+[’'](?:t|s|re|ve|ll|d|m)\b", re.IGNORECASE)
_WORD_RE = re.compile(r"[a-z][a-z'’-]*", re.IGNORECASE)


# ------------------------------------------------------------------ helpers


def profile_path():
    """Default profile location, next to the unmachined user config."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "unmachined" / PROFILE_FILENAME


def strip_noise(text):
    """Remove code fences, inline code, URLs, paths, and shell-looking lines.

    The profile must learn prose, not pasted commands or stack traces.
    """
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]{1,300}`", " ", text)
    text = _URL_RE.sub(" ", text)
    text = _PATHISH_RE.sub(" ", text)
    kept = []
    for line in text.splitlines():
        if _SHELL_LINE_RE.match(line):
            continue
        kept.append(line)
    return "\n".join(kept)


def looks_like_prose(text, min_words=8):
    words = text.split()
    if len(words) < min_words:
        return False
    compact = re.sub(r"\s", "", text)
    if not compact:
        return False
    letters = sum(1 for ch in compact if ch.isalpha())
    return letters / len(compact) >= 0.6


def _dedupe_key(text):
    return hashlib.sha1(re.sub(r"\s+", " ", text.strip().lower()).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- ingesters


def ingest_x_corpus(path):
    """Own-voice X posts: a JSON list of post strings (x-posts.json shape)."""
    samples = []
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return samples
    if not isinstance(data, list):
        return samples
    for item in data:
        if isinstance(item, str) and item.strip():
            samples.append({"text": item.strip(), "source": "x-posts"})
    return samples


def ingest_voice_dir(path):
    """Few-shot contrastive pairs: keep only blockquotes under an own-voice
    author label; GENERIC blocks are counterexamples, not the user's voice.
    voice-guide.md is meta-description and is skipped."""
    samples = []
    few_shot = Path(path) / "few-shot"
    if not few_shot.is_dir():
        return samples
    label_re = re.compile(r"\*\*([A-Za-z0-9_-]+):?\*\*")
    for md in sorted(few_shot.glob("*.md")):
        try:
            lines = md.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        label, block = None, []

        def flush():
            text = "\n".join(block).strip()
            if text and label and label.upper() != "GENERIC":
                samples.append({"text": text, "source": "voice-few-shot"})

        for line in lines:
            m = label_re.search(line)
            if m:
                flush()
                label, block = m.group(1), []
                continue
            stripped = line.strip()
            if stripped.startswith(">"):
                block.append(stripped.lstrip("> ").rstrip())
            elif not stripped and block:
                block.append("")
            elif stripped and block:
                flush()
                label, block = None, []
        flush()
    return samples


def _transcript_user_texts(jsonl_path):
    """Yield human-typed user-message text from one Claude Code transcript.

    Accepts records where promptSource is 'typed', or legacy records without
    the key whose content is a plain string. Rejects sidechains (agent-authored
    subagent prompts), tool results, and harness-generated wrappers.
    """
    try:
        fh = open(jsonl_path, encoding="utf-8", errors="replace")
    except OSError:
        return
    with fh:
        for line in fh:
            if '"type":"user"' not in line and '"type": "user"' not in line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("type") != "user" or rec.get("isSidechain"):
                continue
            source = rec.get("promptSource")
            if "promptSource" in rec and source != "typed":
                continue
            message = rec.get("message") or {}
            if message.get("role") != "user":
                continue
            content = message.get("content")
            texts = []
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list) and source == "typed":
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text") or "")
            for text in texts:
                if text and not _HARNESS_TAG_RE.search(text):
                    yield text


def ingest_transcripts(projects_dir=None, days=90, max_samples=4000):
    """User-role prose from Claude Code transcripts, deduplicated.

    Compaction rewrites full history into new session files, so the same
    typed message appears in several transcripts; dedupe by normalized hash.
    """
    root = Path(projects_dir or Path.home() / ".claude" / "projects")
    if not root.is_dir():
        return []
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    seen, samples = set(), []
    for project in sorted(root.iterdir()):
        if not project.is_dir():
            continue
        for path in sorted(project.glob("*.jsonl")):
            try:
                if path.stat().st_mtime < cutoff:
                    continue
            except OSError:
                continue
            for raw in _transcript_user_texts(path):
                text = strip_noise(raw).strip()
                if not looks_like_prose(text):
                    continue
                key = _dedupe_key(text)
                if key in seen:
                    continue
                seen.add(key)
                samples.append({"text": text, "source": "transcripts"})
                if len(samples) >= max_samples:
                    return samples
    return samples


def ingest_paths(globs):
    """Arbitrary future sample files: .txt/.md prose, one sample per file."""
    import glob as globmod

    samples = []
    for pattern in globs or []:
        for name in sorted(globmod.glob(os.path.expanduser(pattern))):
            path = Path(name)
            if not path.is_file():
                continue
            try:
                text = strip_noise(path.read_text(encoding="utf-8")).strip()
            except (OSError, UnicodeError):
                continue
            if looks_like_prose(text):
                samples.append({"text": text, "source": "paths"})
    return samples


def load_reference_texts(corpus_dir):
    """Other-author corpora (comp-*.json, ref-articles.json) as the reference
    distribution for distinctive-vocabulary scoring."""
    texts = []
    root = Path(corpus_dir)
    if not root.is_dir():
        return texts
    for path in sorted(root.glob("*.json")):
        if not (path.name.startswith("comp-") or path.name.startswith("ref-")):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and isinstance(item.get("body"), str):
                    texts.append(item["body"])
    return texts


# -------------------------------------------------------------- computation


def _clean_for_sentences(text):
    # staccato bullet posts use "•"; drop the marker so bullets read as lines
    return "\n".join(line.lstrip("•").strip() for line in text.splitlines())


def _words(text):
    return _WORD_RE.findall(text.lower())


def compute_profile(samples, reference_texts=None):
    """Deterministic voice fingerprint from ingested samples."""
    per_source, sent_words, openers, opener_bigrams = {}, [], {}, {}
    lowercase_starts = total_sentences = 0
    contractions = em_dashes = exclamations = ellipses = questions = 0
    total_words = 0
    para_sentences, para_words = [], []
    trigram_counts = {}
    word_counts = {}

    for sample in samples:
        text = sample["text"]
        per_source[sample["source"]] = per_source.get(sample["source"], 0) + 1
        masked = scan_text.mask_code(text)
        words_here = len(masked.split())
        total_words += words_here
        contractions += len(_CONTRACTION_RE.findall(masked))
        em_dashes += masked.count("—") + masked.count("–") + len(
            re.findall(r"(?<=\w)--(?=\w)", masked)
        )
        exclamations += masked.count("!")
        ellipses += masked.count("…") + len(re.findall(r"\.\.\.", masked))
        questions += masked.count("?")
        for token in _words(masked):
            word_counts[token] = word_counts.get(token, 0) + 1

        sents = scan_text.sentences(_clean_for_sentences(masked))
        buckets = []
        for sent in sents:
            tokens = sent.split()
            if not tokens:
                continue
            total_sentences += 1
            sent_words.append(len(tokens))
            buckets.append("S" if len(tokens) <= 8 else "M" if len(tokens) <= 20 else "L")
            first_alpha = next((ch for ch in sent if ch.isalpha()), "")
            if first_alpha and first_alpha.islower():
                lowercase_starts += 1
            first = tokens[0].lower().strip(",.;:!?")
            if first:
                openers[first] = openers.get(first, 0) + 1
            if len(tokens) >= 2:
                second = tokens[1].lower().strip(",.;:!?")
                if second:
                    bigram = "{0} {1}".format(first, second)
                    opener_bigrams[bigram] = opener_bigrams.get(bigram, 0) + 1
        joined = "".join(buckets)
        for i in range(len(joined) - 2):
            tri = joined[i:i + 3]
            trigram_counts[tri] = trigram_counts.get(tri, 0) + 1
        for para in re.split(r"\n\s*\n", masked):
            para = para.strip()
            if not para:
                continue
            p_sents = scan_text.sentences(_clean_for_sentences(para))
            if p_sents:
                para_sentences.append(len(p_sents))
                para_words.append(len(para.split()))

    if not total_sentences or not total_words:
        raise ValueError("corpus too small: no prose sentences found")

    bucket_totals = {"S": 0, "M": 0, "L": 0}
    for count in sent_words:
        bucket_totals["S" if count <= 8 else "M" if count <= 20 else "L"] += 1
    trigram_total = sum(trigram_counts.values())
    if trigram_total:
        top_tri = max(sorted(trigram_counts), key=lambda k: trigram_counts[k])
        top_tri_share = trigram_counts[top_tri] / trigram_total
    else:
        top_tri, top_tri_share = None, 0.0

    per_1000 = lambda n: round(n * 1000.0 / total_words, 2)  # noqa: E731

    # distinctive vocabulary: rate ratio vs the reference corpus
    ref_counts, ref_total = {}, 0
    for text in reference_texts or []:
        for token in _words(scan_text.mask_code(text)):
            ref_counts[token] = ref_counts.get(token, 0) + 1
            ref_total += 1
    distinctive = []
    min_count = max(3, total_words // 5000)
    for token, count in word_counts.items():
        if count < min_count or len(token) < 3 or token in STOPWORDS:
            continue
        own_rate = count * 1000.0 / total_words
        if ref_total:
            ref_rate = ref_counts.get(token, 0) * 1000.0 / ref_total
            ratio = (own_rate + 0.01) / (ref_rate + 0.01)
        else:
            ratio = own_rate
        distinctive.append({"word": token, "count": count,
                            "per_1000_words": round(own_rate, 2),
                            "ratio_vs_reference": round(ratio, 1)})
    distinctive.sort(key=lambda d: (-d["ratio_vs_reference"], -d["count"], d["word"]))
    distinctive = distinctive[:20]

    opener_rows = sorted(openers.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    bigram_rows = sorted(opener_bigrams.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    favorites = sorted(
        word for word, count in openers.items()
        if count >= 5 and count / total_sentences >= 0.03
        and word not in ("the", "a", "i", "it")
    )

    return {
        "version": PROFILE_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "enabled": True,
        "corpus": {
            "samples": len(samples),
            "words": total_words,
            "sentences": total_sentences,
            "per_source": dict(sorted(per_source.items())),
            "reference_words": ref_total,
        },
        "sentence_length": {
            "S": round(bucket_totals["S"] / total_sentences, 3),
            "M": round(bucket_totals["M"] / total_sentences, 3),
            "L": round(bucket_totals["L"] / total_sentences, 3),
            "mean_words": round(sum(sent_words) / total_sentences, 1),
            "top_trigram": top_tri,
            "top_trigram_share": round(top_tri_share, 3),
        },
        "contractions": {"per_100_words": round(contractions * 100.0 / total_words, 2)},
        "punctuation": {
            "em_dash_per_1000_words": per_1000(em_dashes),
            "exclamation_per_1000_words": per_1000(exclamations),
            "ellipsis_per_1000_words": per_1000(ellipses),
            "question_per_1000_words": per_1000(questions),
        },
        "casing": {
            "lowercase_sentence_start_rate": round(lowercase_starts / total_sentences, 3),
        },
        "vocabulary": {"distinctive": distinctive},
        "openers": {
            "top": [{"word": w, "count": c} for w, c in opener_rows],
            "top_bigrams": [{"opener": b, "count": c} for b, c in bigram_rows],
            "favorites": favorites,
        },
        "paragraphs": {
            "mean_sentences": round(sum(para_sentences) / len(para_sentences), 2)
            if para_sentences else 0.0,
            "mean_words": round(sum(para_words) / len(para_words), 1)
            if para_words else 0.0,
        },
        "exemplars": select_exemplars(samples),
    }


def select_exemplars(samples, target=EXEMPLAR_TARGET):
    """Deterministic verbatim samples, length-capped and flagged by source.

    Prefer the public own-voice corpus, then curated few-shot, then
    transcripts, then arbitrary paths; within a source, longer clean samples
    first (they carry cadence), ties broken lexically.
    """
    priority = {"x-posts": 0, "voice-few-shot": 1, "transcripts": 2, "paths": 3}
    quota = {"x-posts": 8, "voice-few-shot": 4, "transcripts": 4, "paths": 4}
    chosen, used = [], {}
    candidates = [
        s for s in samples
        if 60 <= len(s["text"]) <= 600 and "http" not in s["text"].lower()
    ]
    candidates.sort(key=lambda s: (priority.get(s["source"], 9), -len(s["text"]), s["text"]))
    for sample in candidates:
        src = sample["source"]
        if used.get(src, 0) >= quota.get(src, 2):
            continue
        text = sample["text"]
        if len(text) > EXEMPLAR_MAX_CHARS:
            text = text[:EXEMPLAR_MAX_CHARS].rsplit(" ", 1)[0]
        chosen.append({"text": text, "source": src})
        used[src] = used.get(src, 0) + 1
        if len(chosen) >= target:
            break
    return chosen


# --------------------------------------------------------------- persistence


def save_profile(profile, path=None):
    path = Path(path or profile_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(profile, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path


def load_profile(path=None):
    path = Path(path or profile_path())
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def format_summary(profile):
    corpus = profile.get("corpus", {})
    lengths = profile.get("sentence_length", {})
    punct = profile.get("punctuation", {})
    lines = [
        "unmachined voice profile",
        "  generated_at:  {0}".format(profile.get("generated_at")),
        "  enabled:       {0}".format(profile.get("enabled", False)),
        "  corpus:        {0} samples, {1} words, {2} sentences".format(
            corpus.get("samples"), corpus.get("words"), corpus.get("sentences")),
        "  per_source:    {0}".format(
            ", ".join("{0}={1}".format(k, v)
                      for k, v in (corpus.get("per_source") or {}).items()) or "(none)"),
        "  sentences:     S={0} M={1} L={2} (mean {3} words)".format(
            lengths.get("S"), lengths.get("M"), lengths.get("L"), lengths.get("mean_words")),
        "  contractions:  {0}/100 words".format(
            profile.get("contractions", {}).get("per_100_words")),
        "  punctuation:   em-dash {0}, ! {1}, ... {2}, ? {3} (per 1000 words)".format(
            punct.get("em_dash_per_1000_words"), punct.get("exclamation_per_1000_words"),
            punct.get("ellipsis_per_1000_words"), punct.get("question_per_1000_words")),
        "  lowercase:     {0} sentence-start rate".format(
            profile.get("casing", {}).get("lowercase_sentence_start_rate")),
        "  openers:       {0}".format(
            ", ".join(row["word"] for row in profile.get("openers", {}).get("top", [])[:6])),
        "  distinctive:   {0}".format(
            ", ".join(row["word"]
                      for row in profile.get("vocabulary", {}).get("distinctive", [])[:10])),
        "  exemplars:     {0}".format(len(profile.get("exemplars", []))),
    ]
    return "\n".join(lines)
