"""
Configuration settings for The Silent Strategist - YouTube Automation Pipeline
"""
import os

# ============================================================
# API KEYS (Set these as environment variables)
# ============================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# ============================================================
# CHANNEL SETTINGS
# ============================================================
CHANNEL_NAME = "The Silent Strategist"
CHANNEL_TAGLINE = "Master Your Mind. Master The Game."
CHANNEL_NICHE = "Dark Psychology, Stoicism & Betrayal Narratives"

# ============================================================
# VIDEO SETTINGS
# ============================================================
VIDEO_RESOLUTION = (1920, 1080)
VIDEO_FPS = 30
VIDEO_MIN_DURATION = 480  # 8 minutes in seconds
VIDEO_MAX_DURATION = 900  # 15 minutes in seconds
VIDEO_FONT = "Arial-Bold"
VIDEO_FONT_SIZE = 48
SUBTITLE_FONT_SIZE = 36
SUBTITLE_COLOR = "white"
SUBTITLE_STROKE_COLOR = "black"
SUBTITLE_STROKE_WIDTH = 2

# ============================================================
# AUDIO SETTINGS
# ============================================================
VOICEOVER_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # ElevenLabs 'Adam' deep male voice
VOICEOVER_MODEL = "eleven_multilingual_v2"
VOICEOVER_STABILITY = 0.5
VOICEOVER_SIMILARITY = 0.75
BACKGROUND_MUSIC_VOLUME = 0.08  # 8% volume for background music

# ============================================================
# CONTENT SETTINGS
# ============================================================
CONTENT_PILLARS = [
    "dark_psychology",
    "stoicism",
    "betrayal_narratives"
]

CONTENT_TOPICS = {
    "dark_psychology": [
        "7 Dark Psychology Tricks They Use to Control You",
        "How Narcissists Manipulate Your Emotions Without You Knowing",
        "The 48 Laws of Power: Darkest Tactics Explained",
        "5 Signs Someone Is Secretly Manipulating You",
        "Dark Psychology: How to Read Anyone Like a Book",
        "The Art of Psychological Warfare: Ancient Strategies",
        "Why Intelligent People Fall for Manipulation",
        "10 Mind Games Toxic People Play",
        "How to Detect Lies Using Dark Psychology",
        "The Psychology Behind Why People Betray You",
    ],
    "stoicism": [
        "Marcus Aurelius: How to Be Unshakeable",
        "The Stoic Response to Betrayal and Pain",
        "7 Stoic Rules for a Powerful Life",
        "Why Silence Is the Ultimate Power Move",
        "Epictetus: How to Control Your Emotions",
        "The Stoic Art of Not Caring What Others Think",
        "How Stoicism Makes You Mentally Invincible",
        "Seneca's Advice on Dealing with Toxic People",
        "The Power of Walking Away: A Stoic Lesson",
        "How to Use Stoicism to Overcome Any Hardship",
    ],
    "betrayal_narratives": [
        "He Trusted His Best Friend... The Betrayal Changed Everything",
        "The Ultimate Revenge: A Story of Patience and Justice",
        "She Destroyed His Life... But He Had the Last Laugh",
        "The Man Who Waited 10 Years for the Perfect Revenge",
        "When Loyalty Is Rewarded with Betrayal: True Stories",
        "The Coldest Revenge Ever Served: A True Story",
        "How One Betrayal Created an Empire",
        "The Psychology Behind Getting Even",
        "They Thought He Was Weak... They Were Wrong",
        "The Art of Silent Revenge: Stoic Stories",
    ]
}

# ============================================================
# THUMBNAIL SETTINGS
# ============================================================
THUMBNAIL_RESOLUTION = (1280, 720)
THUMBNAIL_STYLE = "dark_cinematic"
THUMBNAIL_FONT_SIZE = 72
THUMBNAIL_TEXT_COLOR = "#FFFFFF"
THUMBNAIL_ACCENT_COLOR = "#FF3333"

# ============================================================
# SEO SETTINGS
# ============================================================
DEFAULT_TAGS = [
    "dark psychology", "stoicism", "manipulation tactics",
    "psychology tricks", "marcus aurelius", "self improvement",
    "mental strength", "emotional intelligence", "revenge stories",
    "betrayal", "power moves", "mind games", "toxic people",
    "narcissist", "psychological warfare", "stoic philosophy"
]

DESCRIPTION_TEMPLATE = """
{title}

In this video, we explore {topic_description}

🔔 Subscribe for more content on dark psychology, stoicism, and mastering the human mind.

📚 Recommended Reading:
- The 48 Laws of Power by Robert Greene
- Meditations by Marcus Aurelius
- The Art of War by Sun Tzu

⏱️ Timestamps:
{timestamps}

#DarkPsychology #Stoicism #MindMastery #TheSilentStrategist

Disclaimer: This content is for educational purposes only.
"""

# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "thumbnails")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
BRANDING_DIR = os.path.join(BASE_DIR, "branding")
