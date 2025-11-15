"""Rotinas de ingestão e extração de frames dos vídeos de entrada."""

from __future__ import annotations

from pathlib import Path
import logging
from typing import List

try:  # pragma: no cover - import guard
    import cv2  # type: ignore
except Exception:  # pragma: no cover - handled durante execução
    cv2 = None  # type: ignore

LOGGER = logging.getLogger(__name__)


def extract_frames(video_path: str, fps: int) -> List[Path]:
    """Extrai frames em PNG a partir de ``video_path``.

    Args:
        video_path: caminho do vídeo de origem.
        fps: quantidade de frames por segundo a serem exportados.

    Returns:
        Lista com os caminhos dos frames gerados.
    """

    if fps <= 0:
        raise ValueError("fps deve ser maior que zero")

    source = Path(video_path)
    if not source.exists():
        raise FileNotFoundError(f"vídeo não encontrado: {video_path}")

    if cv2 is None:  # pragma: no cover - dependência externa
        raise RuntimeError("OpenCV não está instalado. Instale opencv-python.")

    output_dir = source.parent / f"{source.stem}_frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise ValueError("Não foi possível abrir o vídeo informado.")

    video_fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(int(video_fps // fps), 1)

    saved_paths: List[Path] = []
    frame_index = 0
    saved_index = 0

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break

            if frame_index % frame_interval == 0:
                frame_path = output_dir / f"{source.stem}_frame_{saved_index:05d}.png"
                if not cv2.imwrite(str(frame_path), frame):
                    raise RuntimeError(f"Falha ao gravar frame {saved_index} em disco")
                saved_paths.append(frame_path)
                saved_index += 1

            frame_index += 1
    finally:
        capture.release()

    if not saved_paths:
        raise RuntimeError("Nenhum frame foi extraído; verifique o vídeo e o fps informado.")

    LOGGER.info("%s frames gerados em %s", len(saved_paths), output_dir)
    return saved_paths
