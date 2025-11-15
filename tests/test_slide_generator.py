from pathlib import Path

from converter.slide_generator import SlideGenerator


def _create_frame(path: Path) -> None:
    path.write_bytes(b"frame-data")


def test_generate_slide_creates_file(tmp_path):
    frame = tmp_path / "frame.bin"
    _create_frame(frame)
    generator = SlideGenerator(output_dir=tmp_path / "slides", image_size=(50, 50))

    metadata = generator.generate_slide(frame, "Teste")

    assert metadata.slide_path.exists()
    assert metadata.overlay_text == "Teste"
    if metadata.slide_path.with_suffix(".txt").exists():
        assert metadata.slide_path.with_suffix(".txt").read_text() == "Teste"


def test_generate_from_frames_respects_overlay_list(tmp_path):
    frames = []
    for index in range(3):
        frame = tmp_path / f"frame_{index}.bin"
        _create_frame(frame)
        frames.append(frame)

    generator = SlideGenerator(output_dir=tmp_path / "slides")
    overlays = ["Primeiro", None, "Terceiro"]

    metadata_list = generator.generate_from_frames(frames, overlays)

    assert len(metadata_list) == 3
    assert metadata_list[0].overlay_text == "Primeiro"
    assert metadata_list[1].overlay_text is None
    assert metadata_list[2].overlay_text == "Terceiro"
