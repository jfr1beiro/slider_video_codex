"""Aplicativo Kivy com área de drag-and-drop para ingestão de vídeos."""

from __future__ import annotations

from pathlib import Path

from app.ui.dragdrop_controller import DragDropController
from app.viewmodel.session_state import SessionState


KV_LAYOUT = """
<DropArea@BoxLayout>:
    orientation: 'vertical'
    padding: 24
    spacing: 16
    canvas.before:
        Color:
            rgba: (.12, .14, .2, 1)
        RoundedRectangle:
            radius: [12]
            pos: self.pos
            size: self.size
    Label:
        id: status_label
        text: root.status
        font_size: '18sp'
        bold: True
    Label:
        id: detail_label
        text: root.detail
        color: (.8, .8, .8, 1)
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]

BoxLayout:
    orientation: 'vertical'
    padding: 32
    spacing: 20
    Label:
        text: 'MCP Robust – Arraste um vídeo para iniciar a ingestão'
        size_hint_y: None
        height: self.texture_size[1]
        color: (.9, .9, .9, 1)
    DropArea:
        id: drop_area
"""


def launch_kivy_app(session_state: SessionState | None = None) -> None:
    """Inicializa o app Kivy. Separado para evitar importações em tempo de teste."""

    try:  # Import tardio para não quebrar ambientes sem Kivy.
        from kivy.app import App
        from kivy.lang import Builder
        from kivy.properties import StringProperty
        from kivy.uix.boxlayout import BoxLayout
        from kivy.core.window import Window
    except Exception as exc:  # pragma: no cover - depende do ambiente gráfico
        raise RuntimeError(
            "Kivy não está instalado ou o ambiente gráfico não está disponível."
        ) from exc

    class DropArea(BoxLayout):  # type: ignore[misc]
        status = StringProperty("Arraste um vídeo MP4/AVI aqui")
        detail = StringProperty("Ou clique e solte um arquivo para iniciar o pipeline.")

    class MCPKivyApp(App):  # type: ignore[misc]
        def __init__(self, controller: DragDropController, **kwargs):
            super().__init__(**kwargs)
            self.controller = controller

        def build(self):
            Window.clearcolor = (0.07, 0.09, 0.12, 1)
            Window.bind(on_dropfile=self._handle_drop)
            return Builder.load_string(KV_LAYOUT)

        def _handle_drop(self, _window, file_path: bytes) -> None:
            decoded = Path(file_path.decode("utf-8"))
            drop_area = self.root.ids["drop_area"]
            try:
                result = self.controller.handle_drop(decoded)
            except FileNotFoundError:
                drop_area.status = "Arquivo não encontrado"
                drop_area.detail = str(decoded)
            except Exception as error:  # pragma: no cover - UI feedback
                drop_area.status = "Erro durante ingestão"
                drop_area.detail = str(error)
            else:
                drop_area.status = "Ingestão concluída"
                drop_area.detail = result["message"]

    controller = DragDropController(session_state=session_state or SessionState())
    MCPKivyApp(controller=controller).run()


__all__ = ["launch_kivy_app"]
