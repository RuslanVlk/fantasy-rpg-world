# Asset sources and integration decisions

Research date: 2026-10-31

## Integrated source

### Kenney — Roguelike/RPG Pack
- Official page: https://kenney.nl/assets/roguelike-rpg-pack
- License: CC0 1.0 (commercial use and modification allowed; attribution not required).
- Grid: 16×16.
- Perspective: 3/4 RPG presentation.
- Project copy: `assets/third_party/kenney_roguelike/`
- The repository already contains the source sheet, transparent sheet, tile catalog, extracted tile cells, and credits. Reuse these files before importing another pack.

## Candidate sources reviewed

### Kenney — Tiny Town
- Official page: https://kenney.nl/assets/tiny-town
- CC0. Potentially useful for buildings and village props only after visual scale/perspective comparison with the approved reference.
- Do not mix blindly with the existing environment palette.

### Aamatniekss — Free Topdown Fantasy Forest
- Page: https://aamatniekss.itch.io/topdown-fantasy-forest
- Free for commercial projects and modification.
- 16×16 orthographic top-down. Not approved for direct integration because it does not match the project's diagonal 3/4 reference.

### Reodesuxz — Free Pixel Top-down Forest and Village
- Page: https://reodesuxz.itch.io/free-pixel-top-down-forest-and-village-tileset-16x16
- Free for commercial projects.
- Orthographic top-down. Not approved for direct integration for the same perspective mismatch.

## Integration rules

1. Prefer assets already present in the Kenney CC0 source pack and the project's extracted environment assets.
2. A candidate must match the approved diagonal 3/4 projection, pixel density, scale, outline treatment, and lighting before it is imported.
3. Do not combine unrelated packs merely to increase asset count.
4. Keep original source files and license/credit notes.
5. Preserve individual transparent sprites; do not flatten the world into a background image.
6. For trees, separate the walk-blocking trunk/footprint from the canopy draw layer. Sort canopy and props by their ground anchor.
7. Test every new asset in the forest demo map at native gameplay zoom before accepting it.

## Remaining environment coverage to build and validate

- River banks, shallow/deep water transitions, waterfall segments and splash pools.
- Bridge pieces with a clearly walkable deck and non-walkable supports.
- Ruins and shrine pieces with modular corners/edges.
- Cave entrance and small house assembled from separate parts.
- More distinct tree silhouettes, rocks, roots, logs and ground cover.
- Player/NPC animation sheets matching the approved character reference.

These are coverage targets, not claims that the assets already exist.
