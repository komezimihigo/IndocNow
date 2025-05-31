from gtts import gTTS
import os

def generate_voice(text, article_id):
    """
    Converts given text to speech and saves it as an MP3 file.
    Returns the path for HTML audio playback.
    """
    if not text or not text.strip():
        print("No text to generate voice.")
        return None

    # Trim text if too long (gTTS can fail over ~5000 chars)
    max_length = 4000
    trimmed_text = text[:max_length]

    try:
        # Ensure audio folder exists
        audio_folder = os.path.join("static", "audio")
        os.makedirs(audio_folder, exist_ok=True)

        filename = f"article_{article_id}.mp3"
        audio_path = os.path.join(audio_folder, filename)

        # Generate and save speech
        tts = gTTS(trimmed_text)
        tts.save(audio_path)

        print(f"[VoiceReader] Audio generated: {audio_path}")
        return f"/static/audio/{filename}"
    except Exception as e:
        print(f"[VoiceReader] Failed to generate audio: {e}")
        return None