"""
make_hero.py: placeholder hero sheet for VaniaGraybox, from the Vitruvian seed.

Writes (into ../assets/hero/):
  hero.png        clean silhouettes, one keyframe per cell. The game reads this.
  hero.json       Aseprite-format data (JSON Array): frames, durations, frameTags, pivot slice.
  hero_guide.png  the same sheet with grid, labels, baseline and pivot marks. Saji draws over this.

Proportions come from the Vitruvian seed (D:\\_WATUSI\\ART LIBRARY\\Seed\\vitruvian, palace T/13/2),
unit = total height. The rig is a flat side view (facing right): pure math + a thin PIL adapter.
Near limbs are black, far limbs grey, so overlapping poses stay readable.

Change the sheet: edit CELL / HERO_H or a pose in MOVES, run `python make_hero.py`.
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "hero")

# --- the contract (confirm with Saji) -------------------------------------------------
CELL = 64          # every frame is CELL x CELL
HERO_H = 48        # standing height in px (Saji's proto protagonist: ~24 x 48)
PIVOT = (CELL // 2, CELL - 2)   # feet: bottom centre. Lowest pixel of the pose sits on this row.
COLS = 8           # cells per row in the sheet

# --- Vitruvian seed (unit = total height) ---------------------------------------------
V = {
    "head": 0.125, "neck": 0.0417,           # chin to sternum line = 0.1667 - 0.125
    "torso": 0.3333,                          # sternum line (0.8333 H) to hip joint (0.5 H)
    "upperArm": 0.225, "forearm": 0.15, "hand": 0.1,
    "upperLeg": 0.25, "lowerLeg": 0.25, "foot": 0.1666,
}
L = {k: v * HERO_H for k, v in V.items()}
THICK = {"torso": 7, "upperLeg": 5, "lowerLeg": 4, "upperArm": 4, "forearm": 3}

NEAR, FAR, SWORD = (0, 0, 0, 255), (110, 110, 110, 255), (60, 60, 60, 255)

# --- poses ----------------------------------------------------------------------------
# Angles in degrees. Limbs: 0 = straight down, + = swung forward (toward facing).
# knee: how much the shin folds back from the thigh. elbow: how much the forearm folds forward.
# lean: torso tilt forward from upright. roll: whole-body rotation (death).
BASE = dict(lean=3, nh=4, nk=6, fh=-4, fk=6, ns=6, ne=14, fs=-6, fe=14, sword=None, roll=0)

def P(**kw):
    p = dict(BASE); p.update(kw); return p

# name: list of (pose, duration ms). Keyframes only: Saji adds the in-betweens.
MOVES = {
    "idle":  [(P(), 500), (P(nk=10, fk=10, ns=4, fs=-4), 500)],
    "walk":  [(P(nh=26, nk=4,  fh=-22, fk=14, ns=-20, fs=20), 130),
              (P(nh=2,  nk=6,  fh=8,   fk=48, ns=0,   fs=0), 130),
              (P(nh=-22, nk=14, fh=26, fk=4,  ns=20,  fs=-20), 130),
              (P(nh=8,  nk=48, fh=2,   fk=6,  ns=0,   fs=0), 130)],
    "crouch": [(P(lean=22, nh=78, nk=135, fh=68, fk=130, ns=30, ne=40, fs=10, fe=40), 100)],
    "jump":  [(P(lean=8, nh=62, nk=95, fh=12, fk=55, ns=150, ne=20, fs=120, fe=20), 100)],
    "fall":  [(P(lean=4, nh=22, nk=30, fh=-12, fk=48, ns=100, ne=10, fs=80, fe=10), 100)],
    "land":  [(P(lean=26, nh=58, nk=108, fh=48, fk=100, ns=40, ne=30, fs=20, fe=30), 90)],
    "attack": [(P(lean=-4, nh=10, nk=8, fh=-14, fk=10, ns=145, ne=25, fs=-20, sword=50), 70),
               (P(lean=14, nh=36, nk=12, fh=-26, fk=8, ns=88, ne=0, fs=-35, sword=0), 100),
               (P(lean=8, nh=24, nk=14, fh=-20, fk=10, ns=40, ne=30, fs=-15, sword=-10), 140)],
    "crouch_attack": [(P(lean=20, nh=78, nk=135, fh=68, fk=130, ns=140, ne=25, sword=50), 70),
                      (P(lean=26, nh=80, nk=135, fh=68, fk=130, ns=92, ne=0, sword=0), 100),
                      (P(lean=22, nh=78, nk=135, fh=68, fk=130, ns=45, ne=30, sword=-10), 140)],
    "jump_attack": [(P(lean=8, nh=62, nk=95, fh=12, fk=55, ns=140, ne=25, sword=50), 70),
                    (P(lean=18, nh=55, nk=90, fh=15, fk=60, ns=55, ne=0, sword=0), 100),
                    (P(lean=12, nh=50, nk=85, fh=15, fk=55, ns=25, ne=25, sword=-10), 140)],
    "backdash": [(P(lean=-16, nh=-24, nk=30, fh=22, fk=18, ns=-30, ne=30, fs=-40, fe=30), 110),
                 (P(lean=-10, nh=-8, nk=16, fh=10, fk=12, ns=-15, ne=25, fs=-25, fe=25), 110)],
    "hurt":  [(P(lean=-26, nh=-6, nk=20, fh=14, fk=12, ns=60, ne=30, fs=40, fe=30), 220)],
    "death": [(P(lean=-26, nh=-6, nk=20, fh=14, fk=12, ns=60, ne=30, fs=40, fe=30), 160),
              (P(lean=40, nh=90, nk=160, fh=80, fk=150, ns=20, ne=10, fs=10, fe=10), 260),
              (P(lean=0, nh=4, nk=10, fh=-4, fk=12, ns=12, ne=6, fs=-6, fe=6, roll=-90), 1200)],
}

# --- the rig (pure math) --------------------------------------------------------------
def at(p, ang, length):
    """point at `length` from p, angle measured from straight down, + = forward (right)."""
    a = math.radians(ang)
    return (p[0] + math.sin(a) * length, p[1] + math.cos(a) * length)

def solve(pose):
    """bones as (layer, a, b, thickness, colour); hip joint at origin."""
    hip = (0.0, 0.0)
    up = 180 - pose["lean"]                    # torso points up, tilted forward by lean
    sternum = at(hip, up, L["torso"])
    chin = at(sternum, up, L["neck"])
    head_c = at(chin, up, L["head"] / 2); head_c = (head_c[0] + 1.0, head_c[1])
    bones = []
    def leg(h, k, col, layer):
        knee = at(hip, h, L["upperLeg"]); ankle = at(knee, h - k, L["lowerLeg"])
        toe = at(ankle, 90, L["foot"] * 0.7)    # foot points forward
        bones.extend([(layer, hip, knee, THICK["upperLeg"], col),
                      (layer, knee, ankle, THICK["lowerLeg"], col),
                      (layer, ankle, toe, 2, col)])
    def arm(s, e, col, layer, sword=None):
        elbow = at(sternum, s, L["upperArm"]); wrist = at(elbow, s + e, L["forearm"])
        hand = at(wrist, s + e, L["hand"] * 0.6)
        sh = at(sternum, 0, 2.0)               # shoulder sits just under the neck line
        bones.extend([(layer, sh, sh, 6, col), (layer, sh, elbow, THICK["upperArm"], col),
                       (layer, elbow, wrist, THICK["forearm"], col),
                       (layer, wrist, hand, 2, col)])
        if sword is not None:
            tip = at(hand, s + e + sword, HERO_H * 0.32)   # sword: blade angle off the forearm, 0 = straight on
            bones.append((3, hand, tip, 1, SWORD))
    leg(pose["fh"], pose["fk"], FAR, 0); arm(pose["fs"], pose["fe"], FAR, 0)
    # torso as a tapered body (not a tube): hips, narrow waist, deep chest pushed forward, thin neck
    bones.append((1, hip, sternum, None, NEAR))
    bones.append((1, sternum, chin, 2, NEAR))
    leg(pose["nh"], pose["nk"], NEAR, 2); arm(pose["ns"], pose["ne"], NEAR, 2, pose["sword"])
    if pose["roll"]:
        r = math.radians(pose["roll"]); c, s_ = math.cos(r), math.sin(r)
        rot = lambda q: (q[0] * c - q[1] * s_, q[0] * s_ + q[1] * c)
        bones = [(l, rot(a), rot(b), t, col) for l, a, b, t, col in bones]
        head_c = rot(head_c)
    return bones, head_c

# --- adapter: draw a pose into a cell -------------------------------------------------
def draw_pose(pose):
    bones, head_c = solve(pose)
    r = L["head"] / 2 - 0.6           # head reads smaller than the shoulders
    pts = [q for _, a, b, *_ in bones for q in (a, b)] + [(head_c[0], head_c[1] + r)]
    low = max(q[1] for q in pts)               # lowest point lands on the pivot row
    xs = [q[0] for q in pts]; mid = (min(xs) + max(xs)) / 2 if pose["roll"] else 0.0
    ox, oy = PIVOT[0] - mid, PIVOT[1] - low
    img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    T = lambda q: (round(q[0] + ox), round(q[1] + oy))
    for layer in (0, 1, 2, 3):
        for l, a, b, t, col in bones:
            if l != layer: continue
            if t is None:                      # tapered torso
                Lt = math.dist(a, b); ax, ay = (b[0] - a[0]) / Lt, (b[1] - a[1]) / Lt
                nx, ny = -ay, ax                # forward side of the torso
                prof = [(0.0, 3.4, 3.4), (0.42, 2.6, 2.4), (0.8, 3.6, 4.6), (1.0, 3.6, 3.0)]  # (t, back, front)
                front, back = [], []
                for tt, bk, fr in prof:
                    cx, cy = a[0] + ax * Lt * tt, a[1] + ay * Lt * tt
                    front.append(T((cx + nx * fr, cy + ny * fr))); back.append(T((cx - nx * bk, cy - ny * bk)))
                d.polygon(front + back[::-1], fill=NEAR)
                continue
            d.line([T(a), T(b)], fill=col, width=t)
            for q in (a, b):
                x, y = T(q); h = t // 2
                if t > 2: d.ellipse([x - h, y - h, x + h, y + h], fill=col)
        if layer == 1:
            x, y = T(head_c); d.ellipse([x - r, y - r, x + r, y + r], fill=NEAR)
    return img

# --- sheet ----------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    cells = [(name, i, pose, dur) for name, keys in MOVES.items() for i, (pose, dur) in enumerate(keys)]
    rows = math.ceil(len(cells) / COLS)
    W, H = COLS * CELL, rows * CELL
    sheet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frames, tags, slice_keys, n = [], [], [], 0
    for name, keys in MOVES.items():
        start = n
        for i, (pose, dur) in enumerate(keys):
            x, y = (n % COLS) * CELL, (n // COLS) * CELL
            sheet.alpha_composite(draw_pose(pose), (x, y))
            frames.append({"filename": f"hero {n}.aseprite",
                           "frame": {"x": x, "y": y, "w": CELL, "h": CELL},
                           "rotated": False, "trimmed": False,
                           "spriteSourceSize": {"x": 0, "y": 0, "w": CELL, "h": CELL},
                           "sourceSize": {"w": CELL, "h": CELL}, "duration": dur})
            n += 1
        tags.append({"name": name, "from": start, "to": n - 1, "direction": "forward", "color": "#000000ff"})
    slice_keys.append({"frame": 0, "bounds": {"x": 0, "y": 0, "w": CELL, "h": CELL},
                       "pivot": {"x": PIVOT[0], "y": PIVOT[1]}})
    data = {"frames": frames,
            "meta": {"app": "https://www.aseprite.org/", "version": "1.3",
                     "image": "hero.png", "format": "RGBA8888", "size": {"w": W, "h": H}, "scale": "1",
                     "frameTags": tags,
                     "layers": [{"name": "hero", "opacity": 255, "blendMode": "normal"}],
                     "slices": [{"name": "pivot", "color": "#0000ffff", "keys": slice_keys}],
                     "x_vaniagraybox": {"cell": CELL, "heroHeight": HERO_H, "pivot": list(PIVOT),
                                        "source": "make_hero.py (Vitruvian seed); replace with Saji's export"}}}
    sheet.save(os.path.join(OUT, "hero.png"))
    with open(os.path.join(OUT, "hero.json"), "w") as f:
        json.dump(data, f, indent=1)

    # guide: 4x, grid, labels, baseline, pivot
    S = 4
    g = Image.new("RGBA", (W * S, H * S), (255, 255, 255, 255))
    g.alpha_composite(sheet.resize((W * S, H * S), Image.NEAREST).point(lambda v: v), (0, 0))
    gd = ImageDraw.Draw(g)
    try: font = ImageFont.load_default(size=11)
    except TypeError: font = ImageFont.load_default()
    names = [(nm, i) for nm, i, *_ in cells]
    for k, (nm, i) in enumerate(names):
        x, y = (k % COLS) * CELL * S, (k // COLS) * CELL * S
        gd.rectangle([x, y, x + CELL * S - 1, y + CELL * S - 1], outline=(200, 200, 200, 255))
        by = y + PIVOT[1] * S + S
        gd.line([x, by, x + CELL * S - 1, by], fill=(230, 60, 60, 255))                 # baseline
        px = x + PIVOT[0] * S + S // 2
        gd.line([px, by - 6, px, by + 6], fill=(30, 30, 140, 255), width=2)              # pivot
        hy = by - HERO_H * S
        gd.line([x, hy, x + 10, hy], fill=(30, 30, 140, 255))                            # height mark
        gd.text((x + 4, y + 3), f"{nm} {i}", fill=(30, 30, 140, 255), font=font)
    g.save(os.path.join(OUT, "hero_guide.png"))
    print(f"{len(cells)} keyframes, {len(tags)} animations, sheet {W}x{H}, cell {CELL}, hero {HERO_H}px")

if __name__ == "__main__":
    main()
