"""Reject likely sensitive information before it reaches Ollama."""
import re

_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.I), "IFSC code"),
    (re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.I), "PAN number"),
    (re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"), "12-digit identity number"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "card number"),
    (re.compile(r"\b\d{8,}\b"), "long numeric identifier or account number"),
    (re.compile(r"\b[A-Za-z0-9._-]{2,}@[A-Za-z][A-Za-z0-9.-]*\b"), "UPI ID"),
    (re.compile(r"\b(?:txn|transaction|utr|rrn|ref(?:erence)?|cheque|check)[\s:#-]*[A-Z0-9-]{5,}\b", re.I), "transaction/reference identifier"),
    (re.compile(r"(?<!\w)(?:\+?91[ -]?)?[6-9]\d{9}(?!\w)"), "phone number"),
]


def find_sensitive_data(text: str) -> list[str]:
    found = []
    for pattern, label in _PATTERNS:
        if pattern.search(text):
            found.append(label)
    return found


def ensure_non_sensitive(text: str) -> None:
    found = find_sensitive_data(text)
    if found:
        # Never include the matched value in the error message or logs.
        raise ValueError("Your message was not sent because it may contain sensitive information: " + ", ".join(found) + ". Remove those details and try again.")
