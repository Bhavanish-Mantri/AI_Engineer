# YT Lecture RAG — Build Spec

Paste this whole file into Claude Code as the project brief. It contains the architecture,
the exact module contracts, every non-obvious failure mode, and the phase order.

---

## 1. What we're building

A retrieval system over my own YouTube DSA playlist. A student asks a question in plain
Hinglish/English, and gets back an answer **plus clickable links that jump to the exact
second in the exact lecture where I explained it**.

```
"bhai memoization aur tabulation ka difference kahan explain kiya hai?"

→ Answer: 3-4 lines, grounded only in what I actually said
→ Sources:
   [1] DP Lecture 3 — Memoization Deep Dive        @ 12:04   ▸ jump
   [2] DP Lecture 5 — Tabulation Recipe            @ 04:31   ▸ jump
   [3] DP Lecture 5 — Tabulation Recipe            @ 21:47   ▸ jump
```

**The differentiator is timestamp-level retrieval.** Every generic RAG demo returns a blob
of text. This returns a *place in a video*. That's the product, and that's the demo moment.

Two phases: working local CLI first, then a deployed web app students can actually use.

---

## 2. Stack

| Layer | Choice | Why this one |
|---|---|---|
| Playlist + audio | `yt-dlp` (Python API, not subprocess) | Only thing that reliably survives YouTube changes |
| Audio transcode | `ffmpeg` (via yt-dlp postprocessor) | Whisper wants 16kHz mono WAV |
| Transcription | `mlx-whisper` w/ `whisper-large-v3` | Apple-Silicon-native, ~3-4x faster than openai-whisper on M4 |
| Transcription fallback | `faster-whisper` (CTranslate2) | For non-Mac / CI |
| Chunking | Custom (time-window based) | LangChain-style text splitters destroy timestamps — see §6.1 |
| Embeddings (local) | `sentence-transformers` + `BAAI/bge-m3` | Multilingual, handles code-switched Hinglish; 1024-dim |
| Embeddings (deploy) | Gemini `text-embedding-004` | 768-dim, no 2.2GB model on the server |
| Vector store | `chromadb` (PersistentClient) | Zero-setup local, metadata filtering, good enough at this scale |
| LLM | Gemini `gemini-2.0-flash` (default), Anthropic or Ollama swappable | Free tier, fast, fine for grounded summarisation |
| API (Phase 3) | `FastAPI` + `uvicorn` | |
| Frontend (Phase 3) | Single HTML page + YouTube IFrame API | `player.seekTo()` = in-page jumping, no page reload |
| CLI | `typer` + `rich` | Progress bars matter — transcription is slow and you'll be staring at it |

```
pip install yt-dlp mlx-whisper chromadb sentence-transformers \
            google-generativeai fastapi uvicorn typer rich
brew install ffmpeg
```

---

## 3. Directory layout

```
yt-rag/
├── ytrag/
│   ├── __init__.py
│   ├── config.py        # all tunables, env-driven
│   ├── playlist.py      # playlist -> Video[], Video -> audio wav
│   ├── transcribe.py    # audio -> Segment[], cached to JSON
│   ├── chunk.py         # Segment[] -> Chunk[] (time windows)
│   ├── embed.py         # pluggable embedder (local | gemini)
│   ├── index.py         # ChromaDB upsert + query
│   ├── answer.py        # retrieve -> grounded answer + citations
│   ├── evaluate.py      # golden-set retrieval hit rate
│   └── cli.py           # typer entrypoint
├── api/
│   ├── main.py          # FastAPI (Phase 3)
│   └── static/index.html
├── eval/golden.json
├── requirements.txt
└── README.md
```

Runtime data lives outside the repo, in `~/.ytrag/`:

```
~/.ytrag/
├── audio/        # <video_id>.wav — DELETABLE, regenerable
├── transcripts/  # <video_id>.json — PRECIOUS, never delete (hours of GPU time)
└── chroma/       # vector store — regenerable from transcripts in minutes
```

That split matters. Transcripts are the expensive artifact. Everything downstream of them
is cheap to rebuild, which is why changing your mind about embedding models later costs
nothing.

---

## 4. Data model

```python
@dataclass
class Video:
    video_id: str          # "dQw4w9WgXcQ"
    title: str
    duration: int          # seconds

@dataclass
class Segment:             # raw Whisper output
    start: float
    end: float
    text: str

@dataclass
class Chunk:               # what actually gets embedded
    chunk_id: str          # f"{video_id}:{int(start_sec)}"  — stable, enables upsert
    video_id: str
    video_title: str
    start_sec: int
    end_sec: int
    text: str

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}&t={self.start_sec}s"

    @property
    def timestamp(self) -> str:   # "12:04" / "1:12:04"
        ...
```

**Chroma metadata may only contain `str`, `int`, `float`, `bool`.** No `None`, no lists,
no nested dicts. It fails at insert time with an unhelpful error. Coerce everything.

---

## 5. Module contracts

### `config.py`
```python
from pathlib import Path
import os

ROOT = Path(os.getenv("YTRAG_ROOT", Path.home() / ".ytrag"))
AUDIO_DIR, TRANSCRIPT_DIR, CHROMA_DIR = ROOT/"audio", ROOT/"transcripts", ROOT/"chroma"
for d in (AUDIO_DIR, TRANSCRIPT_DIR, CHROMA_DIR):
    d.mkdir(parents=True, exist_ok=True)

WHISPER_BACKEND = os.getenv("YTRAG_WHISPER", "mlx")            # mlx | faster
WHISPER_MODEL   = os.getenv("YTRAG_WHISPER_MODEL", "mlx-community/whisper-large-v3-mlx")
WHISPER_LANG    = os.getenv("YTRAG_WHISPER_LANG", "en")        # see §6.0 — TEST THIS FIRST

CHUNK_SECONDS         = int(os.getenv("YTRAG_CHUNK_SECONDS", 75))
CHUNK_OVERLAP_SECONDS = int(os.getenv("YTRAG_CHUNK_OVERLAP", 15))

EMBED_BACKEND = os.getenv("YTRAG_EMBED", "local")              # local | gemini
EMBED_MODEL   = os.getenv("YTRAG_EMBED_MODEL", "BAAI/bge-m3")
LLM_BACKEND   = os.getenv("YTRAG_LLM", "gemini")               # gemini | anthropic | ollama
COLLECTION    = os.getenv("YTRAG_COLLECTION", "dsa_lectures")
TOP_K         = int(os.getenv("YTRAG_TOP_K", 6))
MAX_DISTANCE  = float(os.getenv("YTRAG_MAX_DISTANCE", 0.75))   # see §6.5
```

### `playlist.py`
```python
def list_playlist(playlist_url: str) -> list[Video]
def download_audio(video: Video, force: bool = False) -> Path   # -> ~/.ytrag/audio/<id>.wav
```
Reference implementation:
```python
def list_playlist(playlist_url: str) -> list[Video]:
    import yt_dlp
    opts = {"extract_flat": "in_playlist", "quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
    return [
        Video(video_id=e["id"], title=e.get("title") or e["id"],
              duration=int(e.get("duration") or 0))
        for e in (info.get("entries") or []) if e and e.get("id")
    ]

def download_audio(video: Video, force: bool = False) -> Path:
    import yt_dlp
    out = AUDIO_DIR / f"{video.video_id}.wav"
    if out.exists() and not force:
        return out
    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(AUDIO_DIR / f"{video.video_id}.%(ext)s"),
        "quiet": True, "no_warnings": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "postprocessor_args": ["-ar", "16000", "-ac", "1"],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([video.url])
    return out
```
`extract_flat` is deliberate — it lists 40 videos in one request instead of 40.

### `transcribe.py`
```python
def transcribe(video: Video, force: bool = False) -> list[Segment]
```
- **Check `TRANSCRIPT_DIR/<video_id>.json` first and return early.** This is the single most
  important line in the codebase. Re-transcribing a 40-video playlist by accident costs hours.
- Write the JSON atomically (temp file + `os.replace`), so a Ctrl-C mid-write doesn't leave
  a corrupt half-transcript that the cache check then happily trusts forever.
- Store `{"video_id", "title", "language", "model", "segments": [...]}` — record which model
  and language produced it, so you can tell later which files need redoing.
- mlx call:
  ```python
  import mlx_whisper
  r = mlx_whisper.transcribe(
      str(audio_path),
      path_or_hf_repo=WHISPER_MODEL,
      language=WHISPER_LANG,
      condition_on_previous_text=False,   # see §6.2
      verbose=False,
  )
  segments = [Segment(s["start"], s["end"], s["text"].strip()) for s in r["segments"]]
  ```
- After a successful transcript write, delete the WAV. 16kHz mono is ~115 MB/hour of video;
  a 40-lecture playlist will quietly eat 40-50 GB.

### `chunk.py`
```python
def chunk_segments(video: Video, segments: list[Segment]) -> list[Chunk]
```
Greedy time-window merge:
- Accumulate segments until `end - window_start >= CHUNK_SECONDS`, emit a Chunk.
- Start the next window at `end - CHUNK_OVERLAP_SECONDS`, backing up to the nearest
  segment boundary — **never split a segment**.
- Drop chunks with fewer than ~15 words (intros, "toh chaliye shuru karte hain").
- Prefix the chunk text with the video title before embedding:
  `f"{video.title}\n\n{body}"`. Cheap trick, meaningfully improves retrieval, because a
  chunk from minute 34 often doesn't restate what topic it's about.

### `embed.py`
```python
class Embedder(Protocol):
    dim: int
    def embed_documents(self, texts: list[str]) -> list[list[float]]
    def embed_query(self, text: str) -> list[float]

def get_embedder() -> Embedder    # dispatch on EMBED_BACKEND
```
- Local: `SentenceTransformer(EMBED_MODEL)`, `normalize_embeddings=True`, batch 32.
- bge-m3 needs **no** instruction prefix. (bge-*-en-v1.5 does — `"Represent this sentence
  for searching relevant passages: "` on the query only. If you ever switch models, check.)
- Gemini: `task_type="retrieval_document"` for chunks, `"retrieval_query"` for queries.
  Using the wrong task_type silently degrades results — no error, just worse answers.

### `index.py`
```python
def get_collection()
def upsert_chunks(chunks: list[Chunk]) -> None
def search(query: str, top_k: int = TOP_K, video_id: str | None = None) -> list[tuple[Chunk, float]]
def stats() -> dict
```
- Use `collection.upsert(...)`, not `.add(...)`. With `chunk_id` as the ID, re-ingesting is
  idempotent instead of producing duplicates.
- Name the collection to include the embedding dim: `f"{COLLECTION}_{embedder.dim}"`.
  Chroma throws a dimension-mismatch error if you switch models against the same collection;
  this sidesteps it and lets local and deploy indexes coexist.
- Upsert in batches of ~500.

### `answer.py`
```python
def answer(question: str, top_k: int = TOP_K) -> dict
# -> {"answer": str, "citations": [{"title","timestamp","url","start_sec","video_id"}], "grounded": bool}
```
Prompt shape:
```
You are answering using ONLY the transcript excerpts below, which come from
Pratyush's DSA lectures. The transcripts are auto-generated and may contain
minor errors — read past obvious mis-transcriptions of technical terms.

Rules:
- Answer only from the excerpts. If they don't cover it, say exactly:
  "Ye topic in lectures me cover nahi hua."
- Cite with [1], [2] inline.
- Match the language of the question (Hinglish question -> Hinglish answer).
- 4-6 sentences max.

EXCERPTS
[1] "DP Lecture 3" @ 12:04
<text>
[2] ...

QUESTION: <question>
```
Then map `[n]` back to the chunk to build the citation list — **only include citations the
model actually referenced**, so students don't see three links where only one is relevant.

### `evaluate.py`
```python
def run_eval(path="eval/golden.json") -> dict   # {"hit_rate_at_5": 0.87, "misses": [...]}
```
`eval/golden.json` is 15-20 hand-written entries:
```json
[{"q": "memoization vs tabulation kya difference hai?",
  "expect_video_id": "abc123", "expect_around_sec": 724, "tolerance_sec": 120}]
```
A hit = the expected video appears in top-5 **and** at least one returned chunk overlaps
`expect_around_sec ± tolerance`. This takes 30 minutes to write and is the only way to tell
whether a change actually improved retrieval or just felt better on the one query you kept
testing. It's also a real number you can put on camera.

### `cli.py`
```
ytrag ingest --playlist <URL> [--limit N] [--skip-transcribe]
ytrag ask "question"
ytrag reindex                  # re-chunk + re-embed from cached transcripts, no re-transcription
ytrag stats
ytrag eval
```
`ingest` per video: download audio → transcribe (cached) → delete wav → chunk → upsert.
Wrap it so one failing video logs and continues instead of killing a 3-hour run.

---

## 6. Failure modes — read before writing code

### 6.0 The Whisper language flag (do this first, before anything else)
The lectures are Hinglish. `language="hi"` gives Devanagari output; `language="en"` gives
romanised/translated output. These produce *very* different retrieval behaviour, because
student queries will be romanised Hinglish or English.

**Before ingesting the playlist:** transcribe ONE lecture both ways and read 2-3 minutes of
each. Check specifically what happens to technical terms — memoization, adjacency list,
time complexity, subproblem, DP table. Whichever keeps those clean, wins. My expectation is
`"en"`, but verify — this decision is baked into hours of compute afterwards.

### 6.1 Don't use a generic text splitter
`RecursiveCharacterTextSplitter` and friends operate on a concatenated string and throw
away timestamps. The timestamp *is* the product here. Chunk on the segment list, in the
time domain. This is why `chunk.py` is hand-written.

### 6.2 Whisper loop hallucinations
On silence, music stings, or long pauses Whisper repeats the previous phrase over and over.
`condition_on_previous_text=False` cuts most of it. Also post-filter: if a chunk is >60%
one repeated sentence, drop it. These chunks are retrieval poison — they match everything
and say nothing.

### 6.3 Chunk size
75s ≈ 180-220 words of speech, which is roughly one explained idea. Too small (20s) and
chunks lack context; too big (5 min) and the timestamp lands you before the relevant part
and the student has to hunt. If you tune this, re-run `eval` — don't eyeball it.

### 6.4 The timestamp should land slightly early
Retrieval hits the chunk containing the answer, but the explanation usually *starts* just
before. Subtract 5 seconds from `start_sec` when building the URL (floor at 0). Small thing,
noticeably better feel.

### 6.5 Ungrounded answers will destroy the demo
Gemini knows DSA perfectly well. If retrieval returns junk, it will answer from its own
knowledge and cheerfully attach your timestamps to it — the student clicks and you're
talking about something else. That is worse than saying "cover nahi hua".

Two guards: drop results with `distance > MAX_DISTANCE`, and if nothing survives, return the
refusal without calling the LLM at all. Tune `MAX_DISTANCE` against the golden set.

### 6.6 Idempotency
Everything must be safe to re-run. Cached transcripts, `upsert` not `add`, resume on
partial failure. You *will* re-run this many times.

### 6.7 Deploy-time embedding swap is free
bge-m3 is ~2.2GB — it won't fit a free hosting tier. For deploy set `YTRAG_EMBED=gemini`
and run `ytrag reindex`. Because transcripts are cached, that's a few minutes of embedding,
not hours of re-transcription. Dimension differs (1024 vs 768), which is exactly why the
collection name carries the dim.

---

## 7. Phase order

**Phase 0 — one video, end to end (do not skip).**
Run the language test from §6.0. Then take a single lecture all the way through:
download → transcribe → chunk → embed → ask one question → click the link and confirm it
lands on the right moment. Every architectural mistake shows up here for the price of one
video instead of forty.

**Phase 1 — full playlist ingest.** Progress bar, per-video error handling, resume support.
Write down wall-clock time per lecture-hour; you'll want that number for the video.

**Phase 2 — query CLI + golden-set eval.** `rich` output with clickable terminal links.
Get a hit-rate number.

**Phase 3 — web UI.** FastAPI `POST /ask` returning the `answer()` dict, plus a single HTML
page. Use the YouTube IFrame API so citations call `player.seekTo(start_sec, true)` and jump
*inside the embedded player* rather than opening a new tab. That in-page seek is the moment
that makes people go "wait, how".

**Phase 4 — deploy.** `YTRAG_EMBED=gemini`, `reindex`, ship to Render/Railway/Fly with the
Chroma dir persisted (or swap to hosted Qdrant if it outgrows a volume). Rate-limit `/ask`
and cap question length before it's public.

---

## 8. Definition of done (Phase 2)

- [ ] Language flag decided with evidence, not vibes
- [ ] `ingest` on the full playlist survives a video failing mid-run
- [ ] Re-running `ingest` re-transcribes nothing and duplicates nothing
- [ ] `reindex` rebuilds the vector store from cached transcripts alone
- [ ] An out-of-syllabus question ("React hooks kaise kaam karte hain?") returns the refusal,
      not a confident answer with fake timestamps
- [ ] `eval` prints a hit-rate and lists its misses
- [ ] Every citation link, clicked, lands within ~10s of the actual explanation

---

## 9. Note for later (content)

The strongest on-camera beat here isn't the RAG pipeline — everyone has seen a RAG pipeline.
It's §6.5: showing the system *refusing* to answer, and explaining why a RAG system that
never says "I don't know" is a broken RAG system. That's the part nobody demos, and it's
the part that's actually engineering.