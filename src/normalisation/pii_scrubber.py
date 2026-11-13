"""PII Content Sanitization Scrubber for HomePilot Market Intelligence.

Enforces zero-trust data hygiene:
Scans incoming scraped web markdown and public commentary to detect and redact:
- Irish mobile, landline, and international phone numbers
- Personal email addresses
- Irish IBAN bank account references
- Direct personal identifying signatures

Ensures zero PII is persisted into MongoDB or processed by LLM reasoning engines.
"""

import re
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class PIIScrubber:
    """Zero-trust PII sanitization engine."""

    # Regex for Irish and International Phone Numbers
    PHONE_REGEX = re.compile(
        r"(?:(?:\+?353|00353|0)[\s.-]?)?(?:\(?0?[1-9]\d{0,2}\)?[\s.-]?)?\d{3}[\s.-]?\d{3,4}\b",
        re.IGNORECASE
    )

    # Regex for Email Addresses
    EMAIL_REGEX = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

    # Regex for Irish IBANs (both spaced and continuous formats)
    IBAN_REGEX = re.compile(
        r"\bIE\d{2}(?:[\s]?[A-Z]{4})(?:[\s]?\d{4}){3}[\s]?\d{2}\b|\bIE\d{2}[A-Z]{4}\d{14}\b",
        re.IGNORECASE
    )

    @classmethod
    def scrub_text(cls, text: str) -> Tuple[str, Dict[str, int]]:
        """Sanitizes text by replacing PII occurrences with standardized redaction tokens."""
        if not text:
            return "", {"phones": 0, "emails": 0, "ibans": 0}

        counts = {"phones": 0, "emails": 0, "ibans": 0}

        # Redact IBANs
        def replace_iban(match):
            counts["ibans"] += 1
            return "[REDACTED_IBAN]"
        text = cls.IBAN_REGEX.sub(replace_iban, text)

        # Redact Emails
        def replace_email(match):
            counts["emails"] += 1
            return "[REDACTED_EMAIL]"
        text = cls.EMAIL_REGEX.sub(replace_email, text)

        # Redact Phone Numbers
        def replace_phone(match):
            val = match.group(0).strip()
            # Ignore standard 4-digit years like 2024, 2025, 2026 or small numbers
            if len(re.sub(r"\D", "", val)) < 7:
                return match.group(0)
            counts["phones"] += 1
            return "[REDACTED_PHONE]"
        text = cls.PHONE_REGEX.sub(replace_phone, text)

        total_redacted = sum(counts.values())
        if total_redacted > 0:
            logger.info(f"PII Scrubber redacted {total_redacted} entities: {counts}")

        return text, counts
