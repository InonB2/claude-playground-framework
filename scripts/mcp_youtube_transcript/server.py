#!/usr/bin/env python3
"""YouTube Transcript MCP Server — fetches auto-generated or manual transcripts from YouTube."""

import re
from fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

_api = YouTubeTranscriptApi()

mcp = FastMCP(
    name="youtube-transcript",
    instructions="Use get_youtube_transcript to fetch the full text transcript of any YouTube video by its URL or video ID.",
)


def _extract_video_id(url_or_id: str) -> str:
    """Parse a YouTube URL or bare video ID and return the 11-char video ID."""
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a video ID from: {url_or_id}")


@mcp.tool()
def get_youtube_transcript(video_url_or_id: str, language: str = "en") -> str:
    """
    Fetch the full transcript of a YouTube video.

    Args:
        video_url_or_id: A YouTube URL (any format) or a bare 11-character video ID.
        language: BCP-47 language code, e.g. 'en', 'he', 'es'. Defaults to 'en'.
                  Falls back to any available language if the requested one is missing.

    Returns:
        The complete transcript as plain text, or an error message.
    """
    try:
        video_id = _extract_video_id(video_url_or_id)
    except ValueError as e:
        return f"ERROR: {e}"

    try:
        fetched = _api.fetch(video_id, languages=[language, "en"])
        entries = list(fetched)
        text = " ".join(entry.text for entry in entries)
        return f"[Transcript for video {video_id} — {len(entries)} segments]\n\n{text}"

    except TranscriptsDisabled:
        return f"ERROR: Transcripts are disabled for video {video_id}."
    except VideoUnavailable:
        return f"ERROR: Video {video_id} is unavailable or private."
    except Exception as e:
        return f"ERROR fetching transcript for {video_id}: {type(e).__name__}: {e}"


@mcp.tool()
def list_available_languages(video_url_or_id: str) -> str:
    """
    List all available transcript languages for a YouTube video.

    Args:
        video_url_or_id: A YouTube URL or bare video ID.

    Returns:
        A list of available language codes and names.
    """
    try:
        video_id = _extract_video_id(video_url_or_id)
    except ValueError as e:
        return f"ERROR: {e}"

    try:
        transcript_list = _api.list(video_id)
        lines = [f"Available transcripts for video {video_id}:"]
        for t in transcript_list:
            kind = "auto-generated" if t.is_generated else "manual"
            lines.append(f"  [{t.language_code}] {t.language} ({kind})")
        return "\n".join(lines)
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


if __name__ == "__main__":
    mcp.run()
