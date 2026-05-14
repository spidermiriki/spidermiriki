#!/usr/bin/env python3
"""
Avatar on starry black background generator.

Usage : python gen_images.py <avatar.png>
Output: profile_pic.png (460x460)  and  wallpaper.png (1920x1080)

Install: pip install Pillow
"""

from collections import deque
from PIL import Image, ImageDraw
import random, sys, os


def remove_bg(img, tolerance=35):
    """BFS flood-fill from corners to erase the background."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size

    corners = [px[0, 0][:3], px[w-1, 0][:3], px[0, h-1][:3], px[w-1, h-1][:3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    def near(r, g, b):
        return all(abs(v - bg[i]) < tolerance for i, v in enumerate((r, g, b)))

    visited = {(0,0), (w-1,0), (0,h-1), (w-1,h-1)}
    q = deque(visited)
    while q:
        x, y = q.popleft()
        r, g, b, a = px[x, y]
        if near(r, g, b):
            px[x, y] = (r, g, b, 0)
            for nx, ny in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
    return img


def add_stars(draw, W, H, n, seed=0):
    """Scatter white + #5fc8e8 star dots."""
    random.seed(seed)
    for _ in range(n):
        x = random.uniform(0, W)
        y = random.uniform(0, H)
        r = random.uniform(0.5, 2.2)
        v = random.randint(140, 255)
        color = (95, 200, 232) if random.random() < 0.22 else (v, v, v)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)


def circle_crop(img, size):
    """Resize and apply circular mask, returns RGBA."""
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask)
    return result


def place(base, circ, cx, cy, ring_w=2):
    """Draw blue ring then paste circular avatar centred at (cx, cy)."""
    sz = circ.size[0]
    rr = sz // 2 + 3
    ImageDraw.Draw(base).ellipse(
        [cx-rr, cy-rr, cx+rr, cy+rr],
        outline=(95, 200, 232), width=ring_w
    )
    base.paste(circ, (cx - sz//2, cy - sz//2), circ.split()[3])


def generate(avatar_path, out_dir="."):
    print(f"→ Loading {avatar_path}")
    av = remove_bg(Image.open(avatar_path))

    # ── Profile picture  460 × 460 ──────────────────────────────────────
    S = 460
    im = Image.new("RGB", (S, S), (0, 0, 0))
    add_stars(ImageDraw.Draw(im), S, S, n=85, seed=7)
    place(im, circle_crop(av, 400), cx=S//2, cy=S//2)
    out1 = os.path.join(out_dir, "profile_pic.png")
    im.save(out1)
    print(f"✓  {out1}")

    # ── Wallpaper  1920 × 1080 ──────────────────────────────────────────
    W, H = 1920, 1080
    wl = Image.new("RGB", (W, H), (0, 0, 0))
    add_stars(ImageDraw.Draw(wl), W, H, n=500, seed=13)
    place(wl, circle_crop(av, 520), cx=W//2, cy=H//2, ring_w=3)
    out2 = os.path.join(out_dir, "wallpaper.png")
    wl.save(out2)
    print(f"✓  {out2}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gen_images.py <avatar.png>")
        sys.exit(1)
    generate(sys.argv[1])
