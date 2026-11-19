"""make_bullet.py: placeholder bullet sheet (Aseprite format). Tags: fly (loop), hit (once). Pivot = centre."""
import json, os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "bullet")
C = 16
INK = (0, 0, 0, 255)

def cell(fn):
    im = Image.new("RGBA", (C, C), (0, 0, 0, 0)); fn(ImageDraw.Draw(im)); return im

FRAMES = [
    ("fly", cell(lambda d: d.rectangle([4, 6, 11, 9], fill=INK)), 60),
    ("fly", cell(lambda d: (d.rectangle([5, 6, 11, 9], fill=INK), d.rectangle([2, 7, 4, 8], fill=INK))), 60),
    ("hit", cell(lambda d: (d.rectangle([6, 6, 9, 9], fill=INK), [d.point(p, fill=INK) for p in [(4, 4), (11, 4), (4, 11), (11, 11)]])), 50),
    ("hit", cell(lambda d: [d.rectangle([x, y, x + 1, y + 1], fill=INK) for x, y in [(2, 2), (12, 2), (2, 12), (12, 12), (7, 1), (7, 13)]]), 70),
]

def main():
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.new("RGBA", (C * len(FRAMES), C), (0, 0, 0, 0)); frames, tags = [], {}
    for i, (tag, im, dur) in enumerate(FRAMES):
        sheet.alpha_composite(im, (i * C, 0))
        frames.append({"filename": f"bullet {i}.aseprite", "frame": {"x": i * C, "y": 0, "w": C, "h": C},
                       "rotated": False, "trimmed": False, "spriteSourceSize": {"x": 0, "y": 0, "w": C, "h": C},
                       "sourceSize": {"w": C, "h": C}, "duration": dur})
        tags.setdefault(tag, [i, i]); tags[tag][1] = i
    data = {"frames": frames, "meta": {"app": "https://www.aseprite.org/", "version": "1.3", "image": "bullet.png",
            "format": "RGBA8888", "size": {"w": sheet.width, "h": C}, "scale": "1",
            "frameTags": [{"name": k, "from": a, "to": b, "direction": "forward", "color": "#000000ff"} for k, (a, b) in tags.items()],
            "slices": [{"name": "pivot", "color": "#0000ffff", "keys": [{"frame": 0, "bounds": {"x": C // 2, "y": C // 2, "w": 1, "h": 1}}]}]}}
    sheet.save(os.path.join(OUT, "bullet.png"))
    with open(os.path.join(OUT, "bullet.json"), "w") as f: json.dump(data, f, indent=1)
    print("bullet:", len(FRAMES), "frames")

if __name__ == "__main__":
    main()
