"""Gemini generative AI integration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, List

import google.generativeai as genai
from flask import current_app

from ..models import Resource


@dataclass
class FlashcardItem:
    """Structured flashcard output."""

    question: str
    answer: str


@dataclass
class FlashcardPayload:
    """AI response for flashcards and deck metadata."""

    cards: List[FlashcardItem]
    summary: str


class GeminiServiceError(Exception):
    """Raised when Gemini operations fail."""


class GeminiService:
    """Encapsulates communication with Google Gemini."""

    def __init__(self) -> None:
        self._model_name = "gemini-1.5-pro"

    def _init_client(self) -> genai.GenerativeModel:
        api_key = current_app.config.get("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            raise GeminiServiceError("Gemini API key not configured")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(self._model_name)

    def chunk_resource(self, resource: Resource, *, chunk_size: int = 800) -> list[str]:
        """Chunk resource description for AI processing."""
        text = resource.description or ""
        if not text:
            raise GeminiServiceError("Resource missing textual content")
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def generate_flashcards(self, chunks: Iterable[str]) -> FlashcardPayload:
        """Generate flashcards and summary from text chunks."""
        model = self._init_client()
        prompt = (
            "You are an instructional designer. Given the following study text, generate "
            "exactly 5 high-quality flashcards with question and answer fields in JSON list format. "
            "Also produce a concise summary paragraph capturing the key concept. "
            "Respond strictly as JSON with keys 'flashcards' and 'summary'."
        )
        combined_text = "\n\n".join(chunks)
        response = model.generate_content(f"{prompt}\n\nText:\n{combined_text}")
        if not response or not response.text:
            raise GeminiServiceError("Empty response from Gemini")
        try:
            payload = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise GeminiServiceError("Gemini returned invalid JSON") from exc

        cards = [
            FlashcardItem(question=item["question"], answer=item["answer"])
            for item in payload["flashcards"]
        ]
        summary = payload["summary"]
        return FlashcardPayload(cards=cards, summary=summary)


gemini_service = GeminiService()
