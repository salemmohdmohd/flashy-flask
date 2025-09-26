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
        """Chunk resource content for AI processing."""
        if chunk_size <= 0:
            raise GeminiServiceError("chunk_size must be positive")

        text_source = (resource.text_content or resource.description or "").strip()
        if not text_source:
            raise GeminiServiceError("Resource missing textual content")

        words = text_source.split()
        if not words:
            raise GeminiServiceError("Resource text could not be tokenized")

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # include a space
            if current_chunk and current_length + word_length > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

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

        if "flashcards" not in payload or "summary" not in payload:
            raise GeminiServiceError("Gemini response missing required fields")

        cards: list[FlashcardItem] = []
        for item in payload["flashcards"]:
            question = item.get("question")
            answer = item.get("answer")
            if not question or not answer:
                continue
            cards.append(FlashcardItem(question=question, answer=answer))
        if not cards:
            raise GeminiServiceError("No flashcards produced by Gemini")
        summary = payload["summary"]
        return FlashcardPayload(cards=cards, summary=summary)


gemini_service = GeminiService()
