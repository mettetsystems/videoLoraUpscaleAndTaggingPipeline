# -*- coding: utf-8 -*-
"""
Extract frames from normalized videos for downstream tagging.

- Uses JPEG with adjustable quality (config.frame_extract.jpeg_q).
- Keeps the per-video folder structure (frames/<video_stem>/frame_XXXXXX.jpg).
"""

from pathlib import Path
from scripts.utils.paths import load_config, paths
from scripts.utils.ffmpeg import extract_frames

def main():
    cfg = load_config()
    p = paths(cfg)
    ff = cfg["paths"]["ffmpeg_bin"]
    fps = int(cfg["video_norm"]["fps"])
    jpeg_q = int(cfg["frame_extract"]["jpeg_q"])

    for vid in Path(p["normalized_videos"]).glob("*.mp4"):
        out_dir = p["frames_root"] / vid.stem
        print(f"[frames] {vid.name} -> {out_dir}")
        extract_frames(ff, vid, out_dir, fps=fps, jpeg_q=jpeg_q)

if __name__ == "__main__":
    main()
