# YT Lecture RAG

Retrieval over a YouTube DSA playlist. A student asks a question in Hinglish or English and
gets an answer **plus clickable links that jump to the exact second in the exact lecture**.

```
"bhai memoization aur tabulation ka difference kahan explain kiya hai?"

→ Answer: 3-4 lines, grounded only in what was actually said
→ Sources:
   [1] DP Lecture 3 — Memoization Deep Dive        @ 12:04   ▸ jump
   [2] DP Lecture 5 — Tabulation Recipe            @ 04:31   ▸ jump
```

Every generic RAG demo returns a blob of text. This returns *a place in a video*.

---

## Stack

| Layer | Choice |
|---|---|
| Playlist + audio | `yt-dlp` (Python API) |
| Transcription | `faster-whisper` (CTranslate2), `large-v3`, batched |
| Chunking | hand-written, time-window based |
| Embeddings | `sentence-transformers` + `BAAI/bge-m3` (1024-dim) |
| Vector store | **Qdrant Cloud** — same as day14 / day15 |
| LLM | **Groq** `openai/gpt-oss-120b` — same as day15 / hiremeai |
| CLI | `typer` + `rich` |
| API + UI | `FastAPI` + a single HTML page with the YouTube IFrame API |

### Where this differs from `RAGPLAN.md`

The plan was written for an Apple Silicon machine with a Gemini key. Three swaps, all
deliberate:

- **`faster-whisper`, not `mlx-whisper`.** `mlx` is Apple-Silicon-only. On this box the CUDA
  path is the faster one anyway — and batched, it is 3x faster than the sequential config
  the plan assumed, at no cost in quality.
- **No `ffmpeg`, no WAV files.** `faster-whisper` decodes audio itself through PyAV, so
  `yt-dlp` downloads the raw m4a and Whisper reads it directly. That removes an install, and
  it removes the 16kHz WAVs that run ~115 MB per hour of video.
- **Qdrant + Groq, not Chroma + Gemini.** Matches the rest of week 3, and the keys are
  already in the repo-root `.env`. Qdrant Cloud also makes Phase 4 deploy trivial — the index
  is already remote, so there is no disk volume to persist.

---

## Setup

```bash
cd week3/ytscraper
uv venv --python 3.11
uv sync
```

The CUDA runtime libs that `ctranslate2` needs on Windows are an optional extra:

```bash
uv sync --extra cuda
```

If your GPU is newer than the shipped `ctranslate2` build, `transcribe.py` catches the
failure and falls back to CPU `int8` with a printed warning. Slower, still correct.

**Embeddings run on CPU by default.** `uv` pulls the CPU build of torch from PyPI, so bge-m3
embeds on the CPU — fine for querying, and a few minutes rather than seconds when reindexing
a full playlist. To put it on the GPU (~3GB download):

```bash
uv pip install torch --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

Transcription is unaffected either way: `ctranslate2` ships its own CUDA support and already
uses the GPU.

Keys come from the repo-root `.env` (already present):

```
GROQ_API_KEY=...
QDRANT_URL=...
QDRANT_API_KEY=...
```

---

## Runtime data

Lives outside the repo, in `~/.ytrag/`:

```
~/.ytrag/
├── audio/        # <video_id>.m4a — DELETABLE, regenerable in seconds
├── transcripts/  # <video_id>.json — PRECIOUS, hours of GPU time
└── langtest/     # output of `ytrag langtest`
```

That split is the whole point. Transcripts are the expensive artifact; everything downstream
of them is cheap to rebuild, which is why changing your mind about the embedding model or
the chunk size later costs minutes instead of hours.

---

## Usage

### 0a. Preflight

```bash
uv run ytrag preflight --playlist "<PLAYLIST_URL>"
```

Checks keys, Qdrant, the embedder, the Whisper model, the transcription code
path, playlist listing and the LLM — about a minute. Each check *calls* the
thing rather than asserting it looks importable, because this exists after an
8-hour run died ten seconds in on a missing import. Run it before any long
ingest.

### 0b. Decide the language flag first

```bash
uv run ytrag langtest "https://www.youtube.com/watch?v=<one_lecture>"
```

The lectures are Hinglish. `language="hi"` gives Devanagari output; `language="en"` gives
romanised/translated output. Student queries will be romanised Hinglish or English, so these
two produce *very* different retrieval behaviour.

Read a few minutes of each and check what happens to the technical terms specifically —
memoization, adjacency list, time complexity, subproblem, DP table. Whichever keeps those
clean, wins. Then set `YTRAG_WHISPER_LANG` and move on. This decision gets baked into hours
of compute afterwards, so make it on evidence.

### 1. Ingest

```bash
uv run ytrag ingest --playlist "<PLAYLIST_URL>" --limit 1     # Phase 0: one video, end to end
uv run ytrag ingest --playlist "<PLAYLIST_URL>"               # Phase 1: the whole thing
```

Per video: download audio → transcribe (cached) → delete audio → chunk → upsert. One failing
video logs and the run continues. Re-running re-transcribes nothing and duplicates nothing.

#### Speed, measured on an RTX 5050 laptop

Transcription is the only expensive step, and it is paid exactly once — chunking,
embedding and indexing take seconds, and everything downstream rebuilds from cached
transcripts.

| config | speed | 68.7-hour playlist |
|---|---|---|
| `large-v3` sequential, beam 5 (as RAGPLAN specified) | 2.5x realtime | ~27 h |
| `large-v3` **batch 8**, beam 5 — the default here | **8.1x** | **~8.5 h** |
| `large-v3` batch 8, beam 1 | 10.5x | ~6.5 h |

Batching is not a quality tradeoff: same model, same weights, identical technical-term
capture in testing. The sequential path simply leaves the GPU idle between speech
regions. Beam 1 is a real further gain but uses greedy decoding, which is likeliest to
slip on exactly the thing that matters here — an unusual technical term in accented
speech — so the default stays at beam 5.

#### Surviving a long unattended run

Everything is built to be re-run. The command never changes:

```bash
uv run ytrag ingest --playlist "<PLAYLIST_URL>"
```

- **Power cut.** Transcripts are written to a temp file and atomically renamed, so you
  get a complete file or none — never a truncated one the cache then trusts forever.
  Re-run and every finished video is skipped; you lose only the one in flight.
- **Network drop.** Downloads and Qdrant upserts retry four times with exponential
  backoff, so a brief blip costs seconds. Both operations are idempotent, so a retry
  after a partial success is harmless.
- **Network death.** After `--stop-after-failures` videos fail back to back (default 5)
  the run aborts with a clear message instead of ripping through the rest of the
  playlist failing instantly and reporting a "finished" run that did nothing.
- **Ctrl-C.** Caught explicitly; cached work is safe.
- Whisper and the embedding model are cached on disk after first use, so transcription
  itself needs no network at all.

Don't let the machine sleep mid-run — power loss is survivable, suspending the GPU
mid-inference is messier.

### 2. Ask

```bash
uv run ytrag ask "memoization aur tabulation ka difference kya hai?"
uv run ytrag search "adjacency list"      # retrieval only, shows raw distances
```

### 3. Evaluate

```bash
uv run ytrag eval --verbose
```

### 4. Web UI

```bash
uv run ytrag serve
```

Then <http://127.0.0.1:8000>. Citations call `player.seekTo()` on the embedded player, so
clicking `[2]` jumps *inside the page* rather than opening a tab.

### Other commands

```bash
uv run ytrag preflight            # check every dependency before a long run
uv run ytrag reindex              # re-chunk + re-embed from cached transcripts
uv run ytrag reindex --replace    # same, but clear old chunks first (needed if chunk size changed)
uv run ytrag stats
uv run ytrag clean-audio
```

---

## Sharing this with students

Students should **never transcribe**. That step needs a decent GPU and ~8.5 hours; on a
typical laptop CPU it would be days. But its output is just text — about **1.4 KB per minute
of video**, so this entire 68.7-hour playlist ships as ~6 MB of JSON (1.5 MB zipped).

So the expensive artifact gets committed to the repo, and everyone else skips straight past
the expensive half.

```bash
uv run ytrag export-transcripts     # copy ~/.ytrag/transcripts -> ./transcripts
git add transcripts && git commit
```

Three ways someone can then use it:

**1. Just use it — zero install.** Point them at the deployed URL. No Python, no keys, no
downloads. This is the right answer for almost everyone.

**2. Run it locally.** Clone, add a free Groq key and a free Qdrant cluster, then:

```bash
uv sync
YTRAG_EMBED_MODEL=all-MiniLM-L6-v2 uv run ytrag reindex
uv run ytrag ask "memoization kya hota hai?"
```

`reindex` finds the bundled `transcripts/` automatically. Takes a few minutes on a laptop
CPU — no GPU, no audio downloads, no yt-dlp. Use `all-MiniLM-L6-v2` (90 MB) rather than the
default bge-m3 (2.2 GB): retrieval on Hinglish is somewhat worse, but it runs comfortably on
any machine. Their index costs ~7 MB in a free Qdrant tier.

**3. Point it at their own playlist.** The full pipeline, on whatever content they have.
That's the version that needs a GPU — and their own playlist is probably a lot shorter than
68 hours.

The split that makes this work is the same one that makes re-tuning cheap locally:
transcripts are precious and portable, everything downstream is disposable.

## Configuration

Everything is env-driven; defaults live in [ytrag/config.py](ytrag/config.py).

| Variable | Default | Notes |
|---|---|---|
| `YTRAG_WHISPER_LANG` | `en` | Decide this with `langtest` first |
| `YTRAG_WHISPER_MODEL` | `large-v3` | `medium` if you're impatient |
| `YTRAG_WHISPER_DEVICE` | `auto` | `cuda` / `cpu` to force |
| `YTRAG_WHISPER_BATCH` | `8` | Batched inference — see below. `0` disables |
| `YTRAG_WHISPER_BEAM` | `5` | `1` is ~30% faster, greedy decoding |
| `YTRAG_CHUNK_SECONDS` | `75` | ~one explained idea |
| `YTRAG_CHUNK_OVERLAP` | `15` | |
| `YTRAG_EMBED_MODEL` | `BAAI/bge-m3` | `all-MiniLM-L6-v2` for a small deploy tier |
| `YTRAG_COLLECTION` | `dsa_lectures` | the embedding dim gets appended |
| `YTRAG_TOP_K` | `6` | |
| `YTRAG_MAX_DISTANCE` | `0.5` | the grounding cutoff — see below, and re-tune |
| `YTRAG_LLM_MODEL` | `openai/gpt-oss-120b` | |

---

## The golden set

[eval/golden.json](eval/golden.json) holds two kinds of entry.

**Retrieval** — a hit means the expected video appears in top-k *and* at least one returned
chunk overlaps `expect_around_sec ± tolerance_sec`:

```json
{"q": "memoization vs tabulation kya difference hai?",
 "expect_video_id": "abc123", "expect_around_sec": 724, "tolerance_sec": 120}
```

**Refusal** — a hit means the pipeline declines to answer:

```json
{"q": "React hooks kaise kaam karte hain?", "expect_refusal": true}
```

The refusal entries ship working; the retrieval entries are templates you fill in with your
own video IDs (entries whose `q` starts with `_` are skipped). Writing 15-20 real ones takes
about half an hour and is the only way to tell whether a change improved retrieval or just
felt better on the one query you kept re-testing.

### Tuning `MAX_DISTANCE`

`RAGPLAN.md` suggests `0.75`. Measured against bge-m3 on Hinglish DSA text, that value
**never fires** — the guard is silently off. bge-m3 compresses its distances:

```
ON   memoization aur tabulation me kya difference hai?   0.465
ON   bfs kaise kaam karta hai                            0.379
ON   adjacency list kya hoti hai                         0.353
OFF  Kubernetes me pod aur deployment ka difference?     0.523
OFF  React hooks kaise kaam karte hain?                  0.549
OFF  How do I file my income tax return in India?        0.622
OFF  what is the capital of France                       0.711
```

So the default here is `0.5`, which sits in the separating band. Treat it as a starting
point: on a full index an off-topic query has thousands more chunks to find a spuriously
close match among, so that off-topic floor drifts downwards. Run `ytrag search` on a few
real questions, read the distances, and re-tune with `ytrag eval`.

Note what happened in testing with the loose value: the distance guard let all six chunks
through on "React hooks kaise kaam karte hain?", and the *model's own* refusal is what saved
the answer. That works, but it is one guard doing the job of two, and it costs an LLM call
every time. The cutoff is the cheap guard — keep it armed.

---

## The failure modes this codebase is built around

**Don't use a generic text splitter.** `RecursiveCharacterTextSplitter` operates on one
concatenated string and throws the timestamps away. The timestamp *is* the product here, so
[ytrag/chunk.py](ytrag/chunk.py) chunks on the segment list, in the time domain, and never
splits a segment.

**Whisper loop hallucinations.** On silence or a music sting Whisper repeats the previous
phrase forever. `condition_on_previous_text=False` and `vad_filter=True` cut most of it;
`is_repetitive()` in `chunk.py` drops what survives. These chunks are retrieval poison — they
match everything and say nothing.

**The transcript cache is the most important line in the codebase.** Re-transcribing a
40-video playlist by accident costs hours. It's written atomically (temp file + `os.replace`)
so a Ctrl-C mid-write can't leave a truncated file that the cache check then trusts forever.

**The timestamp should land slightly early.** Retrieval hits the chunk containing the answer,
but the explanation usually starts just before it. Citation URLs rewind 5 seconds
(`YTRAG_LINK_REWIND`). Small thing, noticeably better feel.

**Ungrounded answers will destroy the demo.** The model knows DSA perfectly well. Given junk
context it will answer from its own training and cheerfully attach your timestamps to it —
the student clicks and you're talking about something else. That is strictly worse than
saying "cover nahi hua". Three guards in [ytrag/answer.py](ytrag/answer.py):

1. drop everything above `MAX_DISTANCE`, and if nothing survives return the refusal
   **without calling the LLM at all**;
2. honour the model's own refusal;
3. an answer with zero citations is marked `grounded: false` and gets no links.

**Idempotency.** Cached transcripts, `upsert` not `add`, deterministic point IDs
(`uuid5` of `"{video_id}:{start_sec}"`), resume on partial failure. You *will* re-run this
many times.

---

## Deploying (Phase 4)

bge-m3 is ~2.2GB and won't fit a free tier. Because transcripts are cached, swapping is a few
minutes of embedding rather than hours of re-transcription:

```bash
YTRAG_EMBED_MODEL=all-MiniLM-L6-v2 uv run ytrag reindex
```

The dim differs (1024 vs 384), which is exactly why the collection name carries it — both
indexes coexist in the same Qdrant cluster and nothing has to be torn down.

Ship `api.main:app` to Render/Railway/Fly with the same three env vars. `/ask` is already
rate-limited (`YTRAG_RATE_LIMIT_REQUESTS` per `YTRAG_RATE_LIMIT_WINDOW` seconds, per IP) and
question length is capped at `YTRAG_MAX_QUESTION_CHARS`. The rate limiter is in-process, so
put it in Redis before running more than one worker.

---

## Definition of done (Phase 2)

- [ ] Language flag decided with evidence, not vibes
- [ ] `ingest` on the full playlist survives a video failing mid-run
- [ ] Re-running `ingest` re-transcribes nothing and duplicates nothing
- [ ] `reindex` rebuilds the vector store from cached transcripts alone
- [ ] An out-of-syllabus question returns the refusal, not a confident answer with fake timestamps
- [ ] `eval` prints a hit-rate and lists its misses
- [ ] Every citation link, clicked, lands within ~10s of the actual explanation
