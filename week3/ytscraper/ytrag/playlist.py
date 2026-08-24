"""Playlist -> Video[], and Video -> a local audio file."""

from pathlib import Path

import yt_dlp

from ytrag.config import (
    AUDIO_DIR,
    COOKIES_FILE,
    COOKIES_FROM_BROWSER,
    DOWNLOAD_SLEEP_MAX,
    DOWNLOAD_SLEEP_MIN,
)
from ytrag.models import Video
from ytrag.util import with_retry

# YouTube's way of saying "you are downloading too fast". Not a broken video,
# not a dead network — a rate limit, which needs a long pause rather than the
# usual few-second backoff.
_BOT_MARKERS = ("not a bot", "sign in to confirm", "too many requests", "http error 429")


def _is_bot_challenge(exc: Exception) -> bool:
    return any(marker in str(exc).lower() for marker in _BOT_MARKERS)


def _cookie_opts() -> dict:
    """Cookies, if configured. A cookies.txt file wins over browser extraction.

    Browser extraction only really works for Firefox on Windows — Chrome and
    Edge encrypt their cookie stores with App-Bound Encryption, which yt-dlp
    cannot decrypt. Hence the file option.
    """
    if COOKIES_FILE:
        return {"cookiefile": COOKIES_FILE}
    if COOKIES_FROM_BROWSER:
        return {"cookiesfrombrowser": (COOKIES_FROM_BROWSER,)}
    return {}

# yt-dlp writes progress and warnings straight to stdout, which shreds a rich
# progress bar. Silence it; we report progress ourselves.
_QUIET = {"quiet": True, "no_warnings": True, "noprogress": True}


def list_playlist(playlist_url: str) -> list[Video]:
    """List every video in a playlist in a single request.

    `extract_flat` is deliberate: without it yt-dlp resolves each video
    individually, so a 40-video playlist becomes 40 round trips.
    """
    opts = {**_QUIET, "extract_flat": "in_playlist", "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    entries = info.get("entries") or [info]
    return [
        Video(
            video_id=e["id"],
            title=e.get("title") or e["id"],
            duration=int(e.get("duration") or 0),
        )
        for e in entries
        if e and e.get("id")
    ]


def find_audio(video_id: str) -> Path | None:
    """Return an already-downloaded audio file for this video, if any."""
    for path in sorted(AUDIO_DIR.glob(f"{video_id}.*")):
        if path.suffix not in {".part", ".ytdl", ".tmp"}:
            return path
    return None


def download_audio(video: Video, force: bool = False) -> Path:
    """Download bestaudio to ~/.ytrag/audio/<video_id>.<ext>.

    Note there is no ffmpeg postprocessing step here. faster-whisper decodes
    audio itself through PyAV (which bundles its own FFmpeg libraries), so it
    reads the raw m4a/webm directly. That removes the ffmpeg install, and it
    removes the 16kHz WAVs — which run ~115 MB per hour of video and will
    quietly eat 40-50 GB across a full playlist.
    """
    existing = find_audio(video.video_id)
    if existing and not force:
        return existing

    opts = {
        **_QUIET,
        "format": "bestaudio/best",
        "outtmpl": str(AUDIO_DIR / f"{video.video_id}.%(ext)s"),
        "overwrites": True,  # a retry must replace the partial file, not skip it
        # Pace ourselves. Downloading 127 videos back to back is exactly the
        # pattern YouTube's bot detection looks for.
        "sleep_interval": DOWNLOAD_SLEEP_MIN,
        "max_sleep_interval": DOWNLOAD_SLEEP_MAX,
        # Rotating the client avoids the web client's stricter bot checks.
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }
    opts.update(_cookie_opts())

    def _download():
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([video.url])

    # Retried because this is the step that fails when the wifi drops, or when
    # YouTube decides we look like a bot, in the middle of a long run.
    # Deliberately patient on rate limits: 10, 20, 30 ... minutes, roughly five
    # hours of waiting in total. An IP block typically clears in well under
    # that, so an overnight run rides it out instead of dying at 3am.
    with_retry(
        _download,
        attempts=8,
        label=f"download {video.video_id}",
        is_rate_limit=_is_bot_challenge,
        rate_limit_delay=600,
    )

    path = find_audio(video.video_id)
    if path is None:
        raise RuntimeError(f"yt-dlp reported success but no audio file for {video.video_id}")
    return path


def delete_audio(video_id: str) -> None:
    """Drop the audio once a transcript exists. It is fully regenerable."""
    for path in AUDIO_DIR.glob(f"{video_id}.*"):
        path.unlink(missing_ok=True)
