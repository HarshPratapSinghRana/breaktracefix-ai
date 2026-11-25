import re
from typing import Any, Union, Dict, List

# Common PII & Sensitive Pattern Matchers
SENSITIVE_PATTERNS = [
    # OpenAI API Keys
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
    # Anthropic API Keys
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}", re.IGNORECASE), "[REDACTED_ANTHROPIC_KEY]"),
    # Generic API/Bearer Token Headers
    (re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{20,}", re.IGNORECASE), r"\1[REDACTED_BEARER_TOKEN]"),
    # AWS Access Key IDs
    (re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}\b"), "[REDACTED_AWS_KEY]"),
    # Credit Card Numbers (Luhn-candidate sequences)
    (re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"), "[REDACTED_CREDIT_CARD]"),
    # US Social Security Numbers
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    # Email Addresses
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"), "[REDACTED_EMAIL]"),
    # Password and Secret assignments in JSON/Config
    (re.compile(r'(?i)("?(?:password|secret|token|api_key|access_key|private_key)"?\s*[:=]\s*["\'])([^"\']{4,})(["\'])'), r'\1[REDACTED_SECRET]\3')
]

def redact_text(text: str) -> str:
    """Scrub sensitive PII, API tokens, and credentials from a text string."""
    if not text or not isinstance(text, str):
        return text
    
    redacted = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted

def redact_data(data: Any) -> Any:
    """Recursively scrub sensitive information from strings, dicts, lists, and primitives."""
    if isinstance(data, str):
        return redact_text(data)
    elif isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Check key name for sensitive terms
            lower_key = str(key).lower()
            if any(term in lower_key for term in ["password", "token", "secret", "authorization", "api_key", "private_key"]):
                cleaned[key] = "[REDACTED_SENSITIVE_FIELD]"
            else:
                cleaned[key] = redact_data(value)
        return cleaned
    elif isinstance(data, list):
        return [redact_data(item) for item in data]
    return data

