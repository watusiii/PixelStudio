# Pixel studio — scope, workflow, business model

Nov 18, 2026 · @Law

## The studio

Law + Saji: pixel art that works in an engine, plus the eye that keeps a studio from buying fakes. The market is scared right now: a publisher killed a contracted game over AI promo art and the studio shut down ([Goonswarm, Dec 2025](https://spilled.gg/studio-goonswarm-games-scissors-postal-spin-off-art-allegations)); another publisher bans gen-AI assets by contract after a vendor slipped some in ([Hooded Horse](https://spilled.gg/publisher-hooded-horse-contracts-patch-icons)).

Decided (Law, Nov 18): hand-made with proof, plus technical understanding. Law spots and fixes fakes because he knows both hand-crafted pixel art and AI. AI knowledge powers the audit; every shipped pixel is drawn by hand or placed by our own code under the artist's direction, with process proof shipped.

AI policy (decided, Law + Saji, Nov 18): no AI image generators (Stable Diffusion and the like), ever, for anything. Pixels may be placed by code: scripts (e.g. Python + Pillow) that place or fix pixels programmatically, written by us, AI-assisted coding allowed. Code is a tool like Aseprite's filters; the artist directs and approves every pixel that ships, and we disclose the tools. Published on the site as the studio's AI policy: a trust asset.

Roles (Law, Nov 18): Saji is the artist and only makes top-quality work. Law handles everything else: art direction and audit, pipeline and engine, systems, clients, business. Saji never touches code, scripts or admin; Law's job is to make his inputs simple (a clear brief, one place to drop files).

Law also coaches Saji on the technical side (live on stream, short tutorials) so Saji stays on art. Risk: Saji says he hasn't animated much and isn't confident yet, and the chosen look is animation-heavy. First coaching: an organized animation workspace (tags per animation, layers, onion skin, timeline) like the dev Law saw in voice chat.

## MVP game and the centerpiece

The MVP is a small game built to produce the portfolio. The centerpiece is one scene that proves everything at once: one hall or room in the classic tradition (hero, enemies, tiles, background, GUI, VFX all in one frame), playable, with its making shown.

- Scope (Law, Nov 18): one main character, two enemies, a GUI, one level. As soon as possible.
- Rough load: at NES level, hero \~40 frames and each enemy \~15, about 70 hours of animation at 1 frame an hour. At the chosen Symphony of the Night level, expect roughly 3-5x that (about 200-350 hours) before the level art. Real numbers come from the sprint.
- Genre: Mega Man / Castlevania-type side-scroller (Law, Nov 18). Look: Castlevania, Symphony of the Night era (Saji's pick). That raises the hours roughly 3-5x over NES; keep the level to one hall or room at that quality. First milestone: hero idle, walk and attack plus one room's tiles. Open: end date (Law asks Saji), engine

## Asset range

- Hero: idle, walk, run, jump, attack, hurt, death
- Two enemies (a boss later, not in the MVP)
- Tileset: terrain with full autotile set, animated tiles
- Props and interactables
- Backgrounds: parallax layers
- UI/HUD: bars, frames, icons, a bitmap font
- VFX: hits, projectiles, dust
- Later, not in the MVP: portraits, key art
- Proof: palette sheet, layer files, timelapse

## Workflow

1. Brief and reference board
2. Lock scale, grid, palette
3. Silhouettes, then keyframes
4. In-betweens, cleanup
5. Export sheets + metadata, test in engine
6. QA checklist, delivery package with source files and proof

To learn while sprinting: real frame and hour counts per asset type. Those set the prices.

Studio tooling (Law's side, code, no image generators): sprite scripting and engine import, scripted pixel fixes, internal templates (placeholder sprites, collision masks, palette ramps), and a procedural pattern kit Saji can pull from. The pattern kit overlaps the Genuary kit (field core, colour): build once, use in both.

## Services and pricing (working ranges, to test)

Market floor: $2-10 per animation frame on cheap listings; a top-rated Fiverr artist charges $30-120 base by sprite size plus $10-20 a frame ([sansh\_pixel](https://fiverr.com/sansh_pixel/create-a-pixel-art-background-or-environment-for-your-game)). North America hourly: about $30 entry, $50 mid, $100+ senior ([RocketBrush](https://rocketbrush.com/blog/2d-character-art-prices-and-tips-to-cut-costs)).

| Service | Working range (USD) |
| --- | --- |
| Asset audit (provenance + QA) | 150-500 flat |
| Fix/convert to real pixel art | per asset, quoted from hours |
| Character, full set (\~40 frames, NES level; more at SotN level) | 600-1,500 |
| Tileset with autotiles | 300-800 |
| Art direction retainer | 500-2,000 / month |

These are guesses until the sprint gives real hours.

## Collateral

- **Case studies = the MVP broken out.** One page per asset: the asset, its frames, palette, process timelapse, a clip of it in the game, and short copy on the choices made.
- **Website (Law builds it):** home with the centerpiece room; work (case studies); services and rates; audit; AI policy; about; contact.
- **SEO:** aim at what devs actually search: hiring a pixel artist for an indie game, and how to tell AI pixel art from real. Public teardowns that teach the second one double as the SEO engine.
- **Name:** later, but before the site and accounts.
- **Marketing:** owner open, maybe Saji; Law watches first. Until then: every asset is a post as it's made, on ONE studio account, not three platforms.
- **Paper:** audit one-pager, contract with an originality clause and process proof, 50% deposit, revision limit, intake form, delivery checklist.

## Open

- [ ] Engine for the MVP
- [ ] Deal (Law, Nov 18): Law owns and runs the studio; all money 50/50, audits included; the studio owns the art. To do: Saji's yes in one text
- [ ] Studio name (before the site and accounts)
- [ ] MVP end date (scope is set; Law asks Saji)
- [ ] Fit with Genuary in December
- [ ] Real hours per asset from the sprint, then set prices
