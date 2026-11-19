# VaniaGraybox

Greybox SotN-style room: scrolling floor, parallax, and a hero controller with every animation slot.
The hero is a placeholder silhouette built from the Vitruvian seed. Every file is meant to be replaced.

Run: `python serve.py` (opens http://localhost:8000). Press `?` for controls.

## For Saji: replacing the hero

1. Open `assets/hero/hero_guide.png` in Aseprite: **File > Import Sprite Sheet**, type *By Rows*,
   cell **64 x 64** (guide is 4x, so import `hero.png` for 1:1, keep the guide as a reference layer).
2. One tag per animation, names exactly as below. Draw over the keyframes. Add as many in-between
   frames as you want: the game reads whatever is between a tag's first and last frame, with your durations.
3. Keep the feet on the **pivot**: bottom centre, x 32, y 62 (red baseline + blue tick on the guide).
   Optional: a slice named `pivot` in Aseprite overrides it.
4. **File > Export Sprite Sheet**: Layout *By Rows*, Output *JSON Data* (Array), check **Tags** and **Slices**,
   save over `assets/hero/hero.png` + `assets/hero/hero.json`.
5. In the game press `O` (or refresh). Your frames are in. `V` = viewer, cycle animations with `[` `]`. `T` = slow.

| tag | keyframes now | plays | goes to |
|---|---|---|---|
| idle | 2 | loop | |
| walk | 4 (contact, pass, contact, pass) | loop | |
| crouch | 1 | loop | |
| jump | 1 | loop while rising | fall |
| fall | 1 | loop while falling | land |
| land | 1 | once | idle |
| attack | 3 (windup, strike, recover) | once | idle |
| crouch_attack | 3 | once | crouch |
| jump_attack | 3 | once | fall |
| shoot | 2 (aim, recoil) | while the gun key is fresh | back to idle |
| walk_shoot | 4 (same legs as walk) | loop | back to walk |
| crouch_shoot | 1 | loop | back to crouch |
| jump_shoot | 1 | loop (rising and falling) | back to jump/fall |
| backdash | 2 | once | idle |
| hurt | 1 | once | idle |
| death | 3 (hit, kneel, down) | once | stays |

Gun frames: put a slice named `muzzle` on each shooting frame (1x1 at the barrel tip): bullets start there.
The bullet is its own sheet, `assets/bullet/` (tags `fly`, `hit`), same rules.
Shooting tags swap in on the **same frame number** as the move they ride on (walk frame 3 -> walk_shoot frame 3),
so keep their frame counts matched.

A tag the game can't find falls back to idle and shows as MISSING in the bar under the game.

## Adding a move

One row in `MOVES` in `src/hero.js` + a tag with the same name in Aseprite. That's it.
Rooms are data too: `assets/room.json` lists the layers, their speeds and the floor.

## Files

| file | what |
|---|---|
| `src/sprite.js` | reads any Aseprite JSON export (Array or Hash), plays tags, mirrors around the pivot |
| `src/hero.js` | the moves table + controller |
| `src/main.js` | loop, input, camera, parallax, HUD, viewer |
| `assets/room.json` | the room: size, floor height, layers (speed = 1/phi^n) |
| `assets/room/*.png` | sky, far, mid, near, floor (Saji's bricks, greyed), front |
| `assets/hero/` | `hero.png` + `hero.json` (what the game reads), `hero_guide.png` (draw over this) |
| `tools/make_hero.py` | regenerates the placeholder sheet from the Vitruvian rig |
| `tools/make_room.py` | regenerates the greybox room |
| `tools/make_bullet.py` | regenerates the placeholder bullet |

## Open

- Cell 64 x 64 and hero 48 px tall: to confirm with Saji.
- Shortsword fits the 64 cell (just). Gun + shortsword, two keys, Mega Man style.
