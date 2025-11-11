# scripts/08_split_review.py
"""
Purpose
-------
Pre-split raw review videos into short clips (<= clip_max_seconds) BEFORE upscaling.
Why? Small, uniform clips improve dataset balance, reduce motion blur carryover,
and make downstream tagging more consistent.

What it does
------------
- Walks data/input_videos (your symlink to the review folder).
- For each input video, creates data/clips_5s/<video-basename>/clip_0001.mp4, etc.
- Default: re-encode and *force keyframes* on a 5s cadence so every segment
  cuts cleanly. This avoids the classic '-c copy' non-keyframe split corruption.
- You may switch to "fast_copy: true" in config.yaml to use stream copy if you prefer.

Config (config.yaml)
--------------------
paths:
  input_videos_dir: data/input_videos
  split_clips_dir:  data/clips_5s

video:
  clip_max_seconds: 5
  split_fast_copy: false   # true = faster, copy stream; false = re-encode with keyframes forced

Usage
-----
(.venv) > python scripts/08_split_review.py
"""
import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG  = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))

IN_DIR  = ROOT / CFG["paths"].get("input_videos_dir", "data/input_videos")
OUT_DIR = ROOT / CFG["paths"].get("split_clips_dir",  "data/clips_5s")

MAX_SEC       = int(CFG.get("video", {}).get("clip_max_seconds", 5))
FAST_COPY     = bool(CFG.get("video", {}).get("split_fast_copy", False))

# Ensure output root exists
OUT_DIR.mkdir(parents=True, exist_ok=True)

def split_video(src: Path, dst_dir: Path) -> None:
    """
    Split 'src' into <= MAX_SEC segments inside 'dst_dir'.
    - If FAST_COPY: stream copy (no re-encode). Faster, but segments may start only at keyframes.
    - Else: Re-encode H.264, force keyframes every MAX_SEC seconds for clean, deterministic segments.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    out_pattern = str(dst_dir / "clip_%04d.mp4")

    if FAST_COPY:
        # Fast path: copy streams and segment at keyframes (may not align exactly on MAX_SEC).
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(src),
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", str(MAX_SEC),
            "-reset_timestamps", "1",
            out_pattern,
        ]
    else:
        # Safer path: re-encode and *force* keyframes on the cadence so all segments are cleanly cut.
        # -crf 18 gives visually lossless-ish mezzanine; adjust if you need smaller intermediates.
        # -sc_threshold 0 prevents scene-change keyframe bursts from breaking cadence.
        # -force_key_frames uses an expression to ensure keyframes every MAX_SEC.
        gop = max(1, int(MAX_SEC * 16))  # match your pipeline's 16 FPS; adjust if you change fps later
        force_kf = f"expr:gte(t,n_forced*{MAX_SEC})"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(src),
            "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-g", str(gop), "-keyint_min", str(gop), "-sc_threshold", "0",
            "-force_key_frames", force_kf,
            "-f", "segment", "-segment_time", str(MAX_SEC),
            "-reset_timestamps", "1",
            "-movflags", "+faststart",
            out_pattern,
        ]

    subprocess.run(cmd, check=True)

def main() -> int:
    if not IN_DIR.exists():
        print(f"[split] Input folder not found: {IN_DIR}", file=sys.stderr)
        return 2

    videos = [p for p in IN_DIR.iterdir() if p.is_file()]
    if not videos:
        print(f"[split] No files in {IN_DIR}")
        return 0

    for src in videos:
        base = src.stem
        dst  = OUT_DIR / base
        print(f"[split] {src.name} → {dst}")
        split_video(src, dst)

    print("[split] Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
