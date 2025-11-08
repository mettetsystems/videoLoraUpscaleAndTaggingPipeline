# -*- coding: utf-8 -*-
"""
Normalize all source videos into a consistent size/fps/pixfmt for WAN 2.1 LoRA training.

- Defaults (720p, 16 fps) are tuned for an RTX 4090 but adjustable via config.yaml.
- Produces visually high quality H.264 MP4s (CRF 15, preset 'slow'), no audio.
"""

from pathlib import Path
from scripts.utils.paths import load_config, paths
from scripts.utils.ffmpeg import norm_video

def main():
    cfg = load_config()
    p = paths(cfg)
    ff = cfg["paths"]["ffmpeg_bin"]
    target = (cfg["video_norm"]["width"], cfg["video_norm"]["height"])
    fps = int(cfg["video_norm"]["fps"])
    pix_fmt = cfg["video_norm"]["pix_fmt"]
    crf = int(cfg["video_norm"]["crf"])
    preset = cfg["video_norm"]["preset"]

    for src in Path(p["input_videos"]).glob("*.*"):
        if src.suffix.lower() not in (".mp4", ".mov", ".mkv", ".avi", ".webm"):
            continue
        dst = p["normalized_videos"] / (src.stem + "_norm.mp4")
        print(f"[normalize] {src.name} -> {dst.name}")
        norm_video(ff, src, dst, size=target, fps=fps, pix_fmt=pix_fmt, crf=crf, preset=preset)

if __name__ == "__main__":
    main()
