#!/usr/bin/env python3
"""
The Silent Strategist - Automated Video Generation Pipeline
============================================================
This script automates the entire video creation process:
1. Generate script using OpenAI GPT
2. Generate voiceover using ElevenLabs (or OpenAI TTS as fallback)
3. Download relevant stock footage from Pexels
4. Assemble video with MoviePy (voiceover + stock footage + subtitles)
5. Generate thumbnail
"""

import os
import sys
import json
import time
import requests
import textwrap
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system("sudo pip3 install openai")
    from openai import OpenAI

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, CompositeAudioClip
    )
except ImportError:
    print("Installing moviepy...")
    os.system("sudo pip3 install moviepy[optional]")
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, ColorClip, CompositeAudioClip
    )


class VideoGenerator:
    """Main class for generating faceless YouTube videos."""

    def __init__(self, topic: str, pillar: str = "dark_psychology"):
        self.topic = topic
        self.pillar = pillar
        self.client = OpenAI()  # Uses OPENAI_API_KEY env var
        self.script = ""
        self.audio_path = ""
        self.video_clips = []
        self.output_path = ""

        # Create output directories
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)

    def generate_script(self) -> str:
        """Generate a compelling video script using GPT."""
        print(f"[1/5] Generating script for: {self.topic}")

        prompt = f"""You are a professional YouTube scriptwriter for a channel called "The Silent Strategist" 
that covers dark psychology, stoicism, and betrayal narratives.

Write a compelling 10-minute YouTube video script on the topic: "{self.topic}"

REQUIREMENTS:
- Start with a powerful hook (first 5 seconds must grab attention)
- Use a deep, authoritative, slightly mysterious tone
- Include pattern interrupts every 30-45 seconds (questions, shocking facts, pauses)
- Structure: Hook → Introduction → Main Content (5-7 key points) → Conclusion with call-to-action
- Use storytelling elements and real examples/anecdotes
- Include open loops to maintain viewer retention
- End with a thought-provoking statement and subscribe CTA
- Total word count: 1400-1800 words (for ~10 min at natural pace)
- Do NOT include stage directions or visual cues - ONLY the narration text
- Write in a way that sounds natural when spoken aloud

TONE: Authoritative, mysterious, slightly dark, intellectual, empowering.
Think of a mix between a TED talk and a thriller movie narrator.

OUTPUT FORMAT:
Return ONLY the narration script text, nothing else. No titles, no headers, no [brackets].
Just the pure spoken words from start to finish.
"""

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert YouTube scriptwriter specializing in dark psychology and stoicism content. You write scripts that achieve 60%+ audience retention."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.8
        )

        self.script = response.choices[0].message.content.strip()
        
        # Save script to file
        safe_topic = self.topic.replace(" ", "_").replace(":", "").replace("?", "")[:50]
        script_path = os.path.join(SCRIPTS_DIR, f"{safe_topic}.txt")
        with open(script_path, "w") as f:
            f.write(self.script)
        
        print(f"   Script generated: {len(self.script.split())} words")
        return self.script

    def generate_voiceover(self) -> str:
        """Generate voiceover using OpenAI TTS (or ElevenLabs if configured)."""
        print("[2/5] Generating voiceover...")

        safe_topic = self.topic.replace(" ", "_").replace(":", "").replace("?", "")[:50]
        self.audio_path = os.path.join(AUDIO_DIR, f"{safe_topic}.mp3")

        if ELEVENLABS_API_KEY:
            # Use ElevenLabs for higher quality
            self._generate_elevenlabs_voiceover()
        else:
            # Fallback to OpenAI TTS
            self._generate_openai_voiceover()

        print(f"   Voiceover saved: {self.audio_path}")
        return self.audio_path

    def _generate_openai_voiceover(self):
        """Generate voiceover using OpenAI TTS API."""
        response = self.client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",  # Deep, authoritative male voice
            input=self.script,
            speed=0.95  # Slightly slower for gravitas
        )
        response.stream_to_file(self.audio_path)

    def _generate_elevenlabs_voiceover(self):
        """Generate voiceover using ElevenLabs API."""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICEOVER_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": self.script,
            "model_id": VOICEOVER_MODEL,
            "voice_settings": {
                "stability": VOICEOVER_STABILITY,
                "similarity_boost": VOICEOVER_SIMILARITY
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(self.audio_path, "wb") as f:
                f.write(response.content)
        else:
            print(f"   ElevenLabs failed ({response.status_code}), falling back to OpenAI TTS")
            self._generate_openai_voiceover()

    def download_stock_footage(self, num_clips: int = 8) -> list:
        """Download relevant stock footage from Pexels."""
        print(f"[3/5] Downloading {num_clips} stock video clips...")

        # Generate search keywords based on topic
        keywords = self._get_video_keywords()
        downloaded = []

        for i, keyword in enumerate(keywords[:num_clips]):
            clip_path = self._download_pexels_video(keyword, i)
            if clip_path:
                downloaded.append(clip_path)

        # If not enough clips from Pexels, use fallback keywords
        fallback_keywords = [
            "dark silhouette", "chess game", "thinking man",
            "city night", "storm clouds", "ancient statue",
            "fire flames", "ocean waves dark", "wolf eyes",
            "library books", "rain window", "clock time"
        ]
        
        while len(downloaded) < num_clips:
            idx = len(downloaded)
            keyword = fallback_keywords[idx % len(fallback_keywords)]
            clip_path = self._download_pexels_video(keyword, idx)
            if clip_path:
                downloaded.append(clip_path)
            else:
                break

        self.video_clips = downloaded
        print(f"   Downloaded {len(downloaded)} clips")
        return downloaded

    def _get_video_keywords(self) -> list:
        """Use GPT to generate relevant video search keywords."""
        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "Generate 10 short stock video search keywords (2-3 words each) that would visually complement a video about the given topic. Focus on moody, dark, cinematic visuals. Return only a JSON array of strings."},
                {"role": "user", "content": f"Topic: {self.topic}\nPillar: {self.pillar}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        try:
            content = response.choices[0].message.content.strip()
            # Try to parse JSON
            if content.startswith("["):
                keywords = json.loads(content)
            else:
                # Extract JSON from response
                start = content.find("[")
                end = content.rfind("]") + 1
                keywords = json.loads(content[start:end])
            return keywords
        except (json.JSONDecodeError, ValueError):
            # Fallback keywords
            return [
                "dark silhouette man", "chess strategy", "storm clouds",
                "ancient philosophy", "wolf predator", "fire darkness",
                "city night rain", "thinking contemplation", "power control",
                "shadows mystery"
            ]

    def _download_pexels_video(self, keyword: str, index: int) -> str:
        """Download a single video from Pexels API."""
        if not PEXELS_API_KEY:
            return self._create_placeholder_clip(index)

        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": keyword,
            "per_page": 3,
            "orientation": "landscape",
            "size": "medium"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("videos"):
                    video = data["videos"][0]
                    # Get HD video file
                    video_files = video.get("video_files", [])
                    hd_file = None
                    for vf in video_files:
                        if vf.get("height", 0) >= 720:
                            hd_file = vf
                            break
                    if not hd_file and video_files:
                        hd_file = video_files[0]

                    if hd_file:
                        video_url = hd_file["link"]
                        clip_path = os.path.join(VIDEOS_DIR, f"clip_{index:03d}.mp4")
                        video_response = requests.get(video_url, stream=True)
                        with open(clip_path, "wb") as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        return clip_path
        except Exception as e:
            print(f"   Warning: Could not download clip for '{keyword}': {e}")

        return self._create_placeholder_clip(index)

    def _create_placeholder_clip(self, index: int) -> str:
        """Create a dark placeholder clip when stock footage is unavailable."""
        clip_path = os.path.join(VIDEOS_DIR, f"clip_{index:03d}.mp4")
        
        # Create a dark gradient clip
        clip = ColorClip(
            size=VIDEO_RESOLUTION,
            color=(10, 10, 20),  # Very dark blue-black
            duration=15
        )
        clip = clip.set_fps(VIDEO_FPS)
        clip.write_videofile(clip_path, codec="libx264", audio=False, logger=None)
        clip.close()
        return clip_path

    def assemble_video(self) -> str:
        """Assemble final video from audio + video clips + subtitles."""
        print("[4/5] Assembling final video...")

        safe_topic = self.topic.replace(" ", "_").replace(":", "").replace("?", "")[:50]
        self.output_path = os.path.join(VIDEOS_DIR, f"{safe_topic}_FINAL.mp4")

        # Load audio
        audio = AudioFileClip(self.audio_path)
        total_duration = audio.duration

        # Calculate clip durations
        num_clips = len(self.video_clips)
        if num_clips == 0:
            # Create single dark background
            final_video = ColorClip(
                size=VIDEO_RESOLUTION,
                color=(10, 10, 20),
                duration=total_duration
            ).set_fps(VIDEO_FPS)
        else:
            clip_duration = total_duration / num_clips
            clips = []

            for clip_path in self.video_clips:
                try:
                    clip = VideoFileClip(clip_path)
                    # Resize to target resolution
                    clip = clip.resize(VIDEO_RESOLUTION)
                    # Loop or trim to needed duration
                    if clip.duration < clip_duration:
                        # Loop the clip
                        loops_needed = int(clip_duration / clip.duration) + 1
                        clip = concatenate_videoclips([clip] * loops_needed)
                    clip = clip.subclip(0, clip_duration)
                    clips.append(clip)
                except Exception as e:
                    print(f"   Warning: Could not process clip {clip_path}: {e}")
                    # Add dark placeholder
                    placeholder = ColorClip(
                        size=VIDEO_RESOLUTION,
                        color=(10, 10, 20),
                        duration=clip_duration
                    ).set_fps(VIDEO_FPS)
                    clips.append(placeholder)

            final_video = concatenate_videoclips(clips, method="compose")

        # Set audio
        final_video = final_video.set_audio(audio)

        # Add subtle dark overlay for consistency
        dark_overlay = ColorClip(
            size=VIDEO_RESOLUTION,
            color=(0, 0, 0),
            duration=total_duration
        ).set_opacity(0.3).set_fps(VIDEO_FPS)

        final_composite = CompositeVideoClip([final_video, dark_overlay])
        final_composite = final_composite.set_audio(audio)

        # Write final video
        final_composite.write_videofile(
            self.output_path,
            codec="libx264",
            audio_codec="aac",
            fps=VIDEO_FPS,
            preset="medium",
            bitrate="5000k",
            logger=None
        )

        # Cleanup
        audio.close()
        final_video.close()
        final_composite.close()

        print(f"   Video assembled: {self.output_path}")
        return self.output_path

    def generate_metadata(self) -> dict:
        """Generate SEO-optimized title, description, and tags."""
        print("[5/5] Generating video metadata...")

        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": """Generate YouTube video metadata for a dark psychology/stoicism channel.
Return a JSON object with:
- "title": Clickable, curiosity-inducing title (max 60 chars)
- "description": Full YouTube description with timestamps placeholder
- "tags": Array of 15-20 relevant tags
- "thumbnail_text": Short text for thumbnail (max 4 words, impactful)"""},
                {"role": "user", "content": f"Video topic: {self.topic}\nScript preview: {self.script[:500]}"}
            ],
            max_tokens=800,
            temperature=0.7
        )

        try:
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            metadata = json.loads(content)
        except (json.JSONDecodeError, IndexError):
            metadata = {
                "title": self.topic,
                "description": DESCRIPTION_TEMPLATE.format(
                    title=self.topic,
                    topic_description=self.topic,
                    timestamps="0:00 Introduction\n2:00 Main Content\n8:00 Conclusion"
                ),
                "tags": DEFAULT_TAGS,
                "thumbnail_text": "DARK TRUTH"
            }

        # Save metadata
        metadata_path = os.path.join(VIDEOS_DIR, f"{self.topic.replace(' ', '_')[:50]}_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"   Metadata generated and saved")
        return metadata

    def run_full_pipeline(self) -> dict:
        """Run the complete video generation pipeline."""
        print(f"\n{'='*60}")
        print(f"  THE SILENT STRATEGIST - Video Generation Pipeline")
        print(f"  Topic: {self.topic}")
        print(f"{'='*60}\n")

        # Step 1: Generate script
        self.generate_script()

        # Step 2: Generate voiceover
        self.generate_voiceover()

        # Step 3: Download stock footage
        self.download_stock_footage()

        # Step 4: Assemble video
        self.assemble_video()

        # Step 5: Generate metadata
        metadata = self.generate_metadata()

        print(f"\n{'='*60}")
        print(f"  ✅ VIDEO GENERATION COMPLETE!")
        print(f"  Output: {self.output_path}")
        print(f"{'='*60}\n")

        return {
            "video_path": self.output_path,
            "audio_path": self.audio_path,
            "script": self.script,
            "metadata": metadata
        }


def main():
    """Main entry point for video generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate a faceless YouTube video")
    parser.add_argument("--topic", type=str, required=True, help="Video topic/title")
    parser.add_argument("--pillar", type=str, default="dark_psychology",
                       choices=["dark_psychology", "stoicism", "betrayal_narratives"],
                       help="Content pillar")
    parser.add_argument("--script-only", action="store_true",
                       help="Only generate the script, skip video assembly")
    
    args = parser.parse_args()

    generator = VideoGenerator(topic=args.topic, pillar=args.pillar)
    
    if args.script_only:
        script = generator.generate_script()
        print(f"\n--- SCRIPT ---\n{script}\n")
    else:
        result = generator.run_full_pipeline()
        print(json.dumps({k: v for k, v in result.items() if k != "script"}, indent=2))


if __name__ == "__main__":
    main()
