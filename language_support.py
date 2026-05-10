"""Language catalog and lightweight detection helpers for Justin AI."""

LANGUAGES = {
    "af": "Afrikaans",
    "am": "Amharic",
    "ar": "Arabic",
    "az": "Azerbaijani",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "ceb": "Cebuano",
    "co": "Corsican",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "eo": "Esperanto",
    "es": "Spanish",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "fy": "Frisian",
    "ga": "Irish",
    "gd": "Scots Gaelic",
    "gl": "Galician",
    "gu": "Gujarati",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hmn": "Hmong",
    "hr": "Croatian",
    "ht": "Haitian Creole",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "ig": "Igbo",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "jv": "Javanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "ku": "Kurdish",
    "ky": "Kyrgyz",
    "la": "Latin",
    "lb": "Luxembourgish",
    "lo": "Lao",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mg": "Malagasy",
    "mi": "Maori",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "ms": "Malay",
    "mt": "Maltese",
    "my": "Myanmar Burmese",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "ny": "Chichewa",
    "or": "Odia",
    "pa": "Punjabi",
    "pl": "Polish",
    "ps": "Pashto",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "rw": "Kinyarwanda",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sm": "Samoan",
    "sn": "Shona",
    "so": "Somali",
    "sq": "Albanian",
    "sr": "Serbian",
    "st": "Sesotho",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "tg": "Tajik",
    "th": "Thai",
    "tk": "Turkmen",
    "tl": "Filipino Tagalog",
    "tr": "Turkish",
    "tt": "Tatar",
    "ug": "Uyghur",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "zh": "Chinese",
    "zu": "Zulu",
}

PRIORITY_LANGUAGES = {
    "rw": LANGUAGES["rw"],
    "en": LANGUAGES["en"],
    "fr": LANGUAGES["fr"],
}

LANGUAGE_ALIASES = {
    "kinyarwanda": "rw",
    "ikinyarwanda": "rw",
    "rwanda": "rw",
    "rw": "rw",
    "english": "en",
    "anglais": "en",
    "icyongereza": "en",
    "en": "en",
    "french": "fr",
    "francais": "fr",
    "français": "fr",
    "igifaransa": "fr",
    "fr": "fr",
}

LANGUAGE_MARKERS = {
    "rw": {
        "amakuru", "muraho", "bite", "umeze", "neza", "ndashaka", "mfasha",
        "urakoze", "ikinyarwanda", "igisubizo", "ibibazo", "gusobanura",
        "ndashimira", "banyarwanda", "u Rwanda", "rwanda", "nyamuneka",
    },
    "fr": {
        "bonjour", "salut", "merci", "comment", "pourquoi", "reponds",
        "réponds", "francais", "français", "aide", "avec", "dans", "est-ce",
        "s'il", "vous", "pouvez", "expliquer",
    },
    "en": {
        "hello", "hi", "thanks", "please", "what", "why", "how", "can",
        "could", "help", "explain", "english", "answer",
    },
}

LOCALIZED_MESSAGES = {
    "image_ready": {
        "rw": "Dore ifoto wakoze.",
        "fr": "Voici votre image générée.",
        "en": "Here is your generated image.",
    },
    "audio_ready": {
        "rw": "Dore dosiye y'amajwi wakoze (wasabye amasegonda {seconds}).",
        "fr": "Voici votre fichier audio généré ({seconds} secondes demandées).",
        "en": "Here is your generated audio file ({seconds} seconds requested).",
    },
    "video_ready": {
        "rw": "Dore videwo wakoze (wasabye amasegonda {seconds}).",
        "fr": "Voici votre vidéo générée ({seconds} secondes demandées).",
        "en": "Here is your generated video ({seconds} seconds requested).",
    },
    "fallback": {
        "rw": "Mbabarira, sinabashije gukora igisubizo. Ongera ugerageze.",
        "fr": "Désolé, je n'ai pas pu générer de réponse. Veuillez réessayer.",
        "en": "Sorry, I couldn't generate a response. Please try again.",
    },
}


def detect_language(text):
    """Return a best-effort language code, prioritizing Kinyarwanda, English, and French."""
    normalized = text.strip().lower()
    if not normalized:
        return "en"

    for alias, code in LANGUAGE_ALIASES.items():
        if re_search_word(alias, normalized):
            return code

    scores = {}
    for code, markers in LANGUAGE_MARKERS.items():
        scores[code] = sum(1 for marker in markers if re_search_word(marker.lower(), normalized))

    best_code = max(scores, key=scores.get)
    return best_code if scores[best_code] > 0 else "en"


def language_name(code):
    return LANGUAGES.get(code, LANGUAGES["en"])


def language_instruction(user_message):
    code = detect_language(user_message)
    name = language_name(code)
    priority = ", ".join(f"{name} ({code})" for code, name in PRIORITY_LANGUAGES.items())
    return (
        f"The user's detected language is {name} ({code}). "
        f"Reply in {name}. Match the user's language even when conversation history uses another language. "
        f"Justin AI supports the world language catalog and should especially handle {priority}. "
        "If the user asks to translate or explicitly requests another language, follow that request."
    )


def localized_message(key, language_code, **kwargs):
    messages = LOCALIZED_MESSAGES.get(key, {})
    template = messages.get(language_code) or messages["en"]
    return template.format(**kwargs)


def re_search_word(needle, haystack):
    import re

    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack, re.IGNORECASE) is not None
