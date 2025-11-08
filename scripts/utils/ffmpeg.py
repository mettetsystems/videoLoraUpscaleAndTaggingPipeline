# -*- coding: utf-8 -*-
"""
Thin wrapper around ffmpeg to keep other scripts clean and readable.

- We shell out to ffmpeg (more portable/reliable on Windows).
- Normalization uses lanczos scaling and strips audio (video-only training).
"""

from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Tuple

def run_ffmpeg(args: list[str]) -> None:
    """Run ffmpeg with provided arguments, surfacing errors if any."""
    subprocess.run(args, check=True)

def norm_video(
    ffmpeg_bin: str,
    src: Path,
    dst: Path,
    *, size: Tuple[int, int],
    fps: int,
    pix_fmt: str,
    crf: int,
    preset: str,
) -> None:
    """Normalize a single video into target size/fps/pix_fmt using H.264 visually-lossless settings."""
    w, h = size
    args = [
        ffmpeg_bin, "-y",
        "-i", str(src),
        "-vf", f"scale={w}:{h}:flags=lanczos,fps={fps}",
        "-pix_fmt", pix_fmt,
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-an",
        str(dst)
    ]
    run_ffmpeg(args)

def extract_frames(
    ffmpeg_bin: str,
    src: Path,
    dst_dir: Path,
    *, fps: int,
    jpeg_q: int
) -> None:
    """Extract frames as JPEGs (post-normalization)."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    # We already normalized FPS, so just dump frames.
    args = [
        ffmpeg_bin, "-y",
        "-i", str(src),
        "-qscale:v", str(max(2, 31 - int(jpeg_q/3))),
        str(dst_dir / "frame_%06d.jpg")
    ]
    run_ffmpeg(args)
