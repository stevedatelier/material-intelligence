from __future__ import annotations

from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in (Path(r"C:\Windows\Fonts\seguisb.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def contact_sheet(sources: list[str], output: str, labels: list[str]) -> None:
    panel_w, panel_h, gutter, footer = 620, 430, 10, 58
    canvas = Image.new("RGB", (panel_w * len(sources) + gutter * (len(sources) - 1), panel_h + footer), "#0b1016")
    draw = ImageDraw.Draw(canvas)
    for index, (source, label) in enumerate(zip(sources, labels)):
        image = Image.open(ROOT / source).convert("RGB")
        panel = ImageOps.fit(image, (panel_w, panel_h), method=Image.Resampling.LANCZOS)
        x = index * (panel_w + gutter)
        canvas.paste(panel, (x, 0))
        draw.text((x + 18, panel_h + 14), label.upper(), font=font(22), fill="#eef3f6")
    canvas.save(OUT / output, quality=87, optimize=True, progressive=True)


def read_video_frames(path: Path, start: int, end: int, count: int, size: tuple[int, int]) -> tuple[list[Image.Image], int]:
    capture = cv2.VideoCapture(str(path))
    fps = capture.get(cv2.CAP_PROP_FPS) or 24.0
    indices = [round(start + i * (end - start) / max(count - 1, 1)) for i in range(count)]
    frames: list[Image.Image] = []
    for frame_number in indices:
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ok, bgr = capture.read()
        if not ok:
            raise RuntimeError(f"Could not read frame {frame_number} from {path}")
        image = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        frames.append(ImageOps.fit(image, size, method=Image.Resampling.LANCZOS))
    capture.release()
    duration = round(1000 * ((end - start + 1) / fps) / len(frames))
    return frames, duration


def write_gif(
    source: str,
    output: str,
    start: int,
    end: int,
    count: int,
    size: tuple[int, int],
    colors: int = 80,
) -> None:
    frames, duration = read_video_frames(ROOT / source, start, end, count, size)
    sample_w = 192
    palette_source = Image.new("RGB", (sample_w * len(frames), sample_w), "black")
    for index, frame in enumerate(frames):
        sample = ImageOps.fit(frame, (sample_w, sample_w), method=Image.Resampling.LANCZOS)
        palette_source.paste(sample, (index * sample_w, 0))
    palette = palette_source.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for frame in frames]
    quantized[0].save(
        OUT / output,
        save_all=True,
        append_images=quantized[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


contact_sheet(
    [
        "images/macro-or-closeup_level/Screenshot 2024-08-09 105543.png",
        "images/macro-or-closeup_level/Screenshot 2024-08-09 112913.png",
        "images/macro-or-closeup_level/Screenshot 2024-08-09 141549.png",
    ],
    "material-closeup-geometry.jpg",
    ["local interlock", "topology field", "strand detail"],
)

contact_sheet(
    [
        "images/macro-or-closeup_level/Screenshot 2025-01-02 010829.png",
        "images/macro-or-closeup_level/Screenshot 2025-01-02 011009.png",
        "images/macro-or-closeup_level/Screenshot 2025-01-02 011153.png",
    ],
    "material-closeup-render-studies.jpg",
    ["dark field", "alternating material", "light field"],
)

contact_sheet(
    [
        "images/houdini_process/Screenshot 2024-12-23 104419.png",
        "images/houdini_process/Screenshot 2024-12-25 165425.png",
        "images/houdini_process/Screenshot 2024-12-23 044618.png",
        "images/3d_renders/White_animated_wool.0044.png",
    ],
    "fiber-to-yarn-progression.jpg",
    ["fiber population", "fiber groups", "strand twist", "fiber material"],
)

contact_sheet(
    [
        "images/houdini_process/Screenshot 2024-12-26 193558.png",
        "images/houdini_process/Screenshot 2024-12-25 165402.png",
        "images/3d_renders/Screenshot 2024-12-26 070242.png",
        "images/3d_renders/White_animated_infinity.0063.png",
    ],
    "infinity-yarn-development.jpg",
    ["guide curves", "strand system", "packed twist", "fiber output"],
)

contact_sheet(
    [
        "images/3d_renders/Screenshot 2024-08-01 143000.png",
        "images/3d_renders/Screenshot 2024-08-01 171712.png",
        "images/3d_renders/Screenshot 2024-08-01 172840.png",
    ],
    "fabric-development.jpg",
    ["repeated field", "strand close-up", "open boundary"],
)

contact_sheet(
    [
        "images/houdini_process/Screenshot 2024-12-20 050234.png",
        "images/houdini_process/Screenshot 2024-12-20 230231.png",
        "images/3d_renders/Screenshot 2025-01-01 022815.png",
        "images/3d_renders/Screenshot 2025-01-15 232957.png",
    ],
    "yarn-ball-system.jpg",
    ["wrap paths", "support shell", "twisted output", "material study"],
)

contact_sheet(
    [
        "images/3d_renders/Screenshot 2024-08-12 215523.png",
        "images/3d_renders/Screenshot 2025-01-06 012003.png",
        "images/3d_renders/Screenshot 2025-01-06 022551.png",
        "images/3d_renders/Screenshot 2025-01-15 234445.png",
    ],
    "material-variations.jpg",
    ["felted yellow", "soft white", "blue fiber", "color system"],
)

write_gif(
    "images/Tear Propagation/cloth_tearing_video.mp4",
    "material-failure.gif",
    0,
    53,
    27,
    (800, 450),
    colors=80,
)
write_gif(
    "images/houdini_process/PB-Yarn-ball240.mov",
    "yarn-deformation.gif",
    0,
    132,
    30,
    (640, 640),
    colors=72,
)
write_gif(
    "images/houdini_process/fivewools.mov",
    "vellum-contact.gif",
    0,
    49,
    25,
    (640, 640),
    colors=72,
)
write_gif(
    "images/3d_renders/ten_wool_balls.mov",
    "ten-wool-contact.gif",
    0,
    120,
    30,
    (640, 640),
    colors=72,
)

for path in (
    OUT / "material-closeup-geometry.jpg",
    OUT / "material-closeup-render-studies.jpg",
    OUT / "fiber-to-yarn-progression.jpg",
    OUT / "infinity-yarn-development.jpg",
    OUT / "fabric-development.jpg",
    OUT / "yarn-ball-system.jpg",
    OUT / "material-variations.jpg",
    OUT / "material-failure.gif",
    OUT / "yarn-deformation.gif",
    OUT / "vellum-contact.gif",
    OUT / "ten-wool-contact.gif",
):
    print(f"{path.name}\t{path.stat().st_size}")
