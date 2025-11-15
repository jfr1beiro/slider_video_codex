"""Exportação dos artefatos (slides + metadados) para posterior geração do APK."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from shutil import copy2
import json
from typing import Iterable


def export_project(slide_paths: Iterable[Path], destination: Path, metadata: dict | None = None) -> Path:
    """Copia os slides e gera um relatório JSON resumindo o projeto."""

    export_dir = Path(destination)
    export_dir.mkdir(parents=True, exist_ok=True)
    slides_dir = export_dir / "slides"
    slides_dir.mkdir(exist_ok=True)

    copied = []
    for slide in slide_paths:
        slide = Path(slide)
        if not slide.exists():
            continue
        target = slides_dir / slide.name
        copy2(slide, target)
        copied.append(target)

    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "slide_count": len(copied),
        "slides": [str(path) for path in copied],
        "metadata": metadata or {},
    }

    report_path = export_dir / "export_report.json"
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    placeholder = export_dir / "APK_BUILD.txt"
    placeholder.write_text(
        "Este diretório contém os ativos necessários para a próxima etapa do pipeline (Buildozer/GitHub Actions).\n"
    )

    return report_path
