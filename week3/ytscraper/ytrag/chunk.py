"""Segment[] -> Chunk[], merged into overlapping time windows.

Deliberately hand-written. A generic text splitter (RecursiveCharacterText-
Splitter and friends) operates on one concatenated string and throws the
timestamps away. The timestamp *is* the product here, so chunking happens in
the time domain, on the segment list, and never splits a segment.
"""

import re
from collections import Counter

from ytrag.config import (
    CHUNK_OVERLAP_SECONDS,
    CHUNK_SECONDS,
    MIN_CHUNK_WORDS,
)
from ytrag.models import Chunk, Segment, Video

_SENTENCE_SPLIT = re.compile(r"[.!?\n]+")


def is_repetitive(text: str, threshold: float = 0.6) -> bool:
    """True if one sentence makes up most of the chunk.

    This is Whisper's loop hallucination surviving into a chunk. These are
    retrieval poison: they match everything and say nothing.
    """
    sentences = [s.strip().lower() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    if len(sentences) < 3:
        return False
    most_common = Counter(sentences).most_common(1)[0][1]
    return most_common / len(sentences) >= threshold


def chunk_segments(
    video: Video,
    segments: list[Segment],
    window_seconds: int = CHUNK_SECONDS,
    overlap_seconds: int = CHUNK_OVERLAP_SECONDS,
    min_words: int = MIN_CHUNK_WORDS,
) -> list[Chunk]:
    """Greedy time-window merge with segment-aligned overlap."""
    segments = [s for s in segments if s.text.strip()]
    if not segments:
        return []

    chunks: list[Chunk] = []
    i = 0
    while i < len(segments):
        window_start = segments[i].start
        j = i
        while j < len(segments) and segments[j].end - window_start < window_seconds:
            j += 1
        # j is one past the last segment in the window (or len(segments)).
        last = min(j, len(segments) - 1)
        body_segments = segments[i : last + 1]

        body = " ".join(s.text.strip() for s in body_segments).strip()
        start_sec = int(body_segments[0].start)
        end_sec = int(body_segments[-1].end)

        enough_words = len(body.split()) >= min_words
        if enough_words and not is_repetitive(body):
            chunks.append(
                Chunk(
                    chunk_id=f"{video.video_id}:{start_sec}",
                    video_id=video.video_id,
                    video_title=video.title,
                    start_sec=start_sec,
                    end_sec=end_sec,
                    # Prefixing the title is a cheap trick that meaningfully
                    # improves retrieval: a chunk from minute 34 usually never
                    # restates which topic it belongs to.
                    text=f"{video.title}\n\n{body}",
                )
            )

        if last >= len(segments) - 1:
            break

        # Back up to the nearest segment boundary inside the overlap so the
        # next window re-reads the tail of this one. Never split a segment.
        overlap_start = segments[last].end - overlap_seconds
        next_i = last + 1
        for k in range(i, last + 1):
            if segments[k].start >= overlap_start:
                next_i = k
                break
        # Always make forward progress, even when one segment is longer than
        # the whole window.
        i = max(next_i, i + 1)

    return chunks
