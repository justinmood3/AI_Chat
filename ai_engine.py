from dotenv import load_dotenv
import os
import uuid
import logging
import re

from database import get_chats
from language_support import detect_language, language_instruction, localized_message
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# MoviePy (optional)
try:
    from moviepy.editor import ImageClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

# =========================
# GROQ CLIENT (PRIMARY)
# =========================
from openai import OpenAI

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None

if groq_api_key:
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
else:
    logger.warning("GROQ_API_KEY missing!")

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(__file__)
GENERATED_DIR = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

IMAGE_SIZE = (1024, 640)
WORDS_PER_SECOND = 2.5

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# =========================
# ERROR CLASS
# =========================
class ProviderFailure(Exception):
    def __init__(self, failures: dict):
        self.failures = failures
        super().__init__(str(failures))


# =========================
# GROQ TEXT GENERATION
# =========================
def generate_text(prompt, system_instruction=None):
    if not groq_client:
        raise ProviderFailure({"groq": "GROQ_API_KEY missing"})

    system_message = (
        "You are Justin AI. Be helpful, concise, and respond in the user's language."
    )

    if system_instruction:
        system_message += f" {system_instruction}"

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq error: {e}")
        raise ProviderFailure({"groq": str(e)})


# =========================
# DURATION HANDLING
# =========================
def requested_duration_seconds(message, default_seconds=30):
    text = message.lower()

    minute_match = re.search(r"(\d+(?:\.\d+)?)\s*(minute|min|minutes)", text)
    if minute_match:
        return max(default_seconds, int(float(minute_match.group(1)) * 60))

    second_match = re.search(r"(\d+)\s*(second|seconds)", text)
    if second_match:
        return max(default_seconds, int(second_match.group(1)))

    return default_seconds


def expand_to_duration(text, min_seconds):
    target_words = max(80, int(min_seconds * WORDS_PER_SECOND))
    words = text.split()

    if len(words) >= target_words:
        return text

    repeats = (target_words // len(words)) + 1
    return " ".join((words * repeats)[:target_words])


# =========================
# IMAGE GENERATION (PLACEHOLDER SAFE)
# =========================
def save_placeholder_image(prompt):
    filename = f"image_{uuid.uuid4().hex}.png"
    path = os.path.join(GENERATED_DIR, filename)

    image = Image.new("RGB", IMAGE_SIZE, color=(30, 40, 60))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    lines = []
    words = prompt.split()
    line = ""

    for word in words:
        if len(line + " " + word) > 40:
            lines.append(line)
            line = word
        else:
            line += " " + word if line else word

    if line:
        lines.append(line)

    y = 40
    for l in lines[:15]:
        draw.text((30, y), l, font=font, fill=(255, 255, 255))
        y += 30

    image.save(path)
    return f"/static/generated/{filename}"


def save_image(prompt):
    # No real AI image (Groq does not generate images)
    return save_placeholder_image(prompt)


# =========================
# AUDIO (GROQ + gTTS)
# =========================
def save_audio(prompt, min_seconds=30):
    text_prompt = f"Explain in detail for a voice narration: {prompt}"

    try:
        narration = generate_text(
            text_prompt,
            system_instruction=language_instruction(prompt)
        ).strip()
    except Exception:
        narration = prompt

    narration = expand_to_duration(narration, min_seconds)

    filename = f"audio_{uuid.uuid4().hex}.mp3"
    path = os.path.join(GENERATED_DIR, filename)

    tts = gTTS(text=narration, lang="en")
    tts.save(path)

    return f"/static/generated/{filename}"


# =========================
# VIDEO (OPTIONAL)
# =========================
def save_video(prompt, min_seconds=30):
    if not MOVIEPY_AVAILABLE:
        raise RuntimeError("MoviePy not installed")

    image_url = save_image(prompt)
    audio_url = save_audio(prompt, min_seconds)

    image_path = os.path.join(BASE_DIR, image_url.lstrip("/"))
    audio_path = os.path.join(BASE_DIR, audio_url.lstrip("/"))

    filename = f"video_{uuid.uuid4().hex}.mp4"
    path = os.path.join(GENERATED_DIR, filename)

    clip = ImageClip(image_path).set_duration(min_seconds)

    try:
        audio = AudioFileClip(audio_path)
        clip = clip.set_audio(audio)
    except:
        pass

    clip.write_videofile(path, fps=24, codec="libx264", audio_codec="aac", logger=None)

    return f"/static/generated/{filename}"


# =========================
# MEDIA DETECTION
# =========================
def is_media_request(message):
    text = message.lower()

    if any(k in text for k in ["image", "draw", "illustration"]):
        return "image"

    if any(k in text for k in ["audio", "voice", "sound"]):
        return "audio"

    if any(k in text for k in ["video", "movie"]):
        return "video"

    return None


# =========================
# MAIN RESPONSE ENGINE
# =========================
def get_response(user_message, thread_id):
    try:
        lang = detect_language(user_message)
        media_type = is_media_request(user_message)
        min_seconds = requested_duration_seconds(user_message)

        # IMAGE
        if media_type == "image":
            return {
                "text": localized_message("image_ready", lang),
                "media_type": "image",
                "media_url": save_image(user_message)
            }

        # AUDIO
        if media_type == "audio":
            return {
                "text": localized_message("audio_ready", lang),
                "media_type": "audio",
                "media_url": save_audio(user_message, min_seconds)
            }

        # VIDEO
        if media_type == "video":
            try:
                return {
                    "text": localized_message("video_ready", lang),
                    "media_type": "video",
                    "media_url": save_video(user_message, min_seconds)
                }
            except Exception as e:
                return {
                    "text": "Video generation failed",
                    "media_type": None,
                    "media_url": None
                }

        # CHAT HISTORY
        chats = get_chats(thread_id)
        history = "\n".join([f"User: {m}\nAI: {r}" for m, r, *_ in chats[-10:] if m])

        prompt = (
            f"Conversation:\n{history}\n\nUser: {user_message}"
            if history else user_message
        )

        ai_text = generate_text(prompt)

        return {
            "text": ai_text,
            "media_type": None,
            "media_url": None
        }

    except ProviderFailure as e:
        logger.error(e)
        return {
            "text": "AI service temporarily unavailable. Try again.",
            "media_type": None,
            "media_url": None
        }

    except Exception as e:
        logger.error(e)
        return {
            "text": "Unexpected error occurred.",
            "media_type": None,
            "media_url": None
        }