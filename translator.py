from deep_translator import GoogleTranslator, LibreTranslator


def translate_text(text, target_language='en'):
    """
    Translates text only if needed.
    """
    if not text or target_language == 'en':
        return text
        # 🛑 Skip translation if target is English or empty

    try:
        if target_language == 'rw':
            print("Translating using LibreTranslate (Kinyarwanda)...")
            return LibreTranslator(source='auto', target='rw').translate(text)
        else:
            print(f"Translating using GoogleTranslator to {target_language}...")
            return GoogleTranslator(source='auto', target=target_language).translate(text)
    except Exception as e1:
        print(f"Primary translation failed: {e1}")
        try:
            print("Trying LibreTranslate as fallback...")
            return LibreTranslator(source='auto', target=target_language).translate(text)
        except Exception as e2:
            print(f"Translation completely failed: {e2}")
            return text
