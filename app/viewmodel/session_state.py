"""Gerencia o estado global do projeto durante a edição."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List

StateObserver = Callable[["SessionState"], None]


@dataclass
class SessionState:
    slide_paths: List[Path] = field(default_factory=list)
    theme_mode: str = "dark"
    language: str = "pt-BR"
    current_index: int = 0
    _observers: List[StateObserver] = field(default_factory=list, init=False, repr=False)

    def subscribe(self, observer: StateObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: StateObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self) -> None:
        for observer in list(self._observers):
            observer(self)

    def set_slides(self, slides: List[Path]) -> None:
        self.slide_paths = slides
        self.current_index = 0
        self._notify()

    def append_slides(self, slides: List[Path]) -> None:
        self.slide_paths.extend(slides)
        self._notify()

    def select(self, index: int) -> None:
        if not self.slide_paths:
            self.current_index = 0
            return
        self.current_index = max(0, min(index, len(self.slide_paths) - 1))
        self._notify()

    def next_slide(self) -> None:
        self.select(self.current_index + 1)

    def previous_slide(self) -> None:
        self.select(self.current_index - 1)

    def toggle_theme(self) -> None:
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self._notify()

    def set_language(self, language: str) -> None:
        self.language = language
        self._notify()
