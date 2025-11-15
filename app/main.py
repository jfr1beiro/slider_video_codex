"""CLI baseada em argparse para orquestrar ingestão, geração e exportação."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:  # pragma: no cover - configuração de ambiente
    sys.path.append(str(ROOT_DIR))

from converter.video_ingest import extract_frames
from converter.slide_generator import SlideGenerator
from app.viewmodel.session_state import SessionState
from app.view.screens.editor_screen import EditorScreen
from app.services.exporter import export_project

STATE = SessionState()
EDITOR = EditorScreen(STATE)


def _print(msg: str) -> None:
    """Wrapper simples para facilitar redirecionamento em testes."""

    print(msg)


def cmd_ingest(args: argparse.Namespace) -> None:
    frames = extract_frames(str(args.video), args.fps)
    STATE.set_slides(frames)
    _print(f"✔ {len(frames)} frames gerados em {frames[0].parent}")


def cmd_generate(args: argparse.Namespace) -> None:
    if not STATE.slide_paths:
        raise RuntimeError("Nenhum frame encontrado. Execute o comando 'ingest' primeiro.")

    generator = SlideGenerator(output_dir=args.output, image_size=(args.width, args.height))
    overlay_values: Optional[list[str]] = None
    if args.overlay:
        overlay_values = [args.overlay] * len(STATE.slide_paths)

    slides = generator.generate_from_frames(STATE.slide_paths, overlay_values)
    STATE.set_slides([item.slide_path for item in slides])
    _print(f"Slides gerados em {args.output}")


def cmd_export(args: argparse.Namespace) -> None:
    if not STATE.slide_paths:
        raise RuntimeError("Nenhum slide para exportar.")

    report = export_project(STATE.slide_paths, args.destination, {"theme": STATE.theme_mode})
    _print(f"Relatório criado em {report}")


def cmd_status(_args: argparse.Namespace) -> None:
    current = EDITOR.current_slide()
    lines = [
        "Resumo do SessionState:",
        f"- Slides: {len(STATE.slide_paths)}",
        f"- Tema: {STATE.theme_mode}",
        f"- Idioma: {STATE.language}",
        f"- Índice atual: {STATE.current_index}",
        f"- Slide atual: {current if current else '-'}",
    ]
    _print("\n".join(lines))


def cmd_ui(_args: argparse.Namespace) -> None:
    try:
        from app.ui.kivy_app import launch_kivy_app
    except RuntimeError as error:
        raise RuntimeError(
            "A UI Kivy requer dependências extras e acesso gráfico. Consulte o README."
        ) from error

    launch_kivy_app(STATE)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ferramentas MCP para o app de slides dinâmicos")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="Extrai frames do vídeo informado")
    ingest_parser.add_argument("video", type=Path)
    ingest_parser.add_argument("--fps", type=int, default=1, help="Frames por segundo a exportar", metavar="N")
    ingest_parser.set_defaults(func=cmd_ingest)

    generate_parser = subparsers.add_parser("generate-slides", help="Gera slides otimizados")
    generate_parser.add_argument("--output", type=Path, default=Path("build/slides"))
    generate_parser.add_argument("--width", type=int, default=1080)
    generate_parser.add_argument("--height", type=int, default=1920)
    generate_parser.add_argument("--overlay", type=str, default=None)
    generate_parser.set_defaults(func=cmd_generate)

    export_parser = subparsers.add_parser("export", help="Empacota slides e metadados")
    export_parser.add_argument("--destination", type=Path, default=Path("build/export"))
    export_parser.set_defaults(func=cmd_export)

    status_parser = subparsers.add_parser("status", help="Mostra o estado atual em memória")
    status_parser.set_defaults(func=cmd_status)

    ui_parser = subparsers.add_parser("ui", help="Inicia a interface em Kivy com drag-and-drop")
    ui_parser.set_defaults(func=cmd_ui)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return

    handler: Callable[[argparse.Namespace], None] = args.func
    handler(args)


if __name__ == "__main__":
    main()
