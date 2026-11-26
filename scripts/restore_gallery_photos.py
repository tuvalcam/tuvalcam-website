#!/usr/bin/env python3
"""One-time repair: restore genuine Google-source gallery photos as local WebP assets."""
from __future__ import annotations
import io
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "photo-gallery.js"
IDS = (15, 31, 47, 64, 81, 100)
HTML = (
    "index.html", "cam/index.html", "ayna/index.html",
    "cerceve/index.html", "sineklik/index.html", "galeri/index.html",
    "izmir/index.html",
)

body = JS.read_text(encoding="utf-8")
prefix = "const galleryData="
start = body.index(prefix) + len(prefix)
end = body.index("];", start) + 1
photos = json.loads(body[start:end])
selected = [p for p in photos if p["id"] in IDS]
if len(selected) != 6 or {p["id"] for p in selected} != set(IDS):
    raise RuntimeError("Missing or duplicate gallery photo records")

# Download all original photos before changing any site references.
for photo in selected:
    dest = ROOT / photo["file"]
    errors = []
    for suffix in ("", "=w1200", "=s1200"):
        try:
            req = urllib.request.Request(
                photo["url"] + suffix,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; TuvalCamPhotoRestoration/1.0)",
                    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read(10_000_000)
                mime = resp.headers.get("Content-Type", "")
            if len(raw) < 1000:
                raise RuntimeError("download unexpectedly small")
            with Image.open(io.BytesIO(raw)) as downloaded:
                image = ImageOps.exif_transpose(downloaded).convert("RGB")
            if min(image.size) < 250:
                raise RuntimeError("download is too small to be the original photo")
            image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            dest.parent.mkdir(parents=True, exist_ok=True)
            image.save(dest, "WEBP", quality=86, method=6)
            with Image.open(dest) as validated:
                validated.verify()
            if dest.stat().st_size < 1000:
                raise RuntimeError("converted WebP unexpectedly small")
            print(
                f"RESTORED photo-{photo['id']:03d} "
                f"source={len(raw)} bytes ({mime}) "
                f"local={dest.stat().st_size} bytes size={image.size}"
            )
            break
        except (OSError, ValueError, RuntimeError, UnidentifiedImageError) as exc:
            errors.append(str(exc))
            time.sleep(1)
    else:
        raise RuntimeError(
            f"Cannot restore original photo {photo['id']}; attempts: {errors}"
        )

# The six source URLs in static HTML must now point to local images.
for filename in HTML:
    path = ROOT / filename
    content = path.read_text(encoding="utf-8")
    changed = content
    for photo in selected:
        changed = changed.replace(photo["url"], "/" + photo["file"])
    if changed != content:
        path.write_text(changed, encoding="utf-8")
        print(f"LOCALIZED {filename}")

# Keep provenance URLs in the gallery records but never load them during normal browsing.
old_selector = (
    "const missingLocalPhotoIds=new Set([15,31,47,64,81,100]);\n"
    "const photoURL=id=>{const p=galleryData.find(p=>p.id===id);"
    "return missingLocalPhotoIds.has(id)?p.url:'/'+p.file};"
)
new_selector = "const photoURL=id=>'/'+galleryData.find(p=>p.id===id).file;"
if body.count(old_selector) != 1:
    raise RuntimeError("Unexpected photo selector; manual review required")
body = body.replace(old_selector, new_selector)
old_fallback = "img.onerror=()=>{if(img.src!==p.url){img.onerror=null;img.src=p.url}};"
if body.count(old_fallback) != 2:
    raise RuntimeError("Unexpected image fallback implementation")
body = body.replace(old_fallback, "")
JS.write_text(body, encoding="utf-8")

# Include the restored local images in the existing image sitemap (170 -> 176).
sitemap = ROOT / "sitemap.xml"
xml = sitemap.read_text(encoding="utf-8")
assert xml.count("<url>") == 7
assert xml.count("<image:image>") == 170
for photo in selected:
    category = photo["category"]
    service = {"cam": "cam/", "cerceve": "cerceve/"}.get(category)
    if service is None:
        raise RuntimeError("Unexpected restored photo category " + category)
    page_url = "https://www.tuvalcam.com/" + service
    match = re.search(
        r"(<url>\s*<loc>" + re.escape(page_url) + r"</loc>)(.*?)(</url>)",
        xml,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("No sitemap entry for " + page_url)
    local_url = "https://www.tuvalcam.com/" + photo["file"]
    if local_url in match.group(0):
        raise RuntimeError("Photo already appears in sitemap " + local_url)
    insert = (
        "    <image:image>\n"
        f"      <image:loc>{local_url}</image:loc>\n"
        "    </image:image>\n"
    )
    xml = xml[:match.end(2)] + insert + xml[match.end(2):]
if xml.count("<image:image>") != 176:
    raise RuntimeError("Restored sitemap does not have 176 image entries")
sitemap.write_text(xml, encoding="utf-8")

print("SUCCESS: all six photos saved locally; gallery, JavaScript and image sitemap updated.")
