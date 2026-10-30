# Tools and Production Pipeline

## Selected map and tileset editor: 2D Tiler

Repository: https://github.com/2dtiler/app  
Website: https://2dtiler.com/  
License: MIT (verify the upstream LICENSE file before vendoring or modifying source).

2D Tiler is the primary candidate for assembling modular maps and configuring terrain/autotile rules. Its documented workflow includes layered maps, tilesets, terrain rules, pixel-level edits, palettes, and exports for multiple 2D engines.

### Why it fits this project

- Layered maps and object layers keep the world editable.
- Terrain-aware painting supports standard, diagonal, sparse, and Wang-style workflows.
- Tilesets and maps can be imported/exported independently.
- Palette import helps maintain a consistent art direction.
- Reference-image input is available in supported AI asset-generation workflows.

Important: the editor is a production tool, not an art-style generator. It does not guarantee assets will match our reference. All artwork must be reviewed against `ART_DIRECTION.md`.

## Supporting autotile utility: Autotiler

Repository: https://github.com/itsjavi/autotiler  
Use case: convert a properly authored terrain template into common 47-tile blob or 16-tile dual-grid layouts, with exports for supported tools/engines.

This is a helper, not a replacement for creating high-quality terrain art. Do not use it to stretch or mechanically transform an unsuitable source image into a supposedly finished tileset.

## Optional map-editor alternative: Tiled

Website: https://www.mapeditor.org/  
Tiled is a mature general-purpose map editor with orthogonal, isometric, and hexagonal map support. Keep it as an alternative if a later engine pipeline requires its native map format or more specialized map-editing workflows.

## Project workflow

1. Create and approve source art as independent assets, matching the reference perspective, scale, pixel density, palette, and lighting.
2. Build terrain sheets with complete edge/corner transitions and meaningful variants.
3. Import approved sheets into 2D Tiler and configure terrain/autotile rules.
4. Assemble maps with separate terrain, water, decoration, structure, and object layers.
5. Export source maps and tilesets; retain editable native project files.
6. Validate the exported result in the target game runtime before calling it production-ready.

## Asset provenance

Third-party tools and assets are separate concerns. A tool's open-source license does not grant rights to artwork found in its examples, screenshots, or community packs. Every external art asset must have its own recorded source and license before it is added to the game.
