"""
Fill in the per-criterion hit counts for the Run Log table in README.md
(criteria.md's criteria 1, 4, and 5 -- the revised version of 5).

Criteria 2 and 3 already have real numbers elsewhere: 2 comes from reading
the generated answers in results/*.md, and 3 comes from
run_eval.py::check_out_of_scope. Those need no new code here.

Criteria 1 and 4 need to look *inside* the retrieved chunks, which
run_eval.py's saved state doesn't keep (it only saves source filenames, not
chunk text) -- so retrieval_hits() re-runs retrieval live. That's cheap:
store.search() is deterministic and makes no model calls.

Criterion 5 (revised in unit 2: no hallucinated source citations) only
needs the answer text and the sources that were retrieved for it, both of
which run_eval.py already saved to its cache -- so source_attribution_hits()
reads that instead of calling the model again.

    python metrics.py
"""

import json
import re

from rapidfuzz import fuzz

import config
import questions as qs
from store import search

FUZZY_THRESHOLD = 60          # rapidfuzz.fuzz.partial_ratio score to count as a hit
MIN_SENTENCE_CHARS = 20       # drop pieces this short -- stray fragments, not sentences

STATE_PATH = config.CACHE_DIR / "run_eval_state.json"   # written by run_eval.py
_SOURCE_PATTERN = re.compile(r"[\w-]+\.md")


def _is_literal_hit(expects: str, chunk_text: str) -> bool:
    return expects.strip().lower() in chunk_text.lower()


def _is_fuzzy_hit(expects: str, chunk_text: str, threshold: int = FUZZY_THRESHOLD) -> bool:
    return fuzz.partial_ratio(expects.lower(), chunk_text.lower()) >= threshold


def _sentence_count(chunk_text: str) -> int:
    pieces = re.split(r"[.!?]+(?:\s|$)", chunk_text)
    return sum(1 for p in pieces if len(p.strip()) >= MIN_SENTENCE_CHARS)


def retrieval_hits(top_k=None, threshold=None, corpus=None, variant="default"):
    """
    Re-run retrieval for every answered test question and score criteria
    1 and 4 against the chunks that come back.

    Criterion 1: hit if any retrieved chunk fuzzy-matches `expects`
      (rapidfuzz partial_ratio >= FUZZY_THRESHOLD). Counted out of all
      answered questions.

    Criterion 4: hit if any retrieved chunk has at least 3 sentences.
      Counted out of all answered questions.

    Returns a dict of {"criterion_1": (hits, total), "criterion_4": (hits, total),
    "detail": [per-question rows]}.
    """
    top_k = top_k or config.TOP_K
    threshold = config.THRESHOLD if threshold is None else threshold
    corpus = corpus or config.CORPUS

    items = qs.answered()
    c1_hits = c4_hits = 0
    detail = []

    for item in items:
        question = item["question"]
        expects = item.get("expects", "")
        results = search(question, top_k=top_k, corpus=corpus, variant=variant)

        literal_hit = any(_is_literal_hit(expects, r.text) for r in results)
        fuzzy_hit = any(_is_fuzzy_hit(expects, r.text) for r in results)
        long_enough = any(_sentence_count(r.text) >= 3 for r in results)

        if fuzzy_hit:
            c1_hits += 1
        if long_enough:
            c4_hits += 1

        detail.append({
            "question": question,
            "expects": expects,
            "literal_hit": literal_hit,
            "fuzzy_hit": fuzzy_hit,
            "has_3plus_sentence_chunk": long_enough,
            "sources": sorted({r.source for r in results}),
        })

    return {
        "criterion_1": (c1_hits, len(items)),
        "criterion_4": (c4_hits, len(items)),
        "detail": detail,
    }


def _cited_sources(answer: str) -> set[str]:
    """Filenames (e.g. `guide_eating.md`) that an answer names, in whatever
    formatting the model used (backticks, italics, plain)."""
    return set(_SOURCE_PATTERN.findall(answer))


def source_attribution_hits():
    """
    Criterion 5 (revised in unit 2): every source an answer cites must be
    one of the sources actually retrieved for that question -- no invented
    or misattributed filenames.

    Reads run_eval.py's saved cache (one entry per question/run, with the
    generated answer text and the retrieved source list) rather than
    calling the model again -- this only needs to compare what was already
    produced against what was already retrieved.

    Returns {run_number: (hits, total)}, since this is about the generated
    answer and so (unlike criteria 1 and 4) can vary between runs.
    """
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            f"No {STATE_PATH} -- run `python run_eval.py` first so there's "
            "something to check."
        )
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    hits_by_run: dict[int, list[bool]] = {}
    for question, data in state.items():
        for entry in data["transcript"]:
            run = entry["run"]
            answer = entry.get("answer", "")
            retrieved = set(entry.get("sources", []))
            cited = _cited_sources(answer)
            clean = cited.issubset(retrieved)
            hits_by_run.setdefault(run, []).append(clean)

    return {run: (sum(oks), len(oks)) for run, oks in sorted(hits_by_run.items())}


if __name__ == "__main__":
    report = retrieval_hits()
    for key in ("criterion_1", "criterion_4"):
        hits, total = report[key]
        print(f"{key}: {hits}/{total}")
    print()
    for row in report["detail"]:
        print(row)

    print("\ncriterion_5 (no hallucinated sources), per run:")
    for run, (hits, total) in source_attribution_hits().items():
        print(f"  run {run}: {hits}/{total}")
