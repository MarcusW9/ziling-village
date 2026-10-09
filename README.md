# 字灵村 Ziling Village

A cozy top-down browser game for learning HSK 1 Mandarin. An old calligrapher's brush spilled its magic over a Jiangnan water town, and the characters painted on its signs came alive as shy spirits. You befriend them by learning their words.

## Play

Open `index.html` in a browser. Everything is in that one file, so no server or build step is needed.

| File | What it is |
| --- | --- |
| `index.html` | Main version. The village is built in layers from separate assets, so characters walk behind trees and buildings. |
| `painted-map.html` | Earlier version that uses one painted map image as the world. Kept for comparison. |

Progress saves in the browser (localStorage).

## What's in the game

- Two areas: the village (canal, bridge, square, tea house, calligrapher, market, home, Granny Wang's house) and the south area (inn, pavilion, garden). Walk off the bottom of the square to reach the south area.
- Nine spirits, each owning a set of HSK 1 words: 小字 brush (your companion), 茶茶 tea, 钱钱 coin, 家家 hearth, 日月 sundial, 雨雨 rain, 牛牛 clay ox, and in the south 鱼鱼 koi and 饱饱 clay stove.
- Four chores: tea house sentence building, market tag sorting, Granny Wang's quiz, and calligrapher radical puzzles.
- Per-word mastery stages 1–4. Pinyin fades word by word, reviews are spaced, and a day cycle ends when you rest at home.

## Folder layout

```
index.html            main game (layered)
painted-map.html      earlier single-image version
assets/
  buildings/          tea house, calligrapher, homes, stalls, bridge
  props/ props2/      well, sundial, notice board, lanterns, umbrella, tea tray...
  trees/ bushes/      plum, bamboo, camphor, pine, maple, willows, shrubs
  life/               fences, gate, washing line, firewood, jars, carts, bench
  decorations/        lantern pole, stone lantern, incense burner, banners, shrine, koi pond
  south/              pieces cut from the painted south map (courtyard house, inn, pavilion, stalls, shrines, boat)
  ground/ canal/      grass, flowers, rocks, moss, leaves; lily pads, reeds, jetty, boat
  village2/           second building sheet (courtyard house, farmhouse, beds, stalls...)
  sprites/            spirit sheets, player sheet, covered boat
  map/                ground base and the two painted reference maps
  source-sheets/      the original AI images every asset was cut from
tools/
  magcut.py           cut a magenta-background sheet into separate PNGs
  mapcut.py           cut objects out of a painted map (grass, paving, dirt, water background); south_cuts.json lists the south pieces
  sprite2.py          shrink a spirit concept into 32x32 game sprites
  player.py           shrink the player sheet into walk frames
  fringe.py           clean light fringes off cut-outs
  layout.py           the village layout: places every asset and rebuilds index.html
  layout_south.py     the south garden quarter layout, built the same way
```

## Changing the village layout

All placement lives in `tools/layout.py`. Each entry is `(key, file, centre_x, base_y, width, flip)` on a 640×360 map, where `base_y` is where the object touches the ground (used for depth sorting). Edit an entry, then run from the repo root:

```
python3 tools/layout.py
```

## Art direction rules

1. **Willows belong to the water.** The canal is lined with willows, with a matched pair framing the square.
2. **Three depth bands.** The background (top edge) is a tree canopy behind buildings. The midground (buildings, paths, the square) stays clear and readable. The foreground (bottom edge) is a row of trees framing the view.
3. **One accent tree per landmark.** The plum blossom marks the tea house and the red maple marks the calligrapher. Keep colour sparing so it means something.
4. **Every house has a yard story.** Props sit against walls and fences, not floating on grass.
5. **Symmetry at entrances.** Paired lions, lamp posts, lantern poles and azaleas.
6. **Details cluster where they would grow.** Grass at tree bases, dry grass along fences, rocks at wall corners, flowers in single-colour drifts beside paths.
7. **Open lawns stay open.** Empty grass gives the eye somewhere to rest.
8. **Water life in calm groups.** Lily pads and the moored boat sit near the square, with reeds at the canal ends.

## Making new assets

Generate on a **solid flat magenta (#FF00FF) background**. Magenta never appears in the art, so cut-outs come out clean. Grey or white backgrounds leave fringes on plaster walls and awnings.

Start every prompt with:

```
Cozy pixel art for a top-down life-sim game set in a Chinese water town (Jiangnan style, like Wuzhen or Zhouzhuang). 16-bit style, top-down three-quarter view, limited palette: white plaster, dark grey-black tiled roofs, warm brown wood, red lanterns, green canal water, mossy stone. Clean dark outlines, flat shading with one highlight, soft warm lighting.
```

End every prompt with:

```
On a solid flat magenta #FF00FF background. No grid, no shadow on the ground, no text, no letters, no Chinese characters, no labels. Same scale and style as the reference image.
```

Upload `assets/buildings/tea_house.png` as the style reference. Leave signs and banners blank; the game adds real Chinese text in code, so AI never writes fake characters.

## Next steps

- Collision, so the player can't walk through buildings, trees or fences
- Redraw the six spirits in Aseprite with one shared palette
- Move to Phaser 3 + Tiled, as planned in the design document
