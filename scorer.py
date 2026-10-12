"""
Unit 2: deciding whether an answer was actually correct.

Two approaches are here. Both satisfy run_eval.py's contract:

    judge(question, expects, answer, results) -> bool

`judge_by_keywords` is cheap and deterministic but brittle against paraphrasing
and, especially, against negation ("noisy" vs. "not noisy" both contain
"noisy"). `judge_by_llm` asks the model itself whether the answer conveys the
expected fact, which handles paraphrasing but costs a call per run and can be
wrong in its own way.

Going to experiment with both approaches.
"""

import re

from generate import generate


# ─── 1: keyword matching ───────────────────────────────────────────

# Words that would make any keyword match meaningless (negations, mostly) —
# if these differ between `expects` and `answer`, a keyword hit is probably
# wrong rather than right.
_NEGATORS = {"no", "not", "n't", "closed", "none", "never", "without"}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z']+", text.lower()))


def judge_by_keywords(question: str, expects: str, answer: str, results) -> bool:
    """
    Pass if the answer's words cover the meaningful words in `expects`,
    AND the two don't disagree on negation.

    This is "good enough to try first," not "good enough to trust." Read a
    sample of what it marks right and wrong before you believe its verdicts.
    """
    if not expects.strip():
        return False

    expect_tokens = _tokens(expects)
    answer_tokens = _tokens(answer)

    # Drop short/common words so we're matching on content, not glue.
    stopwords = {"the", "a", "an", "is", "are", "and", "or", "of", "to", "in",
                 "one", "with", "for", "on", "at"}
    content_tokens = expect_tokens - stopwords - _NEGATORS
    if not content_tokens:
        content_tokens = expect_tokens  # fall back rather than auto-pass

    overlap = content_tokens & answer_tokens
    covered_enough = len(overlap) >= max(1, len(content_tokens) // 2)

    # Negation check: if `expects` contains a negator, the answer should too
    # (and vice versa) or the content-word overlap above is matching the
    # opposite claim.
    expects_negated = bool(expect_tokens & _NEGATORS)
    answer_negated = bool(answer_tokens & _NEGATORS)
    if expects_negated != answer_negated:
        return False

    return covered_enough


# ─── 2: LLM as judge ───────────────────────────────────────────────

_JUDGE_SYSTEM = """You are a strict grader for a Q&A system, not an assistant.

You will be given a question, a fact the correct answer must convey, and the
system's actual answer. Decide only whether the actual answer conveys that
fact — do not reward answers that are well-written but miss the fact, and do
not penalize answers that phrase it differently than expected.

A refusal ("I don't have enough information...") never conveys the fact:
answer NO for those.

Reply with exactly one word: YES or NO."""


def judge_by_llm(question: str, expects: str, answer: str, results) -> bool:
    """
    Ask the model whether `answer` actually conveys `expects`.

    Uses the shared generate() in generate.py, so this goes through the same
    rate limiter, retry logic, and session budget as every other call in the
    course — a run of 6 questions x 3 runs adds up to 18 extra calls, which
    counts against SESSION_REQUEST_BUDGET like anything else.

    cache=True on purpose: the same (question, expects, answer) triple should
    always get the same verdict, so re-grading an already-graded answer
    shouldn't cost a second call.
    """
    if not expects.strip():
        return False

    prompt = (
        f"Question: {question}\n\n"
        f"Fact the answer must convey: {expects}\n\n"
        f"System's actual answer: {answer}\n\n"
        f"Does the actual answer convey that fact? Reply YES or NO."
    )
    verdict = generate(prompt, system=_JUDGE_SYSTEM, cache=True).strip().upper()
    return verdict.startswith("Y")


# ───────────────────────────────────────────────────────────────────

judge = judge_by_keywords
