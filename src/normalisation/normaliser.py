import re
import hashlib
from typing import Optional, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
from src.models.document import ExtractedDocument

class DocumentNormaliser:
    """Cleans HTML/Markdown, strips layout boilerplate, extracts metadata, and computes canonical hashes."""

    BOILERPLATE_PATTERNS = [
        r"(?i)cookie(s)?\s*(policy|settings|notice|consent)",
        r"(?i)all\s*rights\s*reserved",
        r"(?i)privacy\s*policy",
        r"(?i)terms\s*(and|&)\s*conditions",
        r"(?i)skip\s*to\s*(main\s*)?content",
    ]

    @classmethod
    def clean_html(cls, html_content: str) -> Tuple[str, str]:
        """Parses raw HTML, removes script/style/nav elements, and returns (title, clean_text_or_markdown)."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Decompose non-content tags
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "form"]):
            element.decompose()

        # Extract main content container if present
        main = soup.find("main") or soup.find("article") or soup.find("div", {"id": re.compile(r"content|main", re.I)})
        target_soup = main if main else soup.body or soup

        # Simple text/markdown conversion
        lines = []
        for p in target_soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"]):
            text = p.get_text(separator=" ", strip=True)
            if not text:
                continue
            
            # Check for cookie/footer boilerplate
            if any(re.search(bp, text) for bp in cls.BOILERPLATE_PATTERNS) and len(text) < 120:
                continue

            tag_name = p.name.lower()
            if tag_name == "h1":
                lines.append(f"\n# {text}\n")
            elif tag_name == "h2":
                lines.append(f"\n## {text}\n")
            elif tag_name == "h3":
                lines.append(f"\n### {text}\n")
            elif tag_name == "li":
                lines.append(f"- {text}")
            else:
                lines.append(f"\n{text}\n")

        clean_markdown = "\n".join(lines).strip()
        return title, clean_markdown

    @classmethod
    def normalise(cls, source_id: str, url: str, raw_content: str, is_html: bool = True, title: str = "", published_at: Optional[datetime] = None) -> ExtractedDocument:
        """Converts raw HTML or text into a normalized ExtractedDocument model."""
        if is_html:
            extracted_title, markdown = cls.clean_html(raw_content)
            title = title or extracted_title
        else:
            markdown = raw_content.strip()

        return ExtractedDocument.create(
            source_id=source_id,
            url=url,
            markdown=markdown,
            title=title,
            published_at=published_at
        )

    @classmethod
    def compute_hash(cls, content: str) -> str:
        """Computes SHA-256 digest of clean content string."""
        return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()
