# Ziling Village: project rules

Cozy top-down browser game for learning HSK 1 Mandarin. See README.md for the full picture.

## How the project fits together

- `index.html` is the main game. It is one self-contained file: code, CSS and every image embedded as data URIs. It also runs on GitHub Pages, so keep its `<!doctype>`, `<head>` and UTF-8 charset.
- `tools/player_walk.py` embeds the player's walk cycles: 4 frames down and up, 3 frames left and right, all native (no mirroring). Check every side frame faces its direction; one wrong frame makes the player 'moonwalk'. Run it after changing the frames in `assets/sprites/player/`.
- `tools/boat.py` embeds the 4-frame rowing boat, aligned on its canopy so only the boatman moves.
- `tools/spirits.py` rebuilds the original six spirit sprites at one shared visible height. Run it after changing any spirit sheet in `assets/sprites/`.
- `tools/spirits_new.py` builds 牛牛 (`niu`), 鱼鱼 (`fish`), 饱饱 (`bao`) and 喵喵 (`mao`) from individual pose PNGs into `SPR2` and their portraits into `AV2`. New spirits should be added here: a stage per evolution, poses `front`, `happy`, `sleep`, scaled per source sheet (sheets are drawn at different scales). `tools/twins.py` makes the cream twin by recolouring 鱼鱼.
- `tools/npcs.py` cuts the villager sheets (`assets/source-sheets/npc_<name>.png`) into poses and places each villager (`NPCS`: scene, position, idle pose, greet pose). Villagers show their greet pose when the player is within 48 px. Granny Wang predates this and is still drawn from `EXTRA`.
- `tools/pet.py` cuts the chow chow puppy sheet and embeds `PET` (walk frames per direction picked by hand after a facing check, plus sit, sleep and a gift portrait). Granny Wang gives him at the end of your first chat with her (day 1). Click him for 来 (follow) or 坐 (wait here, or stay home in the yard). While following he walks the player's trail and sniffs out unfound words within 60 px. His words 狗, 来, 坐 use `sp:'pet'`.
- `tools/kids.py` cuts the two village children's sheets (`npc_kid_boy.png`, `npc_kid_girl.png`) into poses and embeds `KIDS`. Side poses face right and are mirrored for left. In the game the kids walk a hand-placed path graph per scene (`KG`, because neither map's walk data keeps them off houses), cross between maps at the south exit (mostly staying on the player's map), play on their own or together (tag, sitting together, a drawing in the dirt), and at dusk go into Granny Wang's house (node `gd`, they are her grandchildren), coming back out in the morning. Move a node in `KG` if they clip a prop.
- Spirits may set `scene:'south'` to live in the south area. `evo2` adds a second evolution, reached when every word is still Mastered after a 7-day review (tracked in `S.m4`).
- `tools/layout.py` owns the village layout. It also generates the lantern glow points from the red lanterns in each lantern object. It re-embeds every placed asset and the detailed ground into `index.html`. **After changing any asset or position, run `python3 tools/layout.py` from the repo root** instead of hand-editing the `OBJS` array or the `MAPIMG` data URI.
- `layout.py` also holds `SHADOWS` (contact shadow per building, as fractions of its image) and `WINDOWS` (window and door rectangles that light up at night). Moving a building moves its shadow and windows. `SPLIT` cuts a building whose image includes its front yard at the wall line, so characters on the yard aren't drawn behind the house.
- Night windows are not filled rectangles: `tools/winmask.py` (used by both layout scripts) makes a per-window mask that lights only the dark room and lattice gaps, dimmer at the top and edges. Frames, plaster, red couplets and leaves stay unlit.
- Placement entries are `(key, file, centre_x, base_y, width, flip)` on a 640×360 map. `base_y` is where the object touches the ground, used for depth sorting with the player and spirits.
- `tools/layout_south.py` builds the south garden quarter the same way: ground, objects (including the courtyard yard props cut from `building_kit.png`), shadows, window lights, lantern glows, the walkable grid (water blocks walking, the footbridge doesn't) and its click areas. Its source images (`south_layout`, `south_ground`, `south_assets` in `assets/source-sheets/`) share one 1024×577 frame, so positions in the script are in that frame and scaled by 0.625. Run it after changing anything in the south area.
- The south area has no canal, on purpose: the village canal runs east–west, so the south uses a stream and koi pond instead.
- `painted-map.html` is the older single-image version, kept for comparison only.
- Check the script still parses after edits: extract the `<script>` block and run `node --check`.

## Asset rules

- `tools/defringe.py` removes light halos from a cut-out (edge pixels clearly lighter than the art inside them) and refills small holes. Run it on any sprite cut from a pale background.
- New art should be generated on a solid flat magenta (#FF00FF) background. Cut it with `tools/magcut.py`. Grey or white backgrounds leave fringes on plaster walls and awnings.
- Store originals in `assets/source-sheets/` and cut-outs in the matching `assets/<category>/` folder.
- No AI-written Chinese text in art. Signs and banners stay blank; real characters are drawn in code. Fake characters are worse than none in a game that teaches characters.
- Keep sprites at full detail. The user rejected downscaling them to match the map's chunky pixels.

## Art direction

1. Willows line the canal, with a matched pair framing the square.
2. Three depth bands: a tree canopy along the top, a clear midground, and framing trees along the bottom.
3. One accent tree per landmark: plum blossom at the tea house, red maple at the calligrapher.
4. Every house has a yard story, with props against walls, never floating.
5. Paired symmetry at entrances.
6. Ground details cluster where they would grow; flowers come in single-colour drifts.
7. Open lawns stay open.
8. Water life sits in calm groups.

Random scattering was tried and rejected as messy. Place things deliberately.

## Learning design (from the GDD)

- HSK 1 words only count toward mastery. HSK 2 words (河, 桥, 船) are preview words that don't count yet.
- Each word belongs to one spirit. Function words (我, 是, 的…) belong to none.
- No timers or fail states during learning; the clock pauses in any panel.

## Working with the user

- The user prefers direct, concrete answers and real judgments over hedging.
- Show visual changes (a screenshot or a published preview) rather than describing them.
- When a visual change is disliked, revert it exactly, keeping only the parts they asked to keep.

## Commits

- Commit as the user, never as Claude. Before the first commit in a session run:
  `git config user.name "MarcusW9" && git config user.email "160358373+MarcusW9@users.noreply.github.com"`
- No `Co-Authored-By: Claude` line in commit messages.

## Art prompts

- Put every image-generation prompt in a fenced code block, so the user can copy it in one click.
