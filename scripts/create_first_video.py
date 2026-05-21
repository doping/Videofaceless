#!/usr/bin/env python3
"""
Create the first video for The Silent Strategist channel.
This generates:
1. A full script
2. Video metadata
(Voiceover is generated separately using the speech generation tool)
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *
from openai import OpenAI

client = OpenAI()

# First video topic
TOPIC = "7 Dark Psychology Tricks They Use to Control You"
PILLAR = "dark_psychology"

print(f"\n{'='*60}")
print(f"  THE SILENT STRATEGIST - First Video Production")
print(f"  Topic: {TOPIC}")
print(f"{'='*60}\n")

# ============================================================
# STEP 1: Generate Script
# ============================================================
print("[1/2] Generating script...")

script_prompt = f"""You are a professional YouTube scriptwriter for a channel called "The Silent Strategist" 
that covers dark psychology, stoicism, and betrayal narratives.

Write a compelling 10-minute YouTube video script on the topic: "{TOPIC}"

REQUIREMENTS:
- Start with a powerful hook (first 5 seconds must grab attention)
- Use a deep, authoritative, slightly mysterious tone
- Include pattern interrupts every 30-45 seconds (questions, shocking facts, pauses)
- Structure: Hook → Introduction → 7 Key Tricks → Conclusion with call-to-action
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

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are an expert YouTube scriptwriter specializing in dark psychology and stoicism content. You write scripts that achieve 60%+ audience retention."},
        {"role": "user", "content": script_prompt}
    ],
    max_tokens=3000,
    temperature=0.8
)

script = response.choices[0].message.content.strip()
word_count = len(script.split())
print(f"   Script generated: {word_count} words (~{word_count // 150} minutes)")

# Save script
os.makedirs(SCRIPTS_DIR, exist_ok=True)
script_path = os.path.join(SCRIPTS_DIR, "video_001_dark_psychology_tricks.txt")
with open(script_path, "w") as f:
    f.write(script)
print(f"   Saved to: {script_path}")

# ============================================================
# STEP 2: Generate Metadata
# ============================================================
print("\n[2/2] Generating video metadata...")

metadata_response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": """You are a YouTube SEO expert. Generate optimized metadata for a dark psychology video.
Return a valid JSON object with these fields:
- "title": Clickable title (max 60 chars, curiosity-inducing)
- "description": Full YouTube description (include hook, content summary, timestamps, hashtags, disclaimer)
- "tags": Array of 20 relevant tags for SEO
- "thumbnail_text": 2-4 word text for thumbnail (ALL CAPS, shocking/intriguing)
- "category": YouTube category
"""},
        {"role": "user", "content": f"Video topic: {TOPIC}\nScript preview: {script[:800]}"}
    ],
    max_tokens=1000,
    temperature=0.7
)

try:
    content = metadata_response.choices[0].message.content.strip()
    # Clean up potential markdown formatting
    if "```" in content:
        parts = content.split("```")
        for part in parts:
            if part.strip().startswith("json"):
                content = part.strip()[4:]
                break
            elif part.strip().startswith("{"):
                content = part.strip()
                break
    metadata = json.loads(content)
except (json.JSONDecodeError, IndexError) as e:
    print(f"   Warning: Could not parse metadata JSON, using defaults. Error: {e}")
    metadata = {
        "title": "7 Dark Psychology Tricks They Use to Control You",
        "description": f"""7 Dark Psychology Tricks They Use to Control You | The Silent Strategist

In this video, we reveal the 7 most powerful dark psychology tricks that manipulators use to control your thoughts, emotions, and decisions — without you even realizing it.

🔔 Subscribe for more content on dark psychology, stoicism, and mastering the human mind.

📚 Recommended Reading:
- The 48 Laws of Power by Robert Greene
- Influence by Robert Cialdini
- The Art of Seduction by Robert Greene

⏱️ Timestamps:
0:00 - The Hook
0:30 - Introduction
1:30 - Trick #1
3:00 - Trick #2
4:00 - Trick #3
5:00 - Trick #4
6:00 - Trick #5
7:00 - Trick #6
8:00 - Trick #7
9:00 - Conclusion

#DarkPsychology #Manipulation #MindGames #Stoicism #TheSilentStrategist

⚠️ Disclaimer: This content is for educational purposes only.""",
        "tags": ["dark psychology", "manipulation tactics", "mind control", "psychology tricks",
                 "how to read people", "body language", "narcissist", "toxic people",
                 "self improvement", "stoicism", "mental strength", "emotional intelligence",
                 "power moves", "influence", "persuasion", "robert greene",
                 "48 laws of power", "psychological warfare", "mind games", "dark psychology tricks"],
        "thumbnail_text": "THEY CONTROL YOU",
        "category": "Education"
    }

# Save metadata
metadata_path = os.path.join(VIDEOS_DIR, "video_001_metadata.json")
os.makedirs(VIDEOS_DIR, exist_ok=True)
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
print(f"   Metadata saved: {metadata_path}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*60}")
print(f"  ✅ SCRIPT & METADATA GENERATED!")
print(f"{'='*60}")
print(f"  📝 Script: {script_path} ({word_count} words)")
print(f"  📋 Metadata: {metadata_path}")
print(f"  🖼️ Thumbnail text: {metadata.get('thumbnail_text', 'N/A')}")
print(f"  📺 Title: {metadata.get('title', TOPIC)}")
print(f"{'='*60}\n")
print(f"\nNOTE: Voiceover will be generated separately using AI speech synthesis.")
