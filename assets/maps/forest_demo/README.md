# Forest demo map

A 20×14 integration map built from the procedural ground materials, 47 connected
blob masks, and independently extracted Kenney Roguelike/RPG CC0 tree and plant
PNG sprites. It includes a winding river with a narrow sand bank, connected
footpath, stone patches, mixed grass and layered props.

## Files

- `forest_demo_map.png` — combined preview.
- `forest_demo_ground.png` — terrain-only layer.
- `forest_demo_props.png` — transparent prop layer.
- `forest_demo_map_2x.png` — 2× nearest-neighbour preview.
- `forest_demo_map.json` — source terrain cells, selected variants, masks and prop placements.
- `forest_demo_map.tmj` — editable Tiled JSON map.
- `forest_demo_ground.tsj` — atlas tileset for the 20×14 ground cells.
- `forest_demo_props.tsj` — image-collection tileset for separate tree and plant sprites.

## Tiled import

Open `forest_demo_map.tmj` directly in Tiled. The Ground layer uses a 20×14
image atlas whose cells are individually movable. Forest Props is an object
layer; each object refers to its own transparent PNG through an image-collection
tileset and uses bottom-center alignment so larger sprites can overlap lower
ground rows and be depth-sorted.

The map uses an orthogonal cell grid with 3/4-view art. It is a composition and
pipeline smoke test, not a final hand-authored level or a complete game scene.
