"""Controlador reutilizável para UI drag-and-drop em Kivy."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from app.viewmodel.session_state import SessionState
from converter.video_ingest import extract_frames


class DragDropController:
    """Processa arquivos derrubados na interface visual."""

    def __init__(self, session_state: SessionState | None = None, fps: int = 1) -> None:
        self.session_state = session_state or SessionState()
        self.fps = fps

    def handle_drop(self, filepath: str | bytes | Path) -> dict[str, Iterable[Path]]:
        """Extrai frames do vídeo arrastado e atualiza o SessionState."""

        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(path)

        frames = extract_frames(str(path), self.fps)
        self.session_state.set_slides(frames)
        message = f"{len(frames)} frames extraídos de {path.name}"
        return {"frames": frames, "message": message}
