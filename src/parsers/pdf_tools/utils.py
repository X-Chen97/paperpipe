from typing import List, Callable

def clean_text(text: str) -> str:
    """Remove extra whitespace and normalize text."""
    return ' '.join(text.split()).strip()

def is_abstract_header(text: str) -> bool:
    """Check if text is an abstract header."""
    return ''.join(text.split()).lower().startswith('abstract')

def filter_abnormal_words(text: str, patterns: List[Callable[[str], bool]]) -> str:
    """Filter out abnormal words based on patterns."""
    words = text.split()
    filtered_words = []
    for word in words:
        if any(pattern(word) for pattern in patterns):
            break
        filtered_words.append(word)
    return ' '.join(filtered_words)

# Constants
DEFAULT_ABNORMAL_PATTERNS = [
    lambda w: w.startswith('http'),
    lambda w: '©' in w,
    lambda w: 'copyright' in w.lower(),
    lambda w: w.lower().startswith('doi:')
]