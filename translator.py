from deep_translator import GoogleTranslator, LibreTranslator


def translate_text(text, target_language='en'):
    """
    Translates the given text into the specified target language.

    Parameters:
        text (str): The input text to translate.
        target_language (str): The language code to translate the text into
                               (e.g., 'en' for English, 'fr' for French, 'rw' for Kinyarwanda).

    Returns:
        str: Translated text if successful, otherwise original text.

    Notes:
        - Uses GoogleTranslator by default.
        - Falls back to LibreTranslator if needed or when translating to 'rw' (Kinyarwanda).
        - If all translations fail, returns the original text.
    """
    try:
        # Special handling for Kinyarwanda using LibreTranslate
        if target_language == 'rw':
            print("Translating using LibreTranslate (Kinyarwanda)...")
            translated = LibreTranslator(source='auto', target='rw').translate(text)
        else:
            print(f"Translating using GoogleTranslator to '{target_language}'...")
            translated = GoogleTranslator(source='auto', target=target_language).translate(text)

        return translated

    except Exception as e1:
        print(f"[Primary Translator Failed] {e1}")

        # Fallback: Try LibreTranslate for all other languages
        try:
            print(f"Trying fallback with LibreTranslate to '{target_language}'...")
            translated = LibreTranslator(source='auto', target=target_language).translate(text)
            return translated
        except Exception as e2:
            print(f"[Fallback Translator Failed] {e2}")
            print("Returning original text.")
            return text  # Return original text as last resort
