#!/usr/bin/env python3
"""Generate 320px WebP thumbnails for existing post covers.

For every _posts/*.md with an `image:` line, creates
assets/images/thumbs/<name>.webp (max edge 320px) and inserts a
`thumb:` front-matter line. Idempotent: skips posts that already
have a thumb line.

Requires Pillow:  python3 -m pip install --user Pillow
"""

import os
import re
import sys
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(REPO, "_posts")
THUMBS = os.path.join(REPO, "assets", "images", "thumbs")

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow missing: pip install Pillow")


def fetch(url):
    path = os.path.join(REPO, url.lstrip("/"))
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    with urllib.request.urlopen("https://kiruna.schelbert.ml" + url) as r:
        import io
        return Image.open(io.BytesIO(r.read())).convert("RGBA")


def main():
    os.makedirs(THUMBS, exist_ok=True)
    for name in sorted(os.listdir(POSTS)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(POSTS, name)
        text = open(path).read()
        m = re.search(r'^image:\s*"?([^"\n]+)"?\s*$', text, re.M)
        if not m:
            print(f"{name}: no cover, skipped")
            continue
        if re.search(r'^thumb:', text, re.M):
            print(f"{name}: already has thumb, skipped")
            continue
        img_url = m.group(1).strip()
        base = os.path.basename(img_url)
        thumb_rel = "/assets/images/thumbs/" + re.sub(r"\.[^.]+$", ".webp", base)
        thumb_path = os.path.join(REPO, thumb_rel.lstrip("/"))
        if not os.path.exists(thumb_path):
            img = fetch(img_url)
            w, h = img.size
            scale = min(1.0, 320 / max(w, h))
            tw, th = max(1, round(w * scale)), max(1, round(h * scale))
            img.resize((tw, th), Image.LANCZOS).save(thumb_path, "WEBP", quality=80)
            print(f"{name}: thumb {thumb_rel} ({os.path.getsize(thumb_path)//1024} KB)")
        else:
            print(f"{name}: thumb file exists, linking")
        text = re.sub(r'(^image:\s*"?[^"\n]+"?\s*$)',
                      r'\1\nthumb: "' + thumb_rel + '"',
                      text, count=1, flags=re.M)
        open(path, "w").write(text)


if __name__ == "__main__":
    main()
