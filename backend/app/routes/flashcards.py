"""Flashcard endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from ..models import FlashcardDeck, Resource
from ..schemas import FlashcardDeckSchema
from ..services.flashcard_service import FlashcardServiceError, flashcard_service

flashcard_bp = Blueprint("flashcards", __name__)
deck_schema = FlashcardDeckSchema()


@flashcard_bp.post("/generate")
@jwt_required()
def generate_flashcards():
    """Generate flashcards via Gemini AI."""
    payload = request.get_json() or {}
    resource_id = payload.get("resource_id")
    if not resource_id:
        return jsonify({"message": "resource_id is required"}), 400
    resource = Resource.query.get_or_404(resource_id)
    try:
        deck = flashcard_service.generate_deck(owner=current_user, resource=resource)
    except FlashcardServiceError as exc:
        return jsonify({"message": str(exc)}), 400
    return deck_schema.jsonify(deck), 201


@flashcard_bp.get("/<int:deck_id>")
@jwt_required()
def get_deck(deck_id: int):
    """Retrieve a specific flashcard deck."""
    deck = FlashcardDeck.query.get_or_404(deck_id)
    if deck.owner_id != current_user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Not authorized"}), 403
    return deck_schema.jsonify(deck), 200


@flashcard_bp.put("/<int:deck_id>")
@jwt_required()
def update_deck(deck_id: int):
    """Replace flashcards in a deck."""
    deck = FlashcardDeck.query.get_or_404(deck_id)
    if deck.owner_id != current_user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Not authorized"}), 403
    cards = request.json.get("cards")
    if not cards:
        return jsonify({"message": "cards are required"}), 400
    deck = flashcard_service.update_cards(deck=deck, cards=cards)
    return deck_schema.jsonify(deck), 200
