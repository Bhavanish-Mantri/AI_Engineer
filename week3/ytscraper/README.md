# YT Lecture RAG

A Retrieval-Augmented Generation (RAG) system for searching and revising YouTube lecture playlists.

Instead of returning only a text answer, the system retrieves the relevant lecture segments and provides **video titles and timestamps**, allowing the user to jump directly to where the topic was explained.

## Example

```text
Query:
"memoization aur tabulation ka difference kya hai?"

Answer:
A short answer based only on the retrieved lecture content.

Sources:
[1] DP Lecture 3 @ 12:04
[2] DP Lecture 5 @ 04:31
```

The main idea is:

```text
YouTube Playlist
       ↓
Download Audio
       ↓
Transcription
       ↓
Time-based Chunking
       ↓
Embeddings
       ↓
Qdrant Cloud
       ↓
Semantic Retrieval
       ↓
      LLM
       ↓
Answer + Video Timestamps
```

## Features
* Retrieves information from YouTube lecture playlists
* Supports questions in English and Hinglish
* Downloads lecture audio using yt-dlp
* Transcribes lectures using faster-whisper
* Preserves timestamps during transcription and chunking
* Uses semantic embeddings for retrieval
* Stores embeddings in Qdrant Cloud
* Generates grounded answers using Groq
* Provides clickable citations that jump to the relevant point in the YouTube video
* Includes CLI commands for ingestion, search, evaluation, and serving the web UI
* Caches transcripts so expensive transcription does not need to be repeated
* Supports re-indexing without downloading and transcribing videos again

## Tech Stack
| Component | Technology |
| :--- | :--- |
| Video / Audio | yt-dlp |
| Transcription | faster-whisper (large-v3) |
| Chunking | Time-based custom chunking |
| Embeddings | sentence-transformers + BAAI/bge-m3 |
| Vector Database | Qdrant Cloud |
| LLM | Groq openai/gpt-oss-120b |
| CLI | Typer + Rich |
| API | FastAPI |
| Video Integration | YouTube IFrame API |
| Package Manager | UV |

## Project Workflow

### 1. Download Lecture Audio

The playlist is processed using yt-dlp. Only the audio is required for transcription.

```text
YouTube Playlist
      ↓
    yt-dlp
      ↓
    Audio
```

### 2. Transcription

The downloaded audio is transcribed using faster-whisper.

```text
Audio
  ↓
faster-whisper
  ↓
Timestamped Transcript
```

The timestamps are important because they are later used to generate links that point to the exact location in the lecture.

### 3. Time-Based Chunking

The transcript is divided into time-based chunks.

The default configuration uses:
* **Chunk Size:** 75 seconds
* **Overlap:** 15 seconds

The system keeps the timestamp information with each chunk instead of using a generic text splitter.

```text
Lecture
   ↓
00:00 - 01:15
01:00 - 02:15
02:00 - 03:15
...
```

### 4. Generate Embeddings

Each chunk is converted into a vector using:
* **BAAI/bge-m3**

The resulting embeddings are stored in Qdrant Cloud together with the original text and metadata such as the video ID and timestamp.

```text
Text Chunk
    ↓
Embedding Model
    ↓
Vector
    ↓
Qdrant
```

### 5. Retrieve Relevant Chunks

When a user asks a question:

```text
User Query
    ↓
Query Embedding
    ↓
Qdrant Similarity Search
    ↓
Top Relevant Chunks
```

The retrieved chunks contain the information required to answer the question as well as the lecture and timestamp information.

### 6. Generate the Answer

The retrieved context is provided to the Groq LLM.

The system is designed to answer using the retrieved lecture content rather than relying on the model's general knowledge.

```text
Retrieved Context
       +
User Question
       ↓
Groq LLM
       ↓
Grounded Answer
       +
Lecture Citations
```

### 7. Timestamped Citations

The most important feature of this project is that citations point to the relevant location in the lecture.

```text
Answer
  ↓
Source
  ↓
Video ID + Timestamp
  ↓
YouTube Player
  ↓
Exact Lecture Segment
```

The web interface uses the YouTube IFrame API so clicking a citation can seek directly inside the embedded video.

## Setup

### Requirements
* Python 3.11
* UV
* Qdrant Cloud
* Groq API key
* NVIDIA GPU recommended for transcription

Install the project:

```bash
cd week3/ytscraper
uv venv --python 3.11
uv sync
```

For CUDA support on Windows:

```bash
uv sync --extra cuda
```

The project can fall back to CPU transcription if CUDA is unavailable, although transcription will be significantly slower.

### Environment Variables

Create or configure the required environment variables:

```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## Usage

### 1. Preflight Check

Before starting a long ingestion process:

```bash
uv run ytrag preflight --playlist "<PLAYLIST_URL>"
```

This checks the required services, models, playlist access, and configuration.

### 2. Test Transcription Language

```bash
uv run ytrag langtest "https://www.youtube.com/watch?v=<VIDEO_ID>"
```

This can be used to determine whether Hindi or English transcription provides better results for the lecture content.

### 3. Ingest a Playlist

Test the complete pipeline with one video first:

```bash
uv run ytrag ingest --playlist "<PLAYLIST_URL>" --limit 1
```

Process the complete playlist:

```bash
uv run ytrag ingest --playlist "<PLAYLIST_URL>"
```

The ingestion pipeline performs:

```text
Download Audio
     ↓
Transcribe
     ↓
Cache Transcript
     ↓
Chunk Transcript
     ↓
Generate Embeddings
     ↓
Upsert into Qdrant
```

Completed transcripts are cached, so running the command again does not unnecessarily re-transcribe completed videos.

### 4. Ask Questions

```bash
uv run ytrag ask "memoization aur tabulation ka difference kya hai?"
```

### 5. Search Without Generation

To inspect the retrieval results directly:

```bash
uv run ytrag search "adjacency list"
```

### 6. Evaluate the System

```bash
uv run ytrag eval --verbose
```

### 7. Start the Web Interface

```bash
uv run ytrag serve
```

Open:

```text
http://127.0.0.1:8000
```

The web interface allows users to ask questions and open the retrieved lecture directly at the relevant timestamp.

### Runtime Data

Runtime files are stored outside the repository:

```text
~/.ytrag/
├── audio/
├── transcripts/
└── langtest/
```

Transcripts are the most valuable generated artifact because transcription is the most expensive step. Audio files can be deleted after transcription and the downstream pipeline can be rebuilt from cached transcripts.

### Re-indexing

Because transcripts are cached, the vector index can be rebuilt without downloading or transcribing the videos again.

```bash
uv run ytrag reindex
```

To replace the existing collection:

```bash
uv run ytrag reindex --replace
```

Other useful commands:

```bash
uv run ytrag stats
uv run ytrag clean-audio
```

## Grounding and Refusal

The system is designed to avoid answering questions that are outside the knowledge contained in the lecture playlist.

A similarity threshold is used to filter weak retrieval results:

```text
User Query
    ↓
Qdrant Search
    ↓
Similarity Threshold
    ↓
Relevant Context?
   /        \
 Yes        No
  ↓          ↓
LLM       Refuse
  ↓
Answer
```

If no relevant context survives the threshold, the system can refuse to answer instead of generating an unsupported response.

This is important because an LLM may already know the answer to a general question, but the purpose of this application is to answer based on the indexed lecture content.

## Configuration

Important environment variables include:

| Variable | Default | Description |
| :--- | :--- | :--- |
| YTRAG_WHISPER_LANG | en | Whisper transcription language |
| YTRAG_WHISPER_MODEL | large-v3 | Whisper model |
| YTRAG_WHISPER_DEVICE | auto | Transcription device |
| YTRAG_WHISPER_BATCH | 8 | Whisper batch size |
| YTRAG_WHISPER_BEAM | 5 | Whisper beam size |
| YTRAG_CHUNK_SECONDS | 75 | Chunk duration |
| YTRAG_CHUNK_OVERLAP | 15 | Chunk overlap |
| YTRAG_EMBED_MODEL | BAAI/bge-m3 | Embedding model |
| YTRAG_COLLECTION | dsa_lectures | Qdrant collection |
| YTRAG_TOP_K | 6 | Number of retrieved chunks |
| YTRAG_MAX_DISTANCE | 0.5 | Retrieval grounding threshold |
| YTRAG_LLM_MODEL | openai/gpt-oss-120b | Groq model |

## Key Learnings

* Building a RAG system over video content
* Extracting audio from YouTube playlists
* Using Whisper for local transcription
* Preserving timestamps throughout the RAG pipeline
* Time-based document chunking
* Generating semantic embeddings
* Storing embeddings in Qdrant Cloud
* Performing semantic retrieval
* Grounding LLM responses using retrieved context
* Generating timestamp-based video citations
* Building a CLI and web interface around a RAG pipeline
* Designing a pipeline that can resume after failures
* Separating expensive transcription from cheaper indexing and retrieval

## Summary

This project extends the RAG concepts learned earlier by applying them to YouTube lecture content.

Instead of asking:
> "What information is in my documents?"

the system answers:
> "Where in the lectures was this explained?"

The complete pipeline is:

```text
YouTube Playlist
      ↓
yt-dlp
      ↓
Audio
      ↓
faster-whisper
      ↓
Timestamped Transcript
      ↓
75-Second Chunks
      ↓
BGE-M3 Embeddings
      ↓
Qdrant Cloud
      ↓
Semantic Retrieval
      ↓
Groq LLM
      ↓
Grounded Answer
      ↓
Clickable Video Timestamp
```

The result is a RAG system that not only answers questions from the lecture material but also helps the user quickly return to the exact part of the video where the concept was explained.
