from pathlib import Path
import types

import converter.video_ingest as video_ingest


def _build_stub(frame_count=5):
    class DummyCapture:
        def __init__(self):
            self._frames = [object() for _ in range(frame_count)]
            self._index = 0

        def isOpened(self):
            return True

        def read(self):
            if self._index >= len(self._frames):
                return False, None
            frame = self._frames[self._index]
            self._index += 1
            return True, frame

        def get(self, _):
            return 30.0

        def release(self):
            pass

    written_files = []

    def imwrite(path, _frame):
        Path(path).write_bytes(b"fake")
        written_files.append(Path(path))
        return True

    stub = types.SimpleNamespace(
        VideoCapture=lambda _: DummyCapture(),
        CAP_PROP_FPS=5,
        imwrite=imwrite,
    )

    return stub, written_files


def test_extract_frames_generates_expected_files(monkeypatch, tmp_path):
    video_file = tmp_path / "demo.mp4"
    video_file.write_bytes(b"data")
    stub, written_files = _build_stub()
    monkeypatch.setattr(video_ingest, "cv2", stub)

    frames = video_ingest.extract_frames(str(video_file), fps=2)

    assert len(frames) == len(written_files)
    assert all(path.exists() for path in frames)
    assert frames[0].parent.name == "demo_frames"


def test_extract_frames_validates_fps(tmp_path):
    video_file = tmp_path / "demo.mp4"
    video_file.write_bytes(b"data")
    try:
        video_ingest.extract_frames(str(video_file), fps=0)
    except ValueError:
        assert True
    else:  # pragma: no cover - defensive
        raise AssertionError("Deveria ter lançado ValueError")
