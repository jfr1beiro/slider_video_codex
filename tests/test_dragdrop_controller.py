from pathlib import Path

import app.ui.dragdrop_controller as controller_module


class DummyState:
    def __init__(self):
        self.slide_paths = []

    def set_slides(self, slides):
        self.slide_paths = list(slides)


def test_controller_updates_session_state(monkeypatch, tmp_path):
    video = tmp_path / "video.mp4"
    video.write_bytes(b"demo")

    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    fake_frames = [frames_dir / "frame0.png", frames_dir / "frame1.png"]

    def fake_extract(path, fps):  # noqa: ARG001 - assinatura exigida
        assert Path(path) == video
        assert fps == 1
        for frame in fake_frames:
            frame.write_bytes(b"frame")
        return fake_frames

    monkeypatch.setattr(controller_module, "extract_frames", fake_extract)
    state = DummyState()

    controller = controller_module.DragDropController(session_state=state, fps=1)
    result = controller.handle_drop(video)

    assert state.slide_paths == fake_frames
    assert "2 frames" in result["message"]
