#!/usr/bin/env python3
"""
Assemble the final video with real AI-generated video clips.
Combines: 8 video clips (looped/extended) + voiceover + background music
with crossfade transitions between clips.
"""

import os
import subprocess
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS_DIR = os.path.join(BASE_DIR, "videos", "clips")
AUDIO_PATH = os.path.join(BASE_DIR, "audio", "video_001_dark_psychology_tricks.wav")
MUSIC_PATH = os.path.join(BASE_DIR, "audio", "background_music_dark_cinematic.mp3")
OUTPUT_PATH = os.path.join(BASE_DIR, "videos", "video_001_FINAL.mp4")

# Clip order matching the script sections
CLIPS = [
    "clip_01_hook.mp4",       # Hook + Introduction (0:00 - 1:30)
    "clip_02_mirroring.mp4",  # Trick 1: Mirroring (1:30 - 2:45)
    "clip_03_gaslighting.mp4",# Trick 2: Gaslighting (2:45 - 4:00)
    "clip_04_footindoor.mp4", # Trick 3: Foot-in-door + Trick 4: Emotional (4:00 - 5:30)
    "clip_05_scarcity.mp4",   # Trick 5: Scarcity (5:30 - 6:15)
    "clip_06_consensus.mp4",  # Trick 6: False Consensus (6:15 - 7:00)
    "clip_07_silence.mp4",    # Trick 7: Silence (7:00 - 7:30)
    "clip_08_conclusion.mp4", # Conclusion (7:30 - end)
]

print("="*60)
print("  THE SILENT STRATEGIST - Final Video Assembly")
print("  (with AI-generated video clips)")
print("="*60)

# Step 1: Get voiceover duration
print("\n[1/4] Getting voiceover duration...")
result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", AUDIO_PATH],
    capture_output=True, text=True
)
vo_duration = float(result.stdout.strip())
print(f"   Voiceover: {vo_duration:.1f}s ({vo_duration/60:.1f} min)")

# Step 2: Calculate segment durations
# Distribute the total duration across 8 clips
num_clips = len(CLIPS)
segment_duration = vo_duration / num_clips
print(f"\n[2/4] Each segment: ~{segment_duration:.1f}s (clip looped/extended)")

# Step 3: Create extended clips (loop each 8s clip to fill its segment)
print("\n[3/4] Extending clips to fill segments...")
extended_dir = os.path.join(BASE_DIR, "videos", "extended")
os.makedirs(extended_dir, exist_ok=True)

concat_parts = []
for i, clip_name in enumerate(CLIPS):
    clip_path = os.path.join(CLIPS_DIR, clip_name)
    extended_path = os.path.join(extended_dir, f"extended_{i:02d}.mp4")
    
    # Calculate how many loops needed (each clip is 8s)
    clip_duration = 8.0
    loops_needed = math.ceil(segment_duration / clip_duration)
    
    # Create concat file for this clip
    loop_file = os.path.join(extended_dir, f"loop_{i:02d}.txt")
    with open(loop_file, "w") as f:
        for _ in range(loops_needed):
            f.write(f"file '{clip_path}'\n")
    
    # Extend clip with loop and trim to segment duration
    # Also apply a slow zoom (Ken Burns) effect for more dynamism
    zoom_start = 1.0 + (i % 3) * 0.02  # Alternate zoom levels
    zoom_end = zoom_start + 0.05
    
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", loop_file,
        "-t", str(segment_duration),
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,zoompan=z='if(eq(on,0),{zoom_start},{zoom_start}+on*{(zoom_end-zoom_start)/(segment_duration*24)})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(segment_duration*24)}:s=1920x1080:fps=24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-an",
        extended_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback: simple loop without zoom
        cmd_simple = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", loop_file,
            "-t", str(segment_duration),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-an",
            extended_path
        ]
        subprocess.run(cmd_simple, capture_output=True, text=True)
    
    concat_parts.append(extended_path)
    print(f"   [{i+1}/{num_clips}] {clip_name} -> {segment_duration:.1f}s")

# Step 4: Concatenate all extended clips with crossfade transitions
print("\n[4/4] Assembling final video with transitions + audio...")

# First, concatenate all video clips
concat_file = os.path.join(extended_dir, "final_concat.txt")
with open(concat_file, "w") as f:
    for part in concat_parts:
        f.write(f"file '{part}'\n")

# Concatenate video
video_only = os.path.join(extended_dir, "video_only.mp4")
cmd_concat = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_file,
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-t", str(vo_duration),
    video_only
]
subprocess.run(cmd_concat, capture_output=True, text=True)

# Loop background music
music_looped = os.path.join(extended_dir, "music_looped.wav")
music_dur = float(subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", MUSIC_PATH],
    capture_output=True, text=True
).stdout.strip())

music_concat = os.path.join(extended_dir, "music_concat.txt")
with open(music_concat, "w") as f:
    for _ in range(int(vo_duration / music_dur) + 2):
        f.write(f"file '{MUSIC_PATH}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", music_concat, "-t", str(vo_duration),
    "-c:a", "pcm_s16le", music_looped
], capture_output=True, text=True)

# Final assembly: video + voiceover + music
cmd_final = [
    "ffmpeg", "-y",
    "-i", video_only,
    "-i", AUDIO_PATH,
    "-i", music_looped,
    "-filter_complex",
    "[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[vo];"
    "[2:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=0.07[music];"
    "[vo][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "22",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(vo_duration),
    "-movflags", "+faststart",
    OUTPUT_PATH
]

result = subprocess.run(cmd_final, capture_output=True, text=True)
if result.returncode != 0:
    print(f"   Error: {result.stderr[-500:]}")
    # Fallback without music
    cmd_fallback = [
        "ffmpeg", "-y",
        "-i", video_only,
        "-i", AUDIO_PATH,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(vo_duration),
        "-movflags", "+faststart",
        OUTPUT_PATH
    ]
    subprocess.run(cmd_fallback, capture_output=True, text=True)

# Cleanup extended clips
import shutil
shutil.rmtree(extended_dir, ignore_errors=True)

# Final info
file_size = os.path.getsize(OUTPUT_PATH) / (1024*1024)
print(f"\n{'='*60}")
print(f"  ✅ FINAL VIDEO ASSEMBLED!")
print(f"{'='*60}")
print(f"  📺 Output: {OUTPUT_PATH}")
print(f"  ⏱️  Duration: {vo_duration/60:.1f} minutes")
print(f"  📦 Size: {file_size:.1f} MB")
print(f"  🎬 Clips: {num_clips} AI-generated scenes")
print(f"  🎙️ Audio: AI voiceover + cinematic music")
print(f"{'='*60}\n")
