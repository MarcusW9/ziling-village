# Ziling Village: project rules

Cozy top-down browser game for learning HSK 1 Mandarin. See README.md for the full picture.

## How the project fits together

- `index.html` is the main game. It is one self-contained file: code, CSS and every image embedded as data URIs. It also runs on GitHub Pages, so keep its `<!doctype>`, `<head>` and UTF-8 charset.
- `tools/spirits.py` rebuilds the six spirit sprites at one shared visible height. Run it after changing any spirit sheet in `assets/sprites/`.
- `tools/layout.py` owns the village layout. It also generates the lantern glow points from the red lanterns in each lantern object. It re-embeds every placed asset and the detailed ground into `index.html`. **After changing any asset or position, run `python3 tools/layout.py` from the repo root** instead of hand-editing the `OBJS` array or the `MAPIMG` data URI.
- `layout.py` also holds `SHADOWS` (contact shadow per building, as fractions of its image) and `WINDOWS` (window and door rectangles that light up at night). Moving a building moves its shadow and windows.
- Placement entries are `(key, file, centre_x, base_y, width, flip)` on a 640×360 map. `base_y` is where the object touches the ground, used for depth sorting with the player and spirits.
- `painted-map.html` is the older single-image version, kept for comparison only.
- Check the script still parses after edits: extract the `<script>` block and run `node --check`.

## Asset rules

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
