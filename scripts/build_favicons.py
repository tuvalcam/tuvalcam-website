#!/usr/bin/env python3
"""Generate Google-compatible, square PNG/ICO favicons from the Tuval Cam vector mark."""
from pathlib import Path
import io
import cairosvg
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
svg = (ROOT / "favicon.svg").read_bytes()
for size in (48, 96, 192, 512):
    dest = ROOT / f"favicon-{size}x{size}.png"
    dest.write_bytes(cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size))
    with Image.open(dest) as im:
        im.verify()
    print("CREATED", dest.name, dest.stat().st_size)
apple = ROOT / "apple-touch-icon.png"
apple.write_bytes(cairosvg.svg2png(bytestring=svg, output_width=180, output_height=180))
with Image.open(apple) as im:
    im.verify()
print("CREATED", apple.name, apple.stat().st_size)
ico_path = ROOT / "favicon.ico"
with Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg, output_width=256, output_height=256))) as img:
    img.convert("RGBA").save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
with Image.open(ico_path) as im:
    assert im.format == "ICO" and im.size == (256, 256)
print("CREATED", ico_path.name, ico_path.stat().st_size)
