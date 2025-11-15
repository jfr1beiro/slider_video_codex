"""Geração de slides otimizados a partir dos frames extraídos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence
import logging
import shutil

try:  # pragma: no cover - import guard
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover - handled dinamicamente
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    ImageFont = None  # type: ignore

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class SlideMetadata:
    """Representa o resultado da geração de um slide."""

    source_frame: Path
    slide_path: Path
    overlay_text: str | None = None


class SlideGenerator:
    """Aplica transformações básicas e overlays de texto."""

    def __init__(
        self,
        output_dir: Path,
        image_size: tuple[int, int] = (1080, 1920),
        background_color: str = "black",
        text_color: str = "white",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_size = image_size
        self.background_color = background_color
        self.text_color = text_color

    def _prepare_image(self, frame_path: Path):
        if Image is None:
            return None
        image = Image.open(frame_path).convert("RGB")
        image = image.resize(self.image_size)
        return image

    def _apply_overlay(self, image, text: str | None):
        if Image is None or not text:
            return image
        draw = ImageDraw.Draw(image)
        width, height = image.size
        font_size = max(int(height * 0.04), 18)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except OSError:  # pragma: no cover - fallback
            font = ImageFont.load_default()
        # Usa textbbox() ao invés de textsize() (removido no Pillow 10+)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding = 32
        x = max((width - text_width) // 2, padding)
        y = height - text_height - padding
        draw.rectangle(
            [(padding // 2, y - padding // 2), (width - padding // 2, y + text_height + padding // 2)],
            fill=self.background_color,
            outline=None,
        )
        draw.text((x, y), text, font=font, fill=self.text_color)
        return image

    def _save_slide(self, frame_path: Path, image, overlay_text: str | None) -> Path:
        slide_path = self.output_dir / f"{frame_path.stem}_slide.png"
        if Image is None:
            shutil.copy2(frame_path, slide_path)
            if overlay_text:
                slide_path.with_suffix(".txt").write_text(overlay_text)
        else:
            image.save(slide_path, format="PNG")
        return slide_path

    def generate_slide(self, frame_path: Path, overlay_text: str | None = None) -> SlideMetadata:
        image = self._prepare_image(frame_path)
        image = self._apply_overlay(image, overlay_text)
        slide_path = self._save_slide(frame_path, image, overlay_text)
        LOGGER.debug("Slide salvo em %s", slide_path)
        return SlideMetadata(source_frame=frame_path, slide_path=slide_path, overlay_text=overlay_text)

    def generate_from_frames(
        self,
        frames: Sequence[Path],
        overlays: Iterable[str | None] | None = None,
    ) -> List[SlideMetadata]:
        overlays_list = list(overlays or [])
        results: List[SlideMetadata] = []
        for index, frame in enumerate(frames):
            overlay_text = overlays_list[index] if index < len(overlays_list) else None
            results.append(self.generate_slide(frame, overlay_text))
        return results
