from __future__ import annotations

import json
import re

from openai import OpenAI

from app.core.config import Settings, get_settings
from app.services.grouping.heuristic import HeuristicGrouper
from app.services.types import ClassificationResult, MetadataResult, PageContext, PageGroup


class LlmClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = OpenAI(
            base_url=self.settings.llm_base_url,
            api_key=self.settings.llm_api_key,
        )

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)


class LlmGrouper:
    def __init__(self, llm_client: LlmClient | None = None) -> None:
        self.llm = llm_client or LlmClient()
        self.fallback = HeuristicGrouper()

    def group_pages(self, pages: list[PageContext]) -> list[PageGroup]:
        if len(pages) <= 1:
            return self.fallback.group_pages(pages)

        page_summaries = []
        for page in pages:
            page_summaries.append(
                {
                    "page_id": page.page_id,
                    "page_number": page.page_number,
                    "top_lines": page.layout_features.get("top_lines", []),
                    "text_preview": page.text_content[:500],
                    "is_blank": page.is_blank,
                }
            )

        try:
            result = self.llm.complete_json(
                "You split scanned PDF pages into logical documents. Return JSON with key 'groups', "
                "each group has page_ids (array of strings), confidence (0-1), optional title.",
                json.dumps({"pages": page_summaries}),
            )
            groups: list[PageGroup] = []
            for group in result.get("groups", []):
                page_ids = [str(page_id) for page_id in group.get("page_ids", [])]
                if not page_ids:
                    continue
                page_numbers = [
                    page.page_number for page in pages if page.page_id in page_ids
                ]
                groups.append(
                    PageGroup(
                        page_ids=page_ids,
                        page_numbers=sorted(page_numbers),
                        confidence=float(group.get("confidence", 0.7)),
                        title=group.get("title"),
                    )
                )
            if groups:
                return groups
        except Exception:
            pass

        return self.fallback.group_pages(pages)


class LlmClassifier:
    def __init__(self, llm_client: LlmClient | None = None) -> None:
        self.llm = llm_client or LlmClient()

    def classify(self, pages_text: list[str]) -> ClassificationResult:
        combined = "\n".join(pages_text)[:6000]
        result = self.llm.complete_json(
            "Classify the document into one of: bill, contract, information, commercial, other. "
            "Return JSON with doc_type, confidence (0-1), signals (array of short strings).",
            combined,
        )
        doc_type = result.get("doc_type", "other")
        if doc_type not in {"bill", "contract", "information", "commercial", "other"}:
            doc_type = "other"
        return ClassificationResult(
            doc_type=doc_type,
            confidence=float(result.get("confidence", 0.6)),
            signals=[str(item) for item in result.get("signals", [])],
        )


class LlmExtractor:
    def __init__(self, llm_client: LlmClient | None = None) -> None:
        self.llm = llm_client or LlmClient()

    def extract_metadata(self, pages_text: list[str], doc_type: str) -> MetadataResult:
        combined = "\n".join(pages_text)[:6000]
        result = self.llm.complete_json(
            "Extract metadata from a scanned document. Return JSON with document_date (ISO date or null), "
            "sender_name, sender_normalized (lowercase simplified company name), confidence object with "
            "document_date and sender_name scores from 0-1, and extra_fields object.",
            f"Document type hint: {doc_type}\n\n{combined}",
        )
        document_date = result.get("document_date")
        if document_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(document_date)):
            document_date = None
        return MetadataResult(
            document_date=document_date,
            sender_name=result.get("sender_name"),
            sender_normalized=result.get("sender_normalized"),
            confidence={
                "document_date": float(result.get("confidence", {}).get("document_date", 0.6)),
                "sender_name": float(result.get("confidence", {}).get("sender_name", 0.6)),
            },
            extra_fields=result.get("extra_fields", {}),
        )
