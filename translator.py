from deep_translator import GoogleTranslator, LibreTranslator

def translate_text(text, target_language='en'):
    """
    Translates text into the specified target_language.
    Supports GoogleTranslator and LibreTranslate with fallback.
    """
    try:
        # Kinyarwanda needs LibreTranslate
        if target_language == 'rw':
            print("Translating using LibreTranslate (Kinyarwanda)...")
            translated = LibreTranslator(source='auto', target='rw').translate(text)
        else:
            print(f"Translating using GoogleTranslator to {target_language}...")
            translated = GoogleTranslator(source='auto', target=target_language).translate(text)
        return translated
    except Exception as e1:
        print(f"Primary translation failed: {e1}")
        try:
            print("Trying LibreTranslate as fallback...")
            translated = LibreTranslator(source='auto', target=target_language).translate(text)
            return translated
        except Exception as e2:
            print(f"Translation completely failed: {e2}")
            return text  # Return original text as fallback