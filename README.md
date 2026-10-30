# Fantasy RPG World

A modular 2D pixel-art fantasy RPG world built around a consistent diagonal 3/4 perspective and a detailed, natural environment style.

## Visual direction

The project follows the supplied forest-world reference: richly detailed pixel art, readable diagonal perspective, layered natural forms, cohesive lighting and palette, and carefully blended transitions between terrain types.

This is an asset-driven project. Maps must be assembled from reusable tiles and independent objects rather than delivered as one flattened background image.

## Project structure

- `docs/` — visual standards, asset specifications, and production plan.
- `assets/tilesets/` — modular terrain and autotile sets.
- `assets/environment/` — trees, rocks, plants, water features, ruins, buildings, and props.
- `assets/characters/` — player, NPCs, creatures, and animation sheets.
- `assets/maps/` — modular map exports and source files.
- `references/` — approved visual references and style notes.

## Production rules

1. Match the approved reference style; do not drift into generic pixel-art or a different perspective.
2. Keep every asset separate and reusable wherever practical.
3. Avoid primitive geometric placeholders, obvious copy-paste repetition, and noisy pixel clusters.
4. Preserve consistent scale, outline treatment, lighting direction, palette, and pixel density.
5. Do not call an asset set complete until its edges, transitions, variants, and in-engine readability have been checked.
6. Record the source and license for every third-party asset. Do not assume an asset is reusable because it is hosted on GitHub.

## Initial environment target

A forest region with a river and lake, waterfalls, a bridge, paths, ruins, a small house, a cave entrance, a shrine, varied vegetation, rocks, and small environmental details. The area should be assembled from modular pieces and remain editable.

See [Art Direction](docs/ART_DIRECTION.md) and [Asset Production Plan](docs/ASSET_PRODUCTION_PLAN.md).
