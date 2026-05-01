#!/usr/bin/env python3
"""
yt_transcript.py — YouTube transcript extractor
Usage: python scripts/yt_transcript.py <youtube_url>

Primary method:  youtube-transcript-api (fast, no download)
Fallback method: yt-dlp --write-auto-sub --skip-download
Output saved to: scratchpad/transcripts/<video_id>_transcript.txt
"""

import sys
import os
import re
import subprocess
import tempfile
import glob

TRANSCRIPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scratchpad", "transcripts"
)


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from any common URL format."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_via_api(video_id: str) -> str:
    """Use youtube-transcript-api to fetch the transcript (v1.x instance API)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise RuntimeError("youtube-transcript-api is not installed. Run: pip install youtube-transcript-api")

    ytt = YouTubeTranscriptApi()

    # Try to get transcript list and find the best language match
    transcript_list = ytt.list(video_id)

    preferred_langs = ['en', 'en-US', 'en-GB', 'he', 'iw']

    transcript = None
    # Prefer manually created transcripts first
    try:
        transcript = transcript_list.find_manually_created_transcript(preferred_langs)
    except Exception:
        pass

    if transcript is None:
        try:
            transcript = transcript_list.find_generated_transcript(preferred_langs)
        except Exception:
            pass

    if transcript is None:
        # Take whatever is available first
        transcript = next(iter(transcript_list))

    fetched = transcript.fetch()
    lines = []
    for entry in fetched:
        # FetchedTranscriptSnippet object — access .text attribute
        text = entry.text if hasattr(entry, 'text') else entry.get('text', '')
        lines.append(text.strip())

    return "\n".join(lines)


def fetch_via_ytdlp(video_id: str, url: str) -> str:
    """Fallback: use yt-dlp to download auto-subs, parse the VTT file."""
    which = subprocess.run(["which", "yt-dlp"], capture_output=True, text=True)
    if which.returncode != 0:
        # Try Windows path
        which = subprocess.run(["where", "yt-dlp"], capture_output=True, text=True, shell=True)
        if which.returncode != 0:
            raise RuntimeError("yt-dlp is not installed or not on PATH.")

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "--sub-format", "vtt",
            "-o", os.path.join(tmpdir, "%(id)s.%(ext)s"),
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed:\n{result.stderr}")

        vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
        if not vtt_files:
            raise RuntimeError("yt-dlp ran but produced no VTT subtitle files.")

        vtt_path = vtt_files[0]
        with open(vtt_path, "r", encoding="utf-8") as f:
            raw = f.read()

    return parse_vtt(raw)


def parse_vtt(raw: str) -> str:
    """Parse a WebVTT subtitle file into plain text."""
    lines = raw.splitlines()
    text_lines = []
    skip_header = True
    for line in lines:
        # Skip the WEBVTT header block
        if skip_header:
            if line.strip() == "" and text_lines:
                skip_header = False
            continue
        # Skip timestamp lines (e.g. 00:00:01.000 --> 00:00:03.000)
        if re.match(r"^\d{2}:\d{2}:\d{2}", line):
            continue
        # Skip empty lines and NOTE/STYLE blocks
        if line.strip() == "" or line.startswith("NOTE") or line.startswith("STYLE"):
            continue
        # Strip inline tags like <00:00:01.500><c> </c>
        cleaned = re.sub(r"<[^>]+>", "", line).strip()
        if cleaned:
            text_lines.append(cleaned)

    # Deduplicate consecutive identical lines (common in VTT auto-captions)
    deduped = []
    for line in text_lines:
        if not deduped or deduped[-1] != line:
            deduped.append(line)

    return "\n".join(deduped)


def save_transcript(video_id: str, text: str) -> str:
    """Save transcript to the transcripts directory. Returns save path."""
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    out_path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}_transcript.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/yt_transcript.py <youtube_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[yt_transcript] Video ID: {video_id}", file=sys.stderr)

    transcript_text = None
    method_used = None

    # --- Method 1: youtube-transcript-api ---
    print("[yt_transcript] Trying youtube-transcript-api...", file=sys.stderr)
    try:
        transcript_text = fetch_via_api(video_id)
        method_used = "youtube-transcript-api"
    except Exception as e:
        print(f"[yt_transcript] youtube-transcript-api failed: {e}", file=sys.stderr)

    # --- Method 2: yt-dlp fallback ---
    if transcript_text is None:
        print("[yt_transcript] Trying yt-dlp fallback...", file=sys.stderr)
        try:
            transcript_text = fetch_via_ytdlp(video_id, url)
            method_used = "yt-dlp"
        except Exception as e:
            print(f"[yt_transcript] yt-dlp failed: {e}", file=sys.stderr)

    if transcript_text is None:
        print("ERROR: Could not retrieve transcript via any method.", file=sys.stderr)
        sys.exit(1)

    # Save to file
    save_path = save_transcript(video_id, transcript_text)
    print(f"[yt_transcript] Method used : {method_used}", file=sys.stderr)
    print(f"[yt_transcript] Saved to    : {save_path}", file=sys.stderr)
    print(f"[yt_transcript] Lines       : {len(transcript_text.splitlines())}", file=sys.stderr)
    print("---", file=sys.stderr)

    # Print transcript to stdout
    print(transcript_text)


if __name__ == "__main__":
    main()
