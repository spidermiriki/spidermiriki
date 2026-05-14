#!/usr/bin/env python3
"""
Generate profile_pic.png (460x460) and wallpaper.png (1920x1080)
from an avatar image on a starry black background.

Usage  : python gen_images.py <avatar.png>
Install: pip install Pillow
"""

from collections import deque
from PIL import Image, ImageDraw
import random, sys, os


def remove_bg(img, tolerance=35):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    corners = [px[0,0][:3], px[w-1,0][:3], px[0,h-1][:3], px[w-1,h-1][:3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    def near(r, g, b):
        return all(abs(v - bg[i]) < tolerance for i, v in enumerate((r, g, b)))
    visited = {(0,0),(w-1,0),(0,h-1),(w-1,h-1)}
    q = deque(visited)
    while q:
        x, y = q.popleft()
        r, g, b, a = px[x, y]
        if near(r, g, b):
            px[x, y] = (r, g, b, 0)
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in visited:
                    visited.add((nx,ny)); q.append((nx,ny))
    return img


def crop_to_content(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def stars(draw, W, H, n, seed=0):
    random.seed(seed)
    for _ in range(n):
        x, y = random.uniform(0, W), random.uniform(0, H)
        r = random.uniform(0.3, 1.8)
        v = random.randint(150, 255)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(v, v, v))


def draw_planet(draw, cx, cy, R):
    # Base: very light blue
    draw.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(200, 235, 242))
    # Continents: #5fc8e8
    C = (95, 200, 232)
    draw.polygon([
        (cx - int(R*.55), cy - int(R*.72)),
        (cx - int(R*.88), cy - int(R*.40)),
        (cx - int(R*.92), cy + int(R*.10)),
        (cx - int(R*.68), cy + int(R*.40)),
        (cx - int(R*.32), cy + int(R*.28)),
        (cx - int(R*.15), cy - int(R*.18)),
        (cx - int(R*.28), cy - int(R*.55)),
    ], fill=C)
    draw.polygon([
        (cx + int(R*.16), cy - int(R*.50)),
        (cx + int(R*.64), cy - int(R*.26)),
        (cx + int(R*.78), cy + int(R*.24)),
        (cx + int(R*.55), cy + int(R*.62)),
        (cx + int(R*.18), cy + int(R*.48)),
        (cx + int(R*.06), cy + int(R*.08)),
    ], fill=C)
    draw.polygon([
        (cx + int(R*.08), cy - int(R*.70)),
        (cx + int(R*.36), cy - int(R*.58)),
        (cx + int(R*.26), cy - int(R*.40)),
        (cx + int(R*.04), cy - int(R*.50)),
    ], fill=C)


def draw_moon(draw, cx, cy, R):
    # Base: off-white grey
    draw.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(232, 232, 224))
    # Craters: slightly darker grey
    K = (200, 200, 192)
    draw.ellipse([cx-int(R*.38), cy-int(R*.22), cx+int(R*.02), cy+int(R*.18)], fill=K)
    draw.ellipse([cx+int(R*.22), cy+int(R*.28), cx+int(R*.58), cy+int(R*.64)], fill=K)
    draw.ellipse([cx-int(R*.62), cy+int(R*.32), cx-int(R*.36), cy+int(R*.58)], fill=K)
    draw.ellipse([cx+int(R*.08), cy-int(R*.68), cx+int(R*.34), cy-int(R*.42)], fill=K)


def draw_ground(draw, right_edge, H):
    # Lunar surface
    draw.polygon([
        (0, H), (0, H-90),
        (80,  H-140), (200, H-122),
        (340, H-158), (480, H-138),
        (right_edge, H-100),
        (right_edge+250, H-82),
        (right_edge+250, H),
    ], fill=(215, 228, 232))
    # Darker shadow strip at very bottom
    draw.polygon([
        (0, H), (0, H-28),
        (right_edge+250, H-18),
        (right_edge+250, H),
    ], fill=(175, 192, 198))


def generate(avatar_path, out_dir="."):
    print(f"→ Loading {avatar_path}")
    av = crop_to_content(remove_bg(Image.open(avatar_path)))
    av_w, av_h = av.size

    # ── Profile picture  460 × 460 ──────────────────────────────────
    S, pad = 460, 10
    scale = min((S - pad*2) / av_w, (S - pad*2) / av_h)
    nw, nh = int(av_w * scale), int(av_h * scale)
    av_s = av.resize((nw, nh), Image.LANCZOS)

    im = Image.new("RGB", (S, S), (0,0,0))
    stars(ImageDraw.Draw(im), S, S, 85, seed=7)
    im.paste(av_s, ((S-nw)//2, (S-nh)//2), av_s.split()[3])
    im.save(os.path.join(out_dir, "profile_pic.png"))
    print(f"✓  profile_pic.png")

    # ── Wallpaper  1920 × 1080  (Invincible-style) ──────────────────
    W, H = 1920, 1080
    wall = Image.new("RGB", (W, H), (0,0,0))
    wd = ImageDraw.Draw(wall)

    # Dense starfield
    stars(wd, W, H, 1400, seed=42)

    # Planet – upper right
    draw_planet(wd, cx=int(W*.795), cy=int(H*.26), R=215)

    # Scale character to ~78% of height (cap upscale at 5x to avoid blur)
    target_h = int(H * 0.78)
    cscale = min(target_h / av_h, 5.0)
    cw, ch = int(av_w * cscale), int(av_h * cscale)
    av_w2 = av.resize((cw, ch), Image.LANCZOS)

    # Character position – more to the right, ground visible on the left
    char_x = 280
    char_y = H - ch - 105

    # Ground extends from left edge to well past the character
    draw_ground(wd, right_edge=char_x + cw + 200, H=H)

    # Moon – behind character, slightly to the right
    moon_cx = char_x + int(cw * 0.80)
    moon_cy = char_y + int(ch * 0.28)
    draw_moon(wd, moon_cx, moon_cy, R=105)

    # Character on top of moon and ground
    wall.paste(av_w2, (char_x, max(char_y, 10)), av_w2.split()[3])

    wall.save(os.path.join(out_dir, "wallpaper.png"))
    print(f"✓  wallpaper.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gen_images.py <avatar.png>")
        sys.exit(1)
    generate(sys.argv[1])
