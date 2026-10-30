# Forest ground and transition resources

This folder contains a deterministic 64×64 material prototype, its atlas, and
a generic 47-configuration blob-mask library.

## Ground materials
Eight individual RGBA PNGs are generated: `grass_deep`, `grass_light`,
`dirt`, `forest_path`, `stone`, `sand`, `water`, and `mud`.
`forest_ground_atlas.png` is a 4×2 atlas; `tileset.json` describes its cells.

## Autotile mask library
`blob_masks/` contains 47 valid 8-neighbour alpha masks. White selects the
overlay terrain; black leaves the base terrain visible. The bit layout and
filenames are documented in `blob_masks/blob_masks.json`. A renderer still
needs to sample the eight neighbouring cells and composite the selected mask
between two material textures.

## Rebuild and validation

```bash
python -m pip install -r requirements-assets.txt
python tools/generate_forest_tiles.py
python tools/generate_blob_masks.py
python tools/validate_forest_assets.py
```

The GitHub Actions workflow runs all three stages, checks dimensions, atlas
consistency and edge continuity, then commits generated PNG/JSON assets to
`main` and uploads a ZIP artifact.

These are functional technical base resources, not final hand-painted game art.
The forest reference still governs final texture detail, transitions, props,
trees, rocks and the overall visual match.
