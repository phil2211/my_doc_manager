from __future__ import annotations

from app.services.pdf_utils import FIRST_PAGE_PATTERN, hash_distance
from app.services.types import PageContext, PageGroup


class HeuristicGrouper:
    def group_pages(self, pages: list[PageContext]) -> list[PageGroup]:
        if not pages:
            return []

        groups: list[PageGroup] = []
        current_page_ids: list[str] = []
        current_page_numbers: list[int] = []
        current_confidence = 0.85

        def flush_group(confidence: float = 0.85) -> None:
            nonlocal current_page_ids, current_page_numbers, current_confidence
            if current_page_ids:
                title = self._derive_title(pages, current_page_ids[0])
                groups.append(
                    PageGroup(
                        page_ids=list(current_page_ids),
                        page_numbers=list(current_page_numbers),
                        confidence=confidence,
                        title=title,
                    )
                )
            current_page_ids = []
            current_page_numbers = []
            current_confidence = 0.85

        previous: PageContext | None = None
        for page in pages:
            if page.is_blank:
                flush_group(0.95)
                previous = None
                continue

            should_split = False
            split_confidence = 0.75

            if previous is not None:
                prev_hash = previous.layout_features.get("perceptual_hash", "")
                curr_hash = page.layout_features.get("perceptual_hash", "")
                if hash_distance(prev_hash, curr_hash) > 18:
                    should_split = True
                    split_confidence = 0.7

                if FIRST_PAGE_PATTERN.search(page.text_content):
                    should_split = True
                    split_confidence = 0.9

                prev_top = " ".join(previous.layout_features.get("top_lines", [])).lower()
                curr_top = " ".join(page.layout_features.get("top_lines", [])).lower()
                if prev_top and curr_top and prev_top[:40] != curr_top[:40]:
                    shared = set(prev_top.split()) & set(curr_top.split())
                    if len(shared) < 2:
                        should_split = True
                        split_confidence = min(split_confidence, 0.65)

            if should_split and current_page_ids:
                flush_group(current_confidence)
                current_confidence = split_confidence

            current_page_ids.append(page.page_id)
            current_page_numbers.append(page.page_number)
            previous = page

        flush_group(current_confidence)
        return groups

    def _derive_title(self, pages: list[PageContext], first_page_id: str) -> str | None:
        for page in pages:
            if page.page_id == first_page_id:
                for line in page.layout_features.get("top_lines", []):
                    if len(line) > 5:
                        return line[:120]
                if page.text_content:
                    first_line = page.text_content.splitlines()[0].strip()
                    return first_line[:120] if first_line else None
        return None
