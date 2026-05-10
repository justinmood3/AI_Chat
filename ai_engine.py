from google import genai
from dotenv import load_dotenv
import os
import uuid
import logging
import re
from database import get_chats
from PIL import Image, ImageDraw, ImageFont
import pyttsx3

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    try:
        from moviepy.editor import ImageClip, AudioFileClip
    except ImportError:
        from moviepy import ImageClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)

gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
if not gemini_client:
    logger.warning("GEMINI_API_KEY not found. Gemini text generation will be skipped.")

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = None
if groq_api_key and OpenAI:
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
elif groq_api_key and not OpenAI:
    logger.warning("GROQ_API_KEY found, but the openai package is not installed.")

BASE_DIR = os.path.dirname(__file__)
GENERATED_DIR = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

IMAGE_SIZE = (1024, 640)
WORDS_PER_SECOND = 2.5
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MODEL_FALLBACKS = [
    GEMINI_MODEL,
    "gemini-flash-latest",
    "gemini-2.0-flash",
]


def generate_text(prompt):
    last_error = None

    if gemini_client:
        for model in dict.fromkeys(MODEL_FALLBACKS):
            try:
                response = gemini_client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text if response and response.text else ""
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini model {model} failed: {e}")

    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Justin AI. Be helpful, concise, and respond in the user's language."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            last_error = e
            logger.warning(f"Groq model {GROQ_MODEL} failed: {e}")

    if last_error:
        raise last_error
    raise ValueError("No AI provider is configured. Set GEMINI_API_KEY or GROQ_API_KEY in .env.")


def requested_duration_seconds(message, default_seconds=30):
    text = message.lower()
    if any(phrase in text for phrase in [
        "90 seconds",
        "ninety seconds",
        "one and a half minutes",
        "one minute and a half",
        "1.5 minutes",
        "at least 90"
    ]):
        return 90

    minute_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:minute|minutes|min|mins)\b", text)
    if minute_match:
        return max(default_seconds, int(float(minute_match.group(1)) * 60))

    second_match = re.search(r"(\d+)\s*(?:second|seconds|sec|secs)\b", text)
    if second_match:
        return max(default_seconds, int(second_match.group(1)))

    return default_seconds


def expand_to_duration(text, min_seconds):
    target_words = max(80, int(min_seconds * WORDS_PER_SECOND))
    words = text.split()
    if not words:
        return text

    if len(words) >= target_words:
        return text

    repeats = (target_words // len(words)) + 1
    return " ".join((words * repeats)[:target_words])


def save_image(prompt):
    filename = f"image_{uuid.uuid4().hex}.png"
    path = os.path.join(GENERATED_DIR, filename)
    image = Image.new("RGB", IMAGE_SIZE, color=(25, 40, 70))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    lines = []
    words = prompt.split()
    line = ""
    for word in words:
        if len(line + " " + word) > 40:
            lines.append(line.strip())
            line = word
        else:
            line += " " + word if line else word
    if line:
        lines.append(line)
    y = 30
    for line in lines[:18]:
        draw.text((30, y), line, font=font, fill=(240, 240, 240))
        y += 34
    draw.rectangle([(20, 20), (IMAGE_SIZE[0] - 20, IMAGE_SIZE[1] - 20)], outline=(95, 155, 230), width=4)
    image.save(path)
    return f"/static/generated/{filename}"


def save_audio(prompt, min_seconds=90):
    text_prompt = f"Create a long spoken narrative of at least {min_seconds} seconds about: {prompt}"
    try:
        narration = generate_text(text_prompt).strip()
    except Exception as e:
        logger.warning(f"Failed to get expanded audio text: {e}")
        narration = prompt

    narration = expand_to_duration(narration, min_seconds)

    filename = f"audio_{uuid.uuid4().hex}.wav"
    path = os.path.join(GENERATED_DIR, filename)
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.save_to_file(narration, path)
    engine.runAndWait()
    return f"/static/generated/{filename}"


def save_video(prompt, min_seconds=90):
    image_url = save_image(prompt + " video background")
    audio_url = save_audio(prompt, min_seconds=min_seconds)
    image_path = os.path.join(BASE_DIR, image_url.replace("/static/", "static/"))
    audio_path = os.path.join(BASE_DIR, audio_url.replace("/static/", "static/"))
    filename = f"video_{uuid.uuid4().hex}.mp4"
    path = os.path.join(GENERATED_DIR, filename)

    if not MOVIEPY_AVAILABLE:
        raise RuntimeError("Video generation requires moviepy library. Install moviepy to generate video files.")

    clip = ImageClip(image_path)
    if hasattr(clip, "with_duration"):
        clip = clip.with_duration(min_seconds)
    else:
        clip = clip.set_duration(min_seconds)

    audio_clip = None
    try:
        audio_clip = AudioFileClip(audio_path)
        if hasattr(clip, "with_audio"):
            clip = clip.with_audio(audio_clip)
        else:
            clip = clip.set_audio(audio_clip)
    except Exception:
        pass
    try:
        clip.write_videofile(path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    finally:
        clip.close()
        if audio_clip:
            audio_clip.close()
    return f"/static/generated/{filename}"


def is_media_request(message):
    text = message.lower()
    if any(word in text for word in ["generate image", "create image", "make image", "image of", "draw", "picture of", "illustration"]):
        return "image"
    if any(word in text for word in ["generate audio", "create audio", "make audio", "audio of", "voice message", "voice note", "recording", "mp3", "wav"]):
        return "audio"
    if any(word in text for word in ["generate video", "create video", "make video", "video of", "movie", "film"]):
        return "video"
    return None


def get_response(user_message, thread_id):
    try:
        media_type = is_media_request(user_message)
        min_seconds = requested_duration_seconds(user_message)

        if media_type == "image":
            media_url = save_image(user_message)
            return {
                "text": "Here is your generated image.",
                "media_type": "image",
                "media_url": media_url
            }

        if media_type == "audio":
            media_url = save_audio(user_message, min_seconds=min_seconds)
            return {
                "text": f"Here is your generated audio file ({min_seconds} seconds requested).",
                "media_type": "audio",
                "media_url": media_url
            }

        if media_type == "video":
            try:
                media_url = save_video(user_message, min_seconds=min_seconds)
                return {
                    "text": f"Here is your generated video ({min_seconds} seconds requested).",
                    "media_type": "video",
                    "media_url": media_url
                }
            except Exception as e:
                return {
                    "text": f"Video generation failed: {str(e)}",
                    "media_type": None,
                    "media_url": None
                }

        chats = get_chats(thread_id)
        history = "\n".join([f"User: {msg}\nAI: {reply}" for msg, reply, *_ in chats[-10:] if msg])
        if history:
            prompt = f"Conversation history:\n{history}\n\nPlease respond to the following user message in the same language that the user used. User message: {user_message}"
        else:
            prompt = f"Please respond to the following message: {user_message}"

        ai_text = generate_text(prompt) or "Sorry, I couldn't generate a response. Please try again."

        return {
            "text": ai_text,
            "media_type": None,
            "media_url": None
        }

    except ValueError as e:
        logger.error(f"API Key Error: {str(e)}")
        return {"text": f"Configuration Error: {str(e)}", "media_type": None, "media_url": None}
    except Exception as e:
        logger.error(f"Error getting response: {str(e)}")
        return {"text": f"Error: {str(e)}", "media_type": None, "media_url": None}
