"""
make_room.py: greybox parallax layers for VaniaGraybox (black and white, Viva look).

Writes ../assets/room/*.png, one tileable strip per layer (repeats on x), and room.json.
Every layer is a plain PNG: swap any file for real art, same name, and the game picks it up.
Layer speeds step by the golden ratio (1/phi^n), greys step toward black as layers come forward.
Floor tile: Saji's bricks.png, greyed.
"""
import json, os, random
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "assets", "room")
VIEW_W, VIEW_H = 320, 180        # native resolution, scaled by whole numbers in the browser
ROOM_W = VIEW_W * 5              # one hall, five screens long
PHI = (1 + 5 ** 0.5) / 2
random.seed(7)

def g(v): return (v, v, v, 255)

def strip(w, h): return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def towers(w, h, grey, base, n, hmin, hmax, wmin, wmax):
    im = strip(w, h); d = ImageDraw.Draw(im)
    x = 0
    while x < w:
        tw = random.randint(wmin, wmax); th = random.randint(hmin, hmax)
        d.rectangle([x, base - th, x + tw, base], fill=g(grey))
        if random.random() < 0.5:                          # spire
            d.polygon([(x, base - th), (x + tw, base - th), (x + tw // 2, base - th - tw)], fill=g(grey))
        x += tw + random.randint(2, w // n)
    d.rectangle([0, base, w, h], fill=g(grey))
    return im

def colonnade(w, h, grey, top, base, step):
    im = strip(w, h); d = ImageDraw.Draw(im)
    d.rectangle([0, top, w, top + 6], fill=g(grey))         # lintel
    for x in range(0, w, step):
        d.rectangle([x + 4, top, x + 12, base], fill=g(grey))
        d.pieslice([x + 12, top + 4, x + step + 4, top + step], 180, 360, fill=g(grey))
    d.rectangle([0, base, w, h], fill=g(grey))
    return im

def main():
    os.makedirs(OUT, exist_ok=True)
    floor_y = VIEW_H - 32
    sky = Image.new("RGBA", (VIEW_W, VIEW_H), g(236)); d = ImageDraw.Draw(sky)
    for y in range(VIEW_H):                                  # soft vertical fade
        v = round(244 - 22 * y / VIEW_H); d.line([0, y, VIEW_W, y], fill=g(v))
    d.ellipse([228, 22, 268, 62], fill=g(252))               # moon
    layers = [
        ("sky",  sky, 0.0),
        ("far",  towers(640, VIEW_H, 205, floor_y - 30, 6, 30, 80, 14, 30), 1 / PHI ** 3),
        ("mid",  colonnade(480, VIEW_H, 168, 40, floor_y - 6, 48), 1 / PHI ** 2),
        ("near", towers(560, VIEW_H, 128, floor_y, 3, 50, 120, 10, 22), 1 / PHI),
    ]
    meta = []
    for name, im, speed in layers:
        im.save(os.path.join(OUT, f"{name}.png"))
        meta.append({"name": name, "image": f"assets/room/{name}.png", "speed": round(speed, 4), "repeat": name != "sky"})

    bricks_src = os.path.join(ROOT, "bricks.png")
    if os.path.exists(bricks_src):
        tile = ImageOps.grayscale(Image.open(bricks_src).convert("RGB"))
        tile = ImageOps.autocontrast(tile).point(lambda v: 40 + v * 0.35).convert("RGBA")
    else:
        tile = Image.new("RGBA", (32, 32), g(60)); ImageDraw.Draw(tile).rectangle([0, 0, 31, 1], fill=g(90))
    tile.save(os.path.join(OUT, "floor.png"))

    fg = strip(VIEW_W * 2, VIEW_H); d = ImageDraw.Draw(fg)  # foreground pillars, in front of the hero
    d.rectangle([180, 0, 196, VIEW_H], fill=g(24)); d.rectangle([520, 0, 532, VIEW_H], fill=g(24))
    fg.save(os.path.join(OUT, "front.png"))

    room = {
        "view": {"w": VIEW_W, "h": VIEW_H},
        "width": ROOM_W,
        "floorY": floor_y,
        "back": meta,
        "floor": {"image": "assets/room/floor.png"},
        "front": [{"name": "front", "image": "assets/room/front.png", "speed": round(PHI, 4), "repeat": True}],
        "spawn": {"x": 64},
    }
    with open(os.path.join(ROOT, "assets", "room.json"), "w") as f:
        json.dump(room, f, indent=1)
    print("room:", ROOM_W, "wide,", len(meta), "back layers + floor + front")

if __name__ == "__main__":
    main()
