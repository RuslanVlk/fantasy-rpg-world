# Forest ground and transition resources

This folder contains a deterministic 64×64 material prototype, four texture
variants per material, atlases, and a generic 47-configuration blob-mask library.

## Ground materials

Eight base RGBA PNGs are generated: grass_deep, grass_light, dirt, forest_path,
stone, sand, water, and mud. Each material has four distinct 64×64 textures.
The alternate files are in variants/; tileset.json maps the four file paths.
forest_ground_atlas.png contains the eight base materials (4×2).
forest_ground_variants_atlas.png groups four variants per material (4×8).
forest_ground_repeat_preview.png shows a 3×3 repeat for each base texture.

## Autotile mask library

blob_masks/ contains 47 connected 8-neighbour alpha masks. White selects overlay
terrain A; black leaves base terrain B visible. Each mask includes a central
terrain body, connected cardinal lobes, and concave/convex diagonal corners.
The bit layout is documented in blob_masks/blob_masks.json. A renderer samples
the eight neighbouring cells and composites the selected mask over the base.

## Rebuild and validation

```bash
python -m pip install -r requirements-assets.txt
python tools/generate_forest_tiles.py
python tools/generate_blob_masks.py
python tools/validate_forest_assets.py
```

GitHub Actions generates, validates and commits the files, then uploads a ZIP
artifact. Validation checks dimensions, atlas consistency, distinct variants,
repeat-edge continuity, all 47 connected masks, and separate licensed prop PNGs.

These are working technical base resources, not final hand-painted game art.
The forest reference remains the authority for final palette, texture detail,
transitions, props, trees, rocks and the overall visual match.
