"""Camada de interação para operações básicas de edição."""

from __future__ import annotations

from pathlib import Path
from typing import List

from app.services.exporter import export_project
from app.viewmodel.session_state import SessionState


class EditorScreen:
    """Implementa operações essenciais solicitadas pelo MCP."""

    def __init__(self, state: SessionState) -> None:
        self.state = state
        self.state.subscribe(self._on_state_change)
        self.last_event: str | None = None

    def _on_state_change(self, _: SessionState) -> None:
        self.last_event = "state_updated"

    def reorder_slides(self, source_index: int, target_index: int) -> None:
        slides = self.state.slide_paths
        if not slides:
            return
        source_index = max(0, min(source_index, len(slides) - 1))
        target_index = max(0, min(target_index, len(slides) - 1))
        slide = slides.pop(source_index)
        slides.insert(target_index, slide)
        self.state.set_slides(slides)

    def delete_slide(self, index: int) -> None:
        slides = self.state.slide_paths
        if not slides:
            return
        index = max(0, min(index, len(slides) - 1))
        slides.pop(index)
        self.state.set_slides(slides)

    def duplicate_slide(self, index: int) -> None:
        slides = self.state.slide_paths
        if not slides:
            return
        index = max(0, min(index, len(slides) - 1))
        slide = slides[index]
        duplicate = Path(slide.parent / f"{slide.stem}_copy{slide.suffix}")
        duplicate.write_bytes(slide.read_bytes())
        slides.insert(index + 1, duplicate)
        self.state.set_slides(slides)

    def export(self, destination: Path, extra_metadata: dict | None = None) -> Path:
        return export_project(self.state.slide_paths, destination, extra_metadata)

    def current_slide(self) -> Path | None:
        if not self.state.slide_paths:
            return None
        return self.state.slide_paths[self.state.current_index]

    def available_slides(self) -> List[Path]:
        return list(self.state.slide_paths)
