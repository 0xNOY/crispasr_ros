"""Wake-gated confirmation intent classification for short HRI responses."""

from __future__ import annotations

from dataclasses import dataclass
import re
import time
from typing import Iterable, Optional


@dataclass(frozen=True)
class ConfirmationDecision:
    text: str
    intent: str
    command: str
    has_wake_word: bool
    is_within_wake_window: bool


def normalize_text(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def _normalize_terms(terms: Iterable[str]) -> list[str]:
    return [normalized for term in terms if (normalized := normalize_text(term))]


def _contains_term(text: str, term: str) -> bool:
    return re.search(rf"(^|\s){re.escape(term)}($|\s)", text) is not None


class ConfirmationGate:
    def __init__(
        self,
        wake_words: Iterable[str],
        positive_words: Iterable[str],
        negative_words: Iterable[str],
        wake_window_sec: float,
        require_wake_word: bool = True,
    ) -> None:
        self.wake_words = _normalize_terms(wake_words)
        self.positive_words = _normalize_terms(positive_words)
        self.negative_words = _normalize_terms(negative_words)
        self.wake_window_sec = wake_window_sec
        self.require_wake_word = require_wake_word
        self._awake_until = 0.0

    def consume(
        self, text: str, now: Optional[float] = None
    ) -> Optional[ConfirmationDecision]:
        now = time.time() if now is None else now
        normalized = normalize_text(text)
        if not normalized:
            return None

        has_wake_word = any(_contains_term(normalized, word) for word in self.wake_words)
        is_within_wake_window = now <= self._awake_until

        if has_wake_word:
            self._awake_until = now + self.wake_window_sec
            is_within_wake_window = True

        if self.require_wake_word and not (has_wake_word or is_within_wake_window):
            return None

        intent, command = self._classify_intent(normalized)
        if intent is None:
            return None

        self._awake_until = 0.0
        return ConfirmationDecision(
            text=text,
            intent=intent,
            command=command,
            has_wake_word=has_wake_word,
            is_within_wake_window=is_within_wake_window,
        )

    def _classify_intent(self, text: str) -> tuple[Optional[str], str]:
        for word in self.negative_words:
            if _contains_term(text, word):
                return "negative", word

        for word in self.positive_words:
            if _contains_term(text, word):
                return "positive", word

        return None, ""
