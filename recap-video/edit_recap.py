#!/usr/bin/env python3
"""Burmese recap video editor — ffmpeg pipeline (v1).

Usage (phone -> boxes.dev box, or here):
  python3 edit_recap.py --video original.mp4 --voice voice-my.m4a \
      [--subs subs-my.srt] [--cuts cuts.txt] --out recap-my.mp4

What it does, like a human editor would:
  1. Keeps only the scenes listed in cuts.txt (one "START-END" in seconds
     per line, e.g. "0-12.5"); without cuts.txt it keeps the whole video.
  2. Drops the original audio and uses Hip's Burmese voice recording
     instead; normalises its loudness so every video sounds the same.
  3. Paces the video to the narration: by default trims the video to the
     voice length (--mode keep-video keeps the full video and pads silence).
  4. Burns Burmese subtitles into the picture when subs-my.srt is given
     (Noto Sans Myanmar, already on the box via the ffmpeg install).
  5. Fades in/out, scales to 1080p max, H.264 + AAC, faststart for upload.

Inputs Hip provides per video: original file, his Burmese voice file,
optional .srt. No AI voice in v1 — his recording is the voice.
"""
import argparse, json, subprocess, sys, os

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd), file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr)
        sys.exit(1)
    return r

def probe(path):
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path])
    return json.loads(r.stdout)

def duration(path):
    return float(probe(path)["format"]["duration"])

def parse_cuts(path):
    cuts = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a, b = line.split("-", 1)
        cuts.append((float(a), float(b)))
    return cuts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--voice", required=True)
    ap.add_argument("--subs", default=None)
    ap.add_argument("--cuts", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["trim-to-voice", "keep-video"],
                    default="trim-to-voice")
    ap.add_argument("--font", default="Noto Sans Myanmar")
    args = ap.parse_args()

    for p in (args.video, args.voice):
        if not os.path.exists(p):
            print(f"not found: {p}", file=sys.stderr); sys.exit(2)
    vdur, adur = duration(args.video), duration(args.voice)
    cuts = parse_cuts(args.cuts) if args.cuts else None
    if cuts:
        kept = sum(b - a for a, b in cuts)
        print(f"cuts: {len(cuts)} scenes, {kept:.1f}s kept of {vdur:.1f}s video")
    target = adur if args.mode == "trim-to-voice" else vdur
    if cuts:
        target = min(target, kept)
    print(f"video {vdur:.1f}s, voice {adur:.1f}s -> output {target:.1f}s ({args.mode})")

    # --- video filter: optional scene cuts, then scale + fades ---
    if cuts:
        parts, concat_in = [], ""
        for i, (a, b) in enumerate(cuts):
            parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]")
            concat_in += f"[v{i}]"
        vfilter = ";".join(parts) + f";{concat_in}concat=n={len(cuts)}:v=1:a=0,scale=1920:1080:force_original_aspect_ratio=decrease,format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st={max(target-0.5,0)}:d=0.5[vout]"
    else:
        vfilter = (f"[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
                   f"format=yuv420p,fade=t=in:st=0:d=0.5,"
                   f"fade=t=out:st={max(target-0.5,0)}:d=0.5[vout]")
    if args.subs:
        if not os.path.exists(args.subs):
            print(f"not found: {args.subs}", file=sys.stderr); sys.exit(2)
        # burn subtitles after fades; escape : and ' for the filter graph
        sub = args.subs.replace("'", r"\'").replace(":", r"\:")
        style = (f"FontName={args.font},FontSize=28,PrimaryColour=&HFFFFFF&,"
                 "OutlineColour=&H80000000&,BorderStyle=1,Outline=2,"
                 "Alignment=2,MarginV=40")
        vfilter = vfilter.replace("[vout]",
            f",subtitles='{sub}':force_style='{style}'[vout]")

    # --- audio filter: loudness-normalise voice, fit to target length ---
    afilter = (f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,"
               f"atrim=0:{target},asetpts=PTS-STARTPTS[aout]"
               if args.mode == "trim-to-voice" else
               f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur={target}[aout]")

    cmd = ["ffmpeg", "-y", "-i", args.video, "-i", args.voice,
           "-filter_complex", f"{vfilter};{afilter}",
           "-map", "[vout]", "-map", "[aout]",
           "-t", str(target),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", args.out]
    run(cmd)
    info = probe(args.out)
    streams = [(s["codec_type"], s.get("codec_name")) for s in info["streams"]]
    print(f"done: {args.out}  {float(info['format']['duration']):.1f}s  {streams}")

if __name__ == "__main__":
    main()
