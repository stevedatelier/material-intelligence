import json
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


ROOT = Path(r"D:\Apps\Knitting-3Drealworld-houdini")
DOCS = ROOT / "docs/images"
BG = "#0b1016"
PANEL_BG = "#151c24"
TEXT = "#f2f5f7"
MUTED = "#a9b5c1"
CYAN = "#60d8e8"
ORANGE = "#ffad66"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path(r"C:\Windows\Fonts\seguisb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def load(path: str | Path) -> Image.Image:
    return Image.open(ROOT / path if isinstance(path, str) else path).convert("RGB")


def grade(image: Image.Image, saturation: float = 0.9, contrast: float = 1.05) -> Image.Image:
    image = ImageEnhance.Color(image).enhance(saturation)
    return ImageEnhance.Contrast(image).enhance(contrast)


def labeled_panel(
    image: Image.Image,
    size: tuple[int, int],
    label: str,
    detail: str = "",
    accent: str = CYAN,
    focal: tuple[float, float] = (0.5, 0.5),
) -> Image.Image:
    w, h = size
    fitted = ImageOps.fit(image, (w, h), method=Image.Resampling.LANCZOS, centering=focal)
    fitted = grade(fitted)
    draw = ImageDraw.Draw(fitted, "RGBA")
    footer_h = 92 if detail else 62
    draw.rectangle((0, h - footer_h, w, h), fill=(8, 12, 17, 232))
    draw.rectangle((0, h - footer_h, 8, h), fill=accent)
    draw.text((24, h - footer_h + 14), label.upper(), font=font(25, True), fill=TEXT)
    if detail:
        draw.text((24, h - 37), detail, font=font(18), fill=MUTED)
    return fitted


def strip(items, output: str, size: tuple[int, int], gutter: int = 12) -> None:
    total_w, total_h = size
    count = len(items)
    panel_w = (total_w - gutter * (count - 1)) // count
    canvas = Image.new("RGB", (total_w, total_h), BG)
    x = 0
    for item in items:
        image, label, detail, accent, focal = item
        panel = labeled_panel(image, (panel_w, total_h), label, detail, accent, focal)
        canvas.paste(panel, (x, 0))
        x += panel_w + gutter
    canvas.save(DOCS / output, quality=88, optimize=True, progressive=True)


def video_frame(path: Path, index: int) -> Image.Image:
    capture = cv2.VideoCapture(str(path))
    capture.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, bgr = capture.read()
    capture.release()
    if not ok:
        raise RuntimeError(f"Could not read frame {index} from {path}")
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


hero_reference = load("images/real_references/les-triconautes-0TZrwxl--Cg-unsplash.jpg")
hero_geometry = load("images/houdini_process/Screenshot 2024-12-26 195230.png")
hero_final = load("images/3d_renders/White_animated_wool.0046.png")
strip(
    [
        (hero_reference, "material reference", "real yarn at several twist scales", ORANGE, (0.57, 0.50)),
        (hero_geometry, "explicit curve system", "guide and fiber populations in Houdini", CYAN, (0.50, 0.52)),
        (hero_final, "rendered response", "volume and softness emerge from geometry", "#d8ddd4", (0.52, 0.50)),
    ],
    "hero-reference-geometry-render.jpg",
    (1800, 700),
)


lana = load("images/real_references/Lana-2968-Edit.jpg")
controlled = load("images/3d_renders/Screenshot 2024-12-26 070242.png")
fiber_final = load("images/3d_renders/White_animated_infinity.0063.png")
strip(
    [
        (lana, "reference yarn", "ply direction remains legible at ball scale", ORANGE, (0.52, 0.50)),
        (controlled, "nested sweeps", "bundle volume is built from explicit strands", CYAN, (0.50, 0.52)),
        (fiber_final, "fiber-rich output", "flyaways break the otherwise clean boundary", "#d8ddd4", (0.52, 0.50)),
    ],
    "real-yarn-vs-procedural.jpg",
    (1800, 620),
)


guides = load("images/houdini_process/Screenshot 2024-12-26 193558.png")
bundle = load("images/3d_renders/Screenshot 2024-12-26 040943.png")
dense_info = load("images/houdini_process/Screenshot 2024-12-25 165425.png")
final = load("images/3d_renders/White_animated_wool.0044.png")
strip(
    [
        (guides, "01 / guide curves", "trajectory", CYAN, (0.55, 0.50)),
        (bundle, "02 / strand bundle", "volume", CYAN, (0.52, 0.50)),
        (dense_info, "03 / fiber geometry", "26.1M-point debug state", ORANGE, (0.36, 0.50)),
        (final, "04 / shaded output", "appearance", "#d8ddd4", (0.53, 0.50)),
    ],
    "representation-ladder.jpg",
    (2000, 600),
)


stable = load("images/3d_renders/Screenshot 2024-12-26 181041.png")
collapsed = load("images/houdini_process/Screenshot 2024-12-26 193558.png")
overdense = load("images/houdini_process/Screenshot 2024-12-25 165425.png")
strip(
    [
        (stable, "controlled structure", "twist remains readable", CYAN, (0.50, 0.52)),
        (collapsed, "collapsed guides", "cross-section and packing are no longer preserved", ORANGE, (0.68, 0.50)),
        (overdense, "over-dense surface", "nested sweeps dominate the representation cost", "#ff6f6f", (0.33, 0.50)),
    ],
    "success-vs-failure.jpg",
    (1800, 620),
)


tear_video = ROOT / "images/Tear Propagation/cloth_tearing_video.mp4"
tear_final = load("images/Tear Propagation/cam14_blue_alt.0062.png")
strip(
    [
        (video_frame(tear_video, 0), "01 / intact proxy", "connected cloth", CYAN, (0.53, 0.50)),
        (video_frame(tear_video, 11), "02 / failure onset", "local separation", ORANGE, (0.53, 0.50)),
        (video_frame(tear_video, 32), "03 / propagation", "constraints release", ORANGE, (0.53, 0.50)),
        (video_frame(tear_video, 53), "04 / changed topology", "future motion now differs", "#ff6f6f", (0.53, 0.50)),
        (tear_final, "05 / shaded result", "damage remains structurally visible", "#d8ddd4", (0.52, 0.50)),
    ],
    "tear-topology-sequence.jpg",
    (2000, 500),
    gutter=8,
)


# Render the actual cooked Dynamic_Knitting_HDA geometry as an explanatory diagram.
data = json.loads((ROOT / "tools/knit_geometry.json").read_text(encoding="utf-8"))
canvas = Image.new("RGB", (1800, 900), BG)
draw = ImageDraw.Draw(canvas, "RGBA")
draw.text((54, 42), "THE CURRENT KNIT PROTOTYPE — COOKED GEOMETRY", font=font(34, True), fill=TEXT)
draw.text((54, 91), data["node"], font=font(21), fill=MUTED)

plot = (54, 150, 1240, 830)
px0, py0, px1, py1 = plot
projected = []
for primitive in data["polylines"]:
    line = []
    for x, y, z in primitive:
        iso_x = x + z * 0.38
        iso_y = -z * 0.36 - y * 3.0
        line.append((iso_x, iso_y, y))
    projected.append(line)

all_x = [p[0] for line in projected for p in line]
all_y = [p[1] for line in projected for p in line]
min_x, max_x = min(all_x), max(all_x)
min_y, max_y = min(all_y), max(all_y)
scale = min((px1 - px0 - 80) / (max_x - min_x), (py1 - py0 - 80) / (max_y - min_y))

def screen(point):
    x, y, level = point
    sx = px0 + 40 + (x - min_x) * scale
    sy = py0 + 40 + (y - min_y) * scale
    return sx, sy, level

draw.rounded_rectangle(plot, radius=24, fill=PANEL_BG, outline=(88, 107, 124, 130), width=2)
for line in projected:
    points = [screen(point) for point in line]
    level = sum(point[2] for point in points) / len(points)
    color = (96, 216, 232, 205) if level > 0.05 else (255, 173, 102, 185)
    draw.line([(point[0], point[1]) for point in points], fill=color, width=2)

legend_y = 775
draw.line((83, legend_y, 122, legend_y), fill=ORANGE, width=5)
draw.text((137, legend_y - 14), "Y = 0", font=font(18), fill=MUTED)
draw.line((235, legend_y, 274, legend_y), fill=CYAN, width=5)
draw.text((289, legend_y - 14), "Y = 0.1", font=font(18), fill=MUTED)

cards = [
    ("400", "separate polygon curves"),
    ("1,200", "points — three per curve"),
    ("2", "height bands from the row rule"),
    ("0", "shared points between primitives"),
]
card_x, card_y = 1290, 170
for value, label in cards:
    draw.rounded_rectangle((card_x, card_y, 1746, card_y + 130), radius=18, fill=PANEL_BG)
    draw.text((card_x + 24, card_y + 17), value, font=font(39, True), fill=CYAN if value != "0" else ORANGE)
    draw.text((card_x + 24, card_y + 77), label, font=font(19), fill=MUTED)
    card_y += 148
draw.text((1290, 790), "Layout approximation ≠ loop topology", font=font(20, True), fill=TEXT)
canvas.save(DOCS / "knit-prototype-cooked-geometry.jpg", quality=90, optimize=True, progressive=True)


# Convert the strongest procedural motion study to a compact looping GIF.
motion = ROOT / "images/houdini_process/knitting_infity_yarn.avi"
capture = cv2.VideoCapture(str(motion))
frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
fps = capture.get(cv2.CAP_PROP_FPS) or 24.0
indices = [round(i * (frame_count - 1) / 23) for i in range(24)]
gif_frames = []
for index in indices:
    capture.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, bgr = capture.read()
    if not ok:
        continue
    frame = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    frame = ImageOps.fit(frame, (720, 720), method=Image.Resampling.LANCZOS)
    gif_frames.append(frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
capture.release()
duration = round(1000 * (frame_count / fps) / max(len(gif_frames), 1))
gif_frames[0].save(
    DOCS / "yarn-motion-study.gif",
    save_all=True,
    append_images=gif_frames[1:],
    duration=duration,
    loop=0,
    optimize=True,
    disposal=2,
)

print("Generated README visuals:")
for path in sorted(DOCS.glob("*.jpg")):
    if path.name.startswith(("hero-reference", "real-yarn", "representation-ladder", "success-vs", "tear-topology", "knit-prototype")):
        print(path.name, path.stat().st_size)
print("yarn-motion-study.gif", (DOCS / "yarn-motion-study.gif").stat().st_size)
