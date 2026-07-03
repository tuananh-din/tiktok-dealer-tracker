"""Normalize captions and match target keywords (diacritic-insensitive)."""
import re
import unicodedata


def normalize(text: str) -> str:
    """Lowercase, strip diacritics (Vietnamese etc.), collapse whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_patterns(keywords):
    """Turn each keyword into a flexible-spacing regex.

    'qrevo 2 pro' -> matches 'qrevo2pro', 'qrevo 2 pro', 'qrevo  2   pro'.
    Returns list of (original_keyword, compiled_pattern).
    """
    patterns = []
    for kw in keywords:
        norm = normalize(kw)
        parts = [re.escape(p) for p in norm.split(" ") if p]
        if not parts:
            continue
        patterns.append((kw, re.compile(r"\s*".join(parts))))
    return patterns


def match_keywords(caption: str, patterns):
    """Return the list of original keywords found in the caption."""
    norm = normalize(caption)
    return [kw for kw, pat in patterns if pat.search(norm)]
