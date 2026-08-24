"""Golden-set retrieval eval.

This is the only way to tell whether a change actually improved retrieval or
just felt better on the one query you kept re-testing. It takes half an hour
to write the golden set and it produces a real number.

Two kinds of entry:

  {"q": "...", "expect_video_id": "abc123", "expect_around_sec": 724,
   "tolerance_sec": 120}
      A hit = the expected video appears in top-k AND at least one returned
      chunk from it overlaps expect_around_sec +/- tolerance.

  {"q": "React hooks kaise kaam karte hain?", "expect_refusal": true}
      A hit = the full answer() pipeline refuses. This is the guard from
      §6.5, and it is the part worth putting on camera.
"""

import json
from pathlib import Path

from ytrag.answer import answer, retrieve_only
from ytrag.config import MAX_DISTANCE

DEFAULT_GOLDEN = Path(__file__).resolve().parent.parent / "eval" / "golden.json"


def load_golden(path: str | Path = DEFAULT_GOLDEN) -> list[dict]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No golden set at {path}")
    with open(path, "r", encoding="utf-8") as f:
        entries = json.load(f)
    # Entries starting with "_" are comments/templates in the shipped file.
    return [e for e in entries if isinstance(e, dict) and not str(e.get("q", "")).startswith("_")]


def _check_retrieval(entry: dict, k: int) -> dict:
    hits = retrieve_only(entry["q"], top_k=k)
    expected_id = entry["expect_video_id"]
    around = entry.get("expect_around_sec")
    tolerance = int(entry.get("tolerance_sec", 120))

    video_hit = any(chunk.video_id == expected_id for chunk, _ in hits)

    time_hit = video_hit and around is None
    if video_hit and around is not None:
        lo, hi = around - tolerance, around + tolerance
        # Overlap between [chunk.start, chunk.end] and [lo, hi].
        time_hit = any(
            chunk.video_id == expected_id and chunk.start_sec <= hi and chunk.end_sec >= lo
            for chunk, _ in hits
        )

    return {
        "q": entry["q"],
        "kind": "retrieval",
        "hit": bool(time_hit),
        "video_hit": bool(video_hit),
        "expected": expected_id,
        "expect_around_sec": around,
        "got": [
            {
                "video_id": chunk.video_id,
                "title": chunk.video_title,
                "timestamp": chunk.timestamp,
                "start_sec": chunk.start_sec,
                "end_sec": chunk.end_sec,
                "distance": round(distance, 4),
            }
            for chunk, distance in hits
        ],
    }


def _check_refusal(entry: dict, k: int) -> dict:
    result = answer(entry["q"], top_k=k)
    refused = not result["grounded"]
    return {
        "q": entry["q"],
        "kind": "refusal",
        "hit": refused,
        "answer": result["answer"],
        "retrieved": result["retrieved"],
    }


def run_eval(path: str | Path = DEFAULT_GOLDEN, k: int = 5) -> dict:
    entries = load_golden(path)
    if not entries:
        return {
            "n": 0,
            f"hit_rate_at_{k}": 0.0,
            "results": [],
            "misses": [],
            "max_distance": MAX_DISTANCE,
        }

    results = []
    for entry in entries:
        if entry.get("expect_refusal"):
            results.append(_check_refusal(entry, k))
        else:
            results.append(_check_retrieval(entry, k))

    retrieval = [r for r in results if r["kind"] == "retrieval"]
    refusal = [r for r in results if r["kind"] == "refusal"]
    hits = sum(1 for r in results if r["hit"])

    summary = {
        "n": len(results),
        f"hit_rate_at_{k}": round(hits / len(results), 4),
        "max_distance": MAX_DISTANCE,
        "results": results,
        "misses": [r for r in results if not r["hit"]],
    }
    if retrieval:
        summary["retrieval_hit_rate"] = round(
            sum(1 for r in retrieval if r["hit"]) / len(retrieval), 4
        )
        summary["video_hit_rate"] = round(
            sum(1 for r in retrieval if r["video_hit"]) / len(retrieval), 4
        )
    if refusal:
        summary["refusal_rate"] = round(sum(1 for r in refusal if r["hit"]) / len(refusal), 4)

    return summary
