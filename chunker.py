"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# city_guides documents are structured: an H1 title, then a run of "## Heading"
# sections, each holding one paragraph of a few sentences. A section is the
# natural unit of meaning here (criterion 4 wants 3-4 sentences per chunk),
# so chunks never cross a heading boundary. Overlap only makes sense *inside*
# a paragraph that had to be split across chunks, so a fresh heading always
# starts overlap-free.

HEADING_RE = re.compile(r"^#{1,6}\s+.*$", re.MULTILINE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")

TARGET_CHARS = 500     # aim to fill a chunk to about this many characters...
MAX_CHARS = 800        # ...but never exceed this before starting a new one
OVERLAP_WORDS = 4      # words repeated from the end of one chunk to the next


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Break a document into (heading, body) sections on '#'-style headings."""
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [("", text.strip())]

    sections = []
    lead = text[: matches[0].start()].strip()
    if lead:
        sections.append(("", lead))

    for i, m in enumerate(matches):
        heading = m.group().lstrip("#").strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        if body:
            sections.append((heading, body))

    return sections


def _split_sentences(paragraph: str) -> list[str]:
    """Split one paragraph into sentences, collapsing internal line breaks."""
    flat = " ".join(paragraph.split())
    if not flat:
        return []
    return [s.strip() for s in SENTENCE_RE.split(flat) if s.strip()]


def _group_sentences(sentences: list[str]) -> list[str]:
    """
    Pack sentences into chunks, never splitting a sentence in half, with the
    last few words of a chunk repeated at the start of the next one (overlap
    only makes sense within the same paragraph, so this never crosses a
    heading — callers only pass sentences from one section).
    """
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0
    has_new_content = False  # False while `current` holds only carried-over overlap words

    def start_new_chunk() -> None:
        nonlocal current, current_len, has_new_content
        pieces.append(" ".join(current))
        overlap = current[-1].split()[-OVERLAP_WORDS:]
        current = [" ".join(overlap)] if overlap else []
        current_len = len(current[0]) if current else 0
        has_new_content = False

    for sentence in sentences:
        added_len = len(sentence) + (1 if current else 0)
        if current and has_new_content and current_len + added_len > MAX_CHARS:
            start_new_chunk()
            added_len = len(sentence) + (1 if current else 0)

        current.append(sentence)
        current_len += added_len
        has_new_content = True
        if current_len >= TARGET_CHARS:
            start_new_chunk()

    # Trailing overlap with no sentence appended after it just repeats the
    # end of the previous chunk — drop it instead of emitting a fragment.
    if current and has_new_content:
        pieces.append(" ".join(current))

    return pieces


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Sentence-aware chunking for city_guides: one chunk per heading section
    where the section fits comfortably (most sections here are a single
    3-5 sentence paragraph), splitting further only when a section runs long.
    No overlap ever crosses a heading boundary; a 4-word overlap is carried
    between chunks split out of the same paragraph.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        index = 0
        for heading, body in _split_sections(doc.text):
            sentences = _split_sentences(body)
            if not sentences:
                continue
            for piece in _group_sentences(sentences):
                text = f"{heading}: {piece}" if heading else piece
                chunks.append(
                    Chunk(
                        text=text,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
