#!/usr/bin/env python3
"""
Thumbnail Generator for The Silent Strategist
===============================================
Generates eye-catching thumbnails using AI image generation + text overlay.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import *

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    os.system("sudo pip3 install Pillow")
    from PIL import Image, ImageDraw, ImageFont

from openai import OpenAI


class ThumbnailGenerator:
    """Generate YouTube thumbnails with AI backgrounds and bold text."""

    def __init__(self):
        self.client = OpenAI()
        os.makedirs(THUMBNAILS_DIR, exist_ok=True)

    def generate(self, topic: str, thumbnail_text: str = None, style: str = "dark_cinematic") -> str:
        """Generate a complete thumbnail for a video topic."""
        
        if not thumbnail_text:
            thumbnail_text = self._generate_thumbnail_text(topic)
        
        # Generate base image with AI
        base_image_path = self._generate_base_image(topic, style)
        
        # Add text overlay
        final_path = self._add_text_overlay(base_image_path, thumbnail_text, topic)
        
        return final_path

    def _generate_thumbnail_text(self, topic: str) -> str:
        """Generate short, impactful thumbnail text."""
        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "Generate 2-4 word thumbnail text that is shocking, curiosity-inducing, and would make someone click. Use ALL CAPS. Examples: 'THEY KNOW', 'DARK TRUTH', 'NEVER TRUST', 'SILENT POWER'"},
                {"role": "user", "content": f"Topic: {topic}"}
            ],
            max_tokens=20,
            temperature=0.9
        )
        return response.choices[0].message.content.strip().strip('"').upper()

    def _generate_base_image(self, topic: str, style: str) -> str:
        """Generate the base thumbnail image using DALL-E."""
        
        style_prompts = {
            "dark_cinematic": "extremely dark and moody cinematic scene, deep shadows, single dramatic light source, dark blue and black tones with golden accent light, mysterious atmosphere, ultra high contrast, 4K quality",
            "stoic": "ancient Greek marble statue in dramatic side lighting, dark background, golden hour light on one side, philosophical and powerful mood, cinematic composition",
            "psychology": "close-up silhouette of a face in profile, one glowing amber eye visible, dark smoky background, mysterious and unsettling, high contrast, cinematic"
        }
        
        base_prompt = style_prompts.get(style, style_prompts["dark_cinematic"])
        
        # Add topic-specific elements
        topic_lower = topic.lower()
        if "betray" in topic_lower or "revenge" in topic_lower:
            base_prompt += ", broken chess pieces, shattered glass elements"
        elif "stoic" in topic_lower or "marcus" in topic_lower:
            base_prompt += ", ancient Roman architecture in background, marble texture"
        elif "manipulat" in topic_lower or "control" in topic_lower:
            base_prompt += ", puppet strings visible, hands controlling from shadows"
        elif "power" in topic_lower or "silence" in topic_lower:
            base_prompt += ", lone wolf silhouette, mountain peak, storm clouds"
        
        base_prompt += ". YouTube thumbnail composition, leave right side relatively empty for text overlay."
        
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=base_prompt,
            size="1792x1024",
            quality="hd",
            n=1
        )
        
        import requests
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        
        safe_topic = topic.replace(" ", "_").replace(":", "").replace("?", "")[:30]
        base_path = os.path.join(THUMBNAILS_DIR, f"{safe_topic}_base.png")
        
        with open(base_path, "wb") as f:
            f.write(image_response.content)
        
        return base_path

    def _add_text_overlay(self, base_image_path: str, text: str, topic: str) -> str:
        """Add bold text overlay to the thumbnail."""
        
        img = Image.open(base_image_path)
        img = img.resize(THUMBNAIL_RESOLUTION, Image.LANCZOS)
        draw = ImageDraw.Draw(img)
        
        # Try to load a bold font
        font_size = THUMBNAIL_FONT_SIZE
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Split text into lines if too long
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > THUMBNAIL_RESOLUTION[0] * 0.55:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        
        # Position text on right side
        total_text_height = len(lines) * (font_size + 10)
        y_start = (THUMBNAIL_RESOLUTION[1] - total_text_height) // 2
        
        for i, line in enumerate(lines):
            y = y_start + i * (font_size + 10)
            x = THUMBNAIL_RESOLUTION[0] * 0.4  # Start at 40% from left
            
            # Draw text stroke (outline)
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    draw.text((x + dx, y + dy), line, font=font, fill="black")
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=THUMBNAIL_TEXT_COLOR)
        
        # Add red accent line under text
        accent_y = y_start + total_text_height + 15
        draw.rectangle(
            [THUMBNAIL_RESOLUTION[0] * 0.4, accent_y,
             THUMBNAIL_RESOLUTION[0] * 0.4 + 200, accent_y + 6],
            fill=THUMBNAIL_ACCENT_COLOR
        )
        
        # Save final thumbnail
        safe_topic = topic.replace(" ", "_").replace(":", "").replace("?", "")[:30]
        final_path = os.path.join(THUMBNAILS_DIR, f"{safe_topic}_thumbnail.png")
        img.save(final_path, "PNG", quality=95)
        
        print(f"   Thumbnail saved: {final_path}")
        return final_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate a YouTube thumbnail")
    parser.add_argument("--topic", type=str, required=True, help="Video topic")
    parser.add_argument("--text", type=str, default=None, help="Thumbnail text (auto-generated if not provided)")
    parser.add_argument("--style", type=str, default="dark_cinematic",
                       choices=["dark_cinematic", "stoic", "psychology"])
    
    args = parser.parse_args()
    
    generator = ThumbnailGenerator()
    result = generator.generate(args.topic, args.text, args.style)
    print(f"Thumbnail generated: {result}")


if __name__ == "__main__":
    main()
