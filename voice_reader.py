from gtts import gTTS
import os
import cloudinary
import cloudinary.uploader
from gtts import gTTS
import tempfile
import os

# Cloudinary config
cloudinary.config(
  cloud_name = 'dojkqtwxq',
  api_key = '431963252619322',
  api_secret = 'jkughujnbhj'  # Don't expose this in public
)


def generate_voice(text, article_id):
    """
    Converts the given text to speech and saves it as an MP3 file.

    Parameters:
        text (str): The text content to convert to speech.
        article_id (int or str): The ID of the article used to name the MP3 file.

    Returns:
        str: Relative path to the generated MP3 file for HTML audio playback,
             or None if generation failed.

    Notes:
        - Uses Google Text-to-Speech (gTTS).
        - Trims text if longer than 4000 characters (gTTS fails at large input).
        - Saves MP3 into static/audio/ so Flask can serve it.
    """

    def generate_voice(text, article_id):
        if not text or not text.strip():
            return None

        try:
            # Step 1: Create temp audio file
            tts = gTTS(text[:4000])  # gTTS has a char limit
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_path = f.name
                tts.save(temp_path)

            # Step 2: Upload to Cloudinary (under folder "indocnow/audio")
            upload_result = cloudinary.uploader.upload(
                temp_path,
                folder="indocnow/audio/",
                public_id=f"article_{article_id}",
                resource_type="video"  # Audio is treated as 'video' in Cloudinary
            )

            # Step 3: Remove local temp file
            os.remove(temp_path)

            # Step 4: Return Cloudinary URL
            return upload_result["secure_url"]

        except Exception as e:
            print(f"[VoiceReader] Audio upload failed: {e}")
            return None


