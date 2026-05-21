#!/usr/bin/env python3
"""
Batch Video Generator for The Silent Strategist
=================================================
Generates multiple videos in sequence from the content calendar.
Usage: python3 batch_generate.py --count 3 --pillar dark_psychology
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CONTENT_TOPICS, CONTENT_PILLARS
from generate_video import VideoGenerator


def get_next_topics(pillar: str, count: int) -> list:
    """Get next topics to produce from the content calendar."""
    topics = CONTENT_TOPICS.get(pillar, [])
    
    # Check which topics have already been produced
    produced_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "produced_topics.json"
    )
    
    produced = []
    if os.path.exists(produced_file):
        with open(produced_file, "r") as f:
            produced = json.load(f)
    
    # Filter out already produced topics
    available = [t for t in topics if t not in produced]
    
    if not available:
        print(f"All topics in '{pillar}' have been produced! Generating new ones...")
        available = generate_new_topics(pillar, count)
    
    return available[:count]


def generate_new_topics(pillar: str, count: int) -> list:
    """Generate new topic ideas using GPT."""
    from openai import OpenAI
    client = OpenAI()
    
    pillar_descriptions = {
        "dark_psychology": "dark psychology, manipulation tactics, mind games, reading people",
        "stoicism": "stoic philosophy, emotional control, Marcus Aurelius, mental strength",
        "betrayal_narratives": "betrayal stories, revenge narratives, karma, justice stories"
    }
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Generate YouTube video titles for a dark psychology/stoicism channel. Titles should be clickable, curiosity-inducing, and slightly controversial. Return a JSON array of strings."},
            {"role": "user", "content": f"Generate {count * 2} unique video titles about: {pillar_descriptions.get(pillar, pillar)}"}
        ],
        max_tokens=500,
        temperature=0.9
    )
    
    try:
        content = response.choices[0].message.content.strip()
        start = content.find("[")
        end = content.rfind("]") + 1
        topics = json.loads(content[start:end])
        return topics[:count]
    except:
        return [f"The Hidden Truth About {pillar.replace('_', ' ').title()} #{i}" for i in range(count)]


def mark_as_produced(topics: list):
    """Mark topics as produced in the tracking file."""
    produced_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config", "produced_topics.json"
    )
    
    produced = []
    if os.path.exists(produced_file):
        with open(produced_file, "r") as f:
            produced = json.load(f)
    
    produced.extend(topics)
    
    with open(produced_file, "w") as f:
        json.dump(produced, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Batch generate videos")
    parser.add_argument("--count", type=int, default=3, help="Number of videos to generate")
    parser.add_argument("--pillar", type=str, default="random",
                       choices=["dark_psychology", "stoicism", "betrayal_narratives", "random"],
                       help="Content pillar (or 'random' to mix)")
    parser.add_argument("--script-only", action="store_true",
                       help="Only generate scripts")
    
    args = parser.parse_args()
    
    # Select pillar
    if args.pillar == "random":
        pillars_to_use = random.choices(CONTENT_PILLARS, k=args.count)
    else:
        pillars_to_use = [args.pillar] * args.count
    
    results = []
    produced_topics = []
    
    for i, pillar in enumerate(pillars_to_use):
        topics = get_next_topics(pillar, 1)
        if not topics:
            continue
        
        topic = topics[0]
        print(f"\n[Batch {i+1}/{args.count}] Generating: {topic}")
        print("-" * 50)
        
        generator = VideoGenerator(topic=topic, pillar=pillar)
        
        if args.script_only:
            script = generator.generate_script()
            results.append({"topic": topic, "pillar": pillar, "script_length": len(script.split())})
        else:
            result = generator.run_full_pipeline()
            results.append({"topic": topic, "pillar": pillar, "video_path": result["video_path"]})
        
        produced_topics.append(topic)
    
    # Mark topics as produced
    mark_as_produced(produced_topics)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  BATCH GENERATION COMPLETE")
    print(f"  Videos produced: {len(results)}")
    print(f"{'='*60}")
    for r in results:
        print(f"  • {r['topic']}")
    print()


if __name__ == "__main__":
    main()
