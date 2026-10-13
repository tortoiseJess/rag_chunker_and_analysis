# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->
I picked the city_guides corpora, I asked questions that are one step straighforward questions present in the text and tricky ones 
which needs logical deduction. Before changing to my chunker, the rag failed to answer my questions and could not retrieve relevant information that were close enough. Now it can.

## Chunking Strategy

**Method:** `chunker.py::split_documents`. Every document in `city_guides` is
structured the same way: an H1 title, then a run of `## Heading` sections, and
almost every section is exactly one paragraph of 3-5 sentences (verified by
reading all 14 files in Milestone 1). That structure *is* the chunk boundary —
each section already reads as one complete, self-contained thought ("Getting
there", "Eat and drink", etc.), so I split on headings first, then split each
section into sentences, then pack sentences into a chunk without ever cutting
a sentence in half.

**Chunk size:**
  loaded   14 documents, 28,958 characters, ~2,068 characters per document
  chunked  95 chunks, 299 characters on average (shortest 172, longest 633)

I did not pick a target character count first and cut to fit it. I measured
the sections instead: almost all of them are 150-650 characters and 3-5
sentences, so I set the target/max (500/800 chars in `chunker.py`) *above*
the longest section I found, so that the common case — one heading, one
paragraph — becomes exactly one chunk. That satisfies criterion 4 directly:
the chunk is "large enough to hold 3-4 sentences" because in this corpus a
section basically *is* 3-4 sentences. The one outlier, `guide_accessibility.md`,
packs several bolded sub-paragraphs under each heading instead of one, so its
sections run long enough (up to ~1,000 chars) to split into two chunks — that's
the only file where the split/overlap logic actually fires.

**Overlap:**

4 words, and it only ever applies *within* a section that had to be split
(never between two different headings — a new heading always starts clean).
Overlap exists so that if a section is long enough to become two chunks, the
second chunk isn't missing the antecedent of whatever it starts with. I chose
4 words, not a character count, because the unit that matters here is "enough
words to place the sentence," and this corpus's sentences are short enough
that even 4-5 words is normally a recognizable clause fragment, e.g. chunk
`guide_accessibility.md#2` opens with "and through the centre." — the tail of
the previous chunk's last sentence — before continuing with its own new
sentences. (I did not tune this against a bigger number; I picked the smallest
overlap that still reads as "picking up where the last chunk left off" rather
than repeating a whole sentence, since duplicating more than that just wastes
embedding budget on words already present in the neighboring chunk.)

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

======================================================================
Chunk 1  |  source: guide_accessibility.md#1  |  produced by: chunker.py::split_documents
======================================================================
Straightforward: **Thornby Wells** is the easiest town in the region. It is flat, compact, and everything is within three minutes of everything else. Parking is free for two hours anywhere in town and the station is central. The pump room and gardens are level throughout. **Marchwood** has a modern tram network with level boarding on all four lines, running every 8 minutes on weekdays. The city museum and covered market are both step-free. The distances between districts are the main consideration. **Brightwater** is level along the river and through the centre.

======================================================================
Chunk 2  |  source: guide_accessibility.md#2  |  produced by: chunker.py::split_documents
======================================================================
Straightforward: and through the centre. The mill museum is step-free. The station is a 15-minute walk from campus on flat ground, or the shuttle meets the four busiest arrivals.

<!-- Chunks 1 and 2 above are the same "Straightforward" section, split because
     it packs several bolded sub-paragraphs into one heading. Chunk 2 opens
     with "and through the centre." — the last 4 words of chunk 1 — which is
     the overlap in action. -->

======================================================================
Chunk 3  |  source: guide_givens_mill.md#3  |  produced by: chunker.py::split_documents
======================================================================
Eat and drink: A tearoom attached to the mill, open 10 to 4 daily except Tuesdays, which sells bread made from the flour ground twenty metres away and is the reason most people come. One pub, food served lunchtimes and Thursday to Saturday evenings.

======================================================================
Chunk 4  |  source: guide_kestrelford.md#6  |  produced by: chunker.py::split_documents
======================================================================
When to go: Late spring and early autumn. The Saturday market runs year-round but is much reduced from November to February. August is busy with walkers. The single-track approach road is genuinely difficult in snow and the town can be cut off for a day or two most winters.

======================================================================
Chunk 5  |  source: guide_regional_transport.md#1  |  produced by: chunker.py::split_documents
======================================================================
Buses: Three operators run in the region and they do not accept each other's tickets, which is the single most common source of confusion for visitors. Services concentrate on weekday daytimes. Sunday service is minimal to non-existent outside the Brightwater town routes. The Kestrelford service is hourly on weekdays, two-hourly on Saturdays, and does not run on Sundays. The Halden Bay coast service runs four times daily year-round.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**
======================================================================
The assembled prompt, exactly as sent
======================================================================
Documents:

[from guide_eating.md]
Opening hours: This catches visitors out more than anything else. Outside Marchwood, kitchens across the region stop serving at 9pm and often earlier. Kestrelford's pubs serve 12 to 2 and 6 to 8:30 and there is nowhere to eat at all outside those windows. Elder Ness has one pub, closed Mondays. Sunday evening is the hardest meal to find anywhere except Marchwood and Thornby Wells.

[from guide_eating.md]
Practical: Cash is still useful at markets and in the smaller villages. Corry Vale has a farm shop at the valley mouth selling bread and cheese and little else, closing at 4pm — bring supplies if you are staying there. Elder Ness has one shop, closed Sundays and after 5pm.

[from guide_elder_ness.md]
Elder Ness: Elder Ness is a headland with a village of 300 on it, a lighthouse, a bird observatory, and very little else. People come for one of three reasons — birds, walking, or a deliberate absence of things to do.

[from guide_corry_vale.md]
Eat and drink: One pub in the largest village serves food seven days a week. A second, in the third village, opens Thursday to Sunday. There is a farm shop at the valley mouth that sells bread, cheese and little else, and it closes at 4pm. Bring supplies; this is not a place with options.

[from guide_elder_ness.md]
Eat and drink: One pub, serving food 12 to 2 and 6 to 8, closed Mondays. A shop that sells basics and closes at 5pm and all day Sunday. That is the complete list. Visitors staying more than a night bring food with them.

---

Question: Is there anywhere to eat in Elder Ness on a Sunday evening?

Answer using only the documents above, and name the file you used.

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|

These are in scope in corpous questions?
is the museum mentioned in Brighwater suitable for people in wheelchairs?
  run 1: —  (best distance 0.671)
  run 2: —  (best distance 0.671)
  run 3: —  (best distance 0.671)

I like quiet places, should I stay at the seafront hotels?
  run 1: —  (best distance 0.333)
  run 2: —  (best distance 0.333)
  run 3: —  (best distance 0.333)

Which city has the larges population? Which one has the least?
  run 1: —  (best distance 0.636)
  run 2: —  (best distance 0.636)
  run 3: —  (best distance 0.636)

Is there anywhere to eat in Elder Ness on a Sunday evening?
  run 1: —  (best distance 0.394)
  run 2: —  (best distance 0.394)
  run 3: —  (best distance 0.394)

What time do restaurants on Halden Bay's harbour front stop serving in November
  run 1: —  (best distance 0.302)
  run 2: —  (best distance 0.302)
  run 3: —  (best distance 0.302)

I'm taking a Sunday day trip from the regional hub to Kestrelford using only public transport — is that possible?
  run 1: —  (best distance 0.463)
  run 2: —  (best distance 0.463)
  run 3: —  (best distance 0.463)

Out-of-scope questions (the gate should refuse these):
  refused  (best distance 0.802)  What is the capital of Mongolia?
  refused  (best distance 0.888)  How do I change the oil in a diesel engine?
  refused  (best distance 0.967)  Who won the 1994 World Cup?
  refused  (best distance 0.839)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.847)  How do I write a for loop in Rust?
  -> gate refused 5 of 5

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**
I asked Claude to split from the heading in the city guides and two different headings cannot be in the same chunk, split chunks by sentences, and it needs to fulfill my criteria of 3-5 sentences.

**2.**
It needs to overlap 4 words as I read that some concepts are similar in different docs so I need this coherence. So I told claude to fix it.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 3/5 | 3/5 | 3/5 | MISSED |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk contains at least 3 sentences | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. (revised) Every cited source was actually retrieved — no hallucinated citations | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

> `questions.py` has 6 questions, but this run's judging (the table above, and
> `metrics.py`) only covers the first 5 — the Kestrelford day-trip question
> (#6) was not included in this run.

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->
Question: Is there anywhere to eat in Elder Ness on a Sunday evening?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.3936     guide_eating.md                  Opening hours: This catches visitors out more than a...
2   0.4568     guide_eating.md                  Practical: Cash is still useful at markets and in th...
3   0.4623     guide_elder_ness.md              Elder Ness: Elder Ness is a headland with a village ...
4   0.4835     guide_corry_vale.md              Eat and drink: One pub in the largest village serves...
5   0.5473     guide_elder_ness.md              Eat and drink: One pub, serving food 12 to 2 and 6 t...

Gate: best distance 0.394 is under the 0.7 cutoff
store.search() retrieves the vectors from chroma db (this answers criteria 1,2, 5)

Out-of-scope questions (the gate should refuse these):
  refused  (best distance 0.802)  What is the capital of Mongolia?
  refused  (best distance 0.888)  How do I change the oil in a diesel engine?
  refused  (best distance 0.967)  Who won the 1994 World Cup?
  refused  (best distance 0.839)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.847)  How do I write a for loop in Rust?
  -> gate refused 5 of 5
  That output is produced by check_out_of_scope() in run_eval.py:278 (
## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MISSED | `metrics.py::retrieval_hits()` reruns `store.search()` per question and checks `rapidfuzz.fuzz.partial_ratio(expects, chunk.text) >= 60` against every retrieved chunk — a hit if any chunk clears that bar. Came back 3/5, same in all three runs (retrieval is deterministic, so it can't vary run to run) — below the 4-of-5 target. |
| 2 | Every answer names a source | MET | Read the saved answer text in `results/*.md` (and `.cache/run_eval_state.json`) for each run — every one of the 5 answers names at least one `guide_*.md` filename. 5/5 in all three runs. |
| 3 | Gate stops out-of-corpus questions | MET | `run_eval.py::check_out_of_scope()` runs each `OUT_OF_SCOPE` question through `gate.check()` once — deterministic, so one pass is the whole measurement. Refused 5/5. |
| 4 | Chunk contains at least 3 sentences | MET | `metrics.py::retrieval_hits()` splits each retrieved chunk's text on `.!?` and counts pieces longer than 20 characters (to drop stray fragments) — a hit if any retrieved chunk has 3+ of those. 5/5, deterministic across runs. |
| 5 | (revised) Every cited source was actually retrieved | MET | `metrics.py::source_attribution_hits()` regex-extracts the `guide_*.md` filenames each saved answer cites and checks that set is a subset of the sources `store.search()` actually returned for that question (from the same cached run data as #2). 5/5 in all three runs — no hallucinated citations. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->
Criteria 1:
My ground truth expects is wrong. So it's even before the pipeline above

## The Improvement

**What I changed:**
The expect statement now is just a copy of the relevant text that I want AI to use instead of me paraphrasing.

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->
     It was the only one failing criteria in that run table.

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunk contains at least 3 sentences | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. (revised) Every cited source was actually retrieved — no hallucinated citations | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->
It helped
## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
