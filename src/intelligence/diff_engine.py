import re
import difflib
from typing import Optional, List, Dict, Any, Tuple
from src.models.change import ContentChange, SemanticDelta
from src.models.document import ExtractedDocument

class SemanticDiffEngine:
    """Detects substantive changes between document versions while filtering out layout/formatting noise."""

    NUMERIC_PATTERN = re.compile(r"€?\d+(?:,\d{3})*(?:\.\d+)?%?")

    @classmethod
    def compare_documents(cls, old_doc: ExtractedDocument, new_doc: ExtractedDocument) -> Optional[ContentChange]:
        """Compares previous and current versions of a document. Returns a ContentChange if meaningful."""
        if old_doc.content_hash == new_doc.content_hash:
            return None # Zero delta

        old_lines = [l.strip() for l in old_doc.markdown.splitlines() if l.strip()]
        new_lines = [l.strip() for l in new_doc.markdown.splitlines() if l.strip()]

        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        added_lines: List[str] = []
        removed_lines: List[str] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "replace":
                removed_lines.extend(old_lines[i1:i2])
                added_lines.extend(new_lines[j1:j2])
            elif tag == "delete":
                removed_lines.extend(old_lines[i1:i2])
            elif tag == "insert":
                added_lines.extend(new_lines[j1:j2])

        # Filter out minor lines (e.g. less than 10 characters)
        meaningful_adds = [l for l in added_lines if len(l) > 15]
        meaningful_removes = [l for l in removed_lines if len(l) > 15]

        # Extract numeric differences
        old_numbers = set(cls.NUMERIC_PATTERN.findall(" ".join(removed_lines)))
        new_numbers = set(cls.NUMERIC_PATTERN.findall(" ".join(added_lines)))
        numeric_deltas = [
            {"removed_value": n} for n in (old_numbers - new_numbers)
        ] + [
            {"added_value": n} for n in (new_numbers - old_numbers)
        ]

        # Classify change type
        if numeric_deltas:
            change_type = "pricing_update" if any("€" in str(d) for d in numeric_deltas) else "fact_change"
        elif any(re.search(r"(?i)scheme|rule|criteria|eligib|deadline|law|bill", l) for l in meaningful_adds):
            change_type = "policy_revision"
        elif any(re.search(r"(?i)january|february|march|april|may|june|july|august|september|october|november|december|\d{4}", l) for l in meaningful_adds):
            change_type = "date_change"
        elif not meaningful_adds and not meaningful_removes:
            change_type = "trivial_layout"
        else:
            change_type = "fact_change"

        if change_type == "trivial_layout":
            return None # Ignore trivial formatting changes

        delta = SemanticDelta(
            summary=f"Detected {change_type}: {len(meaningful_adds)} statements added, {len(meaningful_removes)} removed.",
            added_facts=meaningful_adds[:5],
            removed_facts=meaningful_removes[:5],
            numeric_deltas=numeric_deltas[:5]
        )

        change_id = f"chg_{new_doc.doc_id}_{new_doc.version}"
        return ContentChange(
            change_id=change_id,
            doc_id=new_doc.doc_id,
            url=new_doc.url,
            previous_hash=old_doc.content_hash,
            current_hash=new_doc.content_hash,
            change_type=change_type,
            semantic_delta=delta,
            processed_for_insights=False
        )
