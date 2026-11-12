import re
import string
import unicodedata

# Comprehensive stopwords set to ensure zero-dependency fallback if NLTK corpus is not downloaded
DEFAULT_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
    "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

def clean_text(text: str) -> str:
    """
    Normalizes unicode, removes non-printable characters, normalizes line breaks and whitespace.
    """
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Replace common bullet characters with newline or standard bullet
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u00B7\u25CF\u25AA\u25B6\u27A4]', '\n• ', text)
    # Remove control characters except newlines/tabs
    text = "".join(ch for ch in text if ch in string.printable or ch == '\n' or ch == '\t')
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def tokenize_words(text: str) -> list[str]:
    """
    Tokenizes text into words preserving programming terms like C++, C#, .NET, Node.js.
    """
    if not text:
        return []
    # Match words, including terms with ++, #, dots, hyphens
    tokens = re.findall(r'[a-zA-Z0-9+#.-]+', text)
    return tokens

def remove_stopwords(tokens: list[str]) -> list[str]:
    """
    Removes stopwords while preserving tech-specific terminology.
    """
    return [t for t in tokens if t.lower() not in DEFAULT_STOPWORDS and len(t) > 1]

def preprocess_for_vectorizer(text: str) -> str:
    """
    Returns clean lowercase alphanumeric text suitable for TF-IDF / Scikit-learn models.
    """
    clean = clean_text(text).lower()
    # Replace punctuation except technical characters
    clean = re.sub(r'[^a-z0-9\s+#.-]', ' ', clean)
    tokens = tokenize_words(clean)
    filtered = remove_stopwords(tokens)
    return " ".join(filtered)
