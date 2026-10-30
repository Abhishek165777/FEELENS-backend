import pytest
from utils.privacy_guard import ensure_non_sensitive

def test_rejects_long_numeric_identifier():
    with pytest.raises(ValueError):
        ensure_non_sensitive("My transaction reference is 123456789012")

def test_rejects_email():
    with pytest.raises(ValueError):
        ensure_non_sensitive("Contact me at person@example.com")

def test_allows_general_question():
    ensure_non_sensitive("What is an annual maintenance fee?")
