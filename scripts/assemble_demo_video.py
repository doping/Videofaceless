#!/usr/bin/env python3
"""
Assemble a complete demo video for The Silent Strategist.
Uses a simple dark background + voiceover + background music.
Optimized for speed.
"""

import os
import sys
import subprocess

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_PATH = os.path.join(BASE_DIR, "audio", "video_001_dark_psychology_tricks.wav")
MUSIC_PATH = os.path.join(BASE_DIR, "audio", "background_music_dark_cinematic.mp3")
OUTPUT_PATH = os.path.join(BASE_DIR, "videos", "video_001_FINAL.mp4")

# Check files exist
if not os.path.exists(AUDIO_PATH):
    print(f"ERROR: Voiceover not found: {AUDIO_PATH}")
    sys.exit(1)
if not os.path.exists(MUSIC_PATH):
    print(f"ERROR: Background music not found: {MUSIC_PATH}")
    sys.exit(1)

print("="*60)
print("  THE SILENT STRATEGIST - Video Assembly")
print("="*60)

# Step 1: Get voiceover duration
print("\n[1/3] Analyzing voiceover duration...")
result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", 
     "-of", "default=noprint_wrappers=1:nokey=1", AUDIO_PATH],
    capture_output=True, text=True
)
vo_duration = float(result.stdout.strip())
print(f"   Voiceover duration: {vo_duration:.1f} seconds ({vo_duration/60:.1f} minutes)")

# Step 2: Loop background music
print("\n[2/3] Preparing background music (looped)...")
music_looped_path = os.path.join(BASE_DIR, "audio", "music_looped.wav")

# Get music duration
result = subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", MUSIC_PATH],
    capture_output=True, text=True
)
music_duration = float(result.stdout.strip())
loops_needed = int(vo_duration / music_duration) + 2
print(f"   Music duration: {music_duration:.1f}s, looping {loops_needed}x")

# Create concat file for looping
concat_file = os.path.join(BASE_DIR, "audio", "concat_list.txt")
with open(concat_file, "w") as f:
    for _ in range(loops_needed):
        f.write(f"file '{MUSIC_PATH}'\n")

# Loop the music and trim to voiceover duration
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_file,
    "-t", str(vo_duration),
    "-c:a", "pcm_s16le",
    music_looped_path
], capture_output=True, text=True)
print(f"   Looped music ready")

# Step 3: Combine into final video using a simple dark color background
print("\n[3/3] Assembling final video (dark bg + voiceover + music)...")

# Use ffmpeg to create video with:
# - Simple solid dark color background (very fast to generate)
# - Voiceover as main audio
# - Background music at low volume
cmd_final = [
    "ffmpeg", "-y",
    # Dark background - simple color source (much faster than noise filter)
    "-f", "lavfi", "-i", f"color=c=0x080812:s=1920x1080:d={vo_duration}:r=24",
    # Voiceover
    "-i", AUDIO_PATH,
    # Background music (looped)
    "-i", music_looped_path,
    # Mix audio: voiceover at full + music at 8%
    "-filter_complex",
    "[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[vo];"
    "[2:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=0.08[music];"
    "[vo][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
    "-c:a", "aac", "-b:a", "128k",
    "-t", str(vo_duration),
    OUTPUT_PATH
]

result = subprocess.run(cmd_final, capture_output=True, text=True)
if result.returncode != 0:
    print(f"   Error with music mix: {result.stderr[-300:]}")
    print("   Trying simpler approach (voiceover only)...")
    cmd_simple = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x080812:s=1920x1080:d={vo_duration}:r=24",
        "-i", AUDIO_PATH,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(vo_duration),
        OUTPUT_PATH
    ]
    result = subprocess.run(cmd_simple, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   FATAL: {result.stderr[-300:]}")
        sys.exit(1)

# Cleanup
if os.path.exists(music_looped_path):
    os.remove(music_looped_path)
if os.path.exists(concat_file):
    os.remove(concat_file)

# Get final file size
file_size = os.path.getsize(OUTPUT_PATH) / (1024*1024)

print(f"\n{'='*60}")
print(f"  ✅ VIDEO ASSEMBLY COMPLETE!")
print(f"{'='*60}")
print(f"  📺 Output: {OUTPUT_PATH}")
print(f"  ⏱️  Duration: {vo_duration/60:.1f} minutes")
print(f"  📦 Size: {file_size:.1f} MB")
print(f"  🎙️ Audio: AI voiceover + dark cinematic music")
print(f"{'='*60}\n")
