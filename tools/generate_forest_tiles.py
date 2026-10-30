#!/usr/bin/env python3
"""Generate the first editable 64x64 forest terrain tile pack.

All textures are generated deterministically with Pillow and the Python standard
library. Each tile is exported separately as RGBA PNG plus a labeled-free atlas.
"""
from pathlib import Path
import random
from PIL import Image, ImageDraw

OUT = Path("assets/tilesets/forest_ground")
SIZE = 64
SEED = 20261030

PALETTES = {
    "grass_deep": ((39, 75, 48), (57, 99, 57), (78, 119, 66), (105, 137, 76)),
    "grass_light": ((58, 91, 49), (76, 116, 58), (101, 139, 69), (129, 151, 81)),
    "dirt": ((83, 57, 39), (105, 72, 47), (127, 91, 57), (148, 111, 71)),
    "forest_path": ((91, 67, 45), (116, 85, 55), (139, 106, 68), (158, 127, 83)),
    "stone": ((75, 79, 75), (99, 103, 94), (126, 128, 113), (151, 149, 128)),
    "sand": ((139, 119, 76), (164, 143, 91), (187, 164, 108), (207, 184, 128)),
    "water": ((30, 70, 88), (37, 93, 111), (49, 117, 129), (76, 143, 145)),
    "mud": ((67, 66, 47), (88, 83, 55), (111, 101, 64), (133, 119, 77)),
}

def make_tile(name, palette, seed):
    rng = random.Random(seed)
    base, mid, light, highlight = palette
    im = Image.new("RGBA", (SIZE, SIZE), (*base, 255))
    d = ImageDraw.Draw(im)
    # Broad irregular patches establish a natural, non-repeating ground texture.
    for _ in range(18):
        x, y = rng.randrange(-8, SIZE), rng.randrange(-8, SIZE)
        w, h = rng.randrange(7, 22), rng.randrange(5, 15)
        col = rng.choice([base, mid, mid, light])
        d.ellipse((x, y, x+w, y+h), fill=(*col, 255))
    # Pixel clusters, not isolated random noise.
    for _ in range(125):
        x, y = rng.randrange(2, SIZE-3), rng.randrange(2, SIZE-3)
        col = rng.choices([base, mid, light, highlight], [2, 5, 3, 1])[0]
        if rng.random() < 0.65:
            d.rectangle((x, y, x+rng.choice([1, 2, 3]), y+rng.choice([1, 2])), fill=(*col, 255))
        else:
            d.point((x, y), fill=(*col, 255))
    if name.startswith("grass"):
        # Small tufts with a consistent upper-left light.
        for _ in range(17):
            x, y = rng.randrange(4, 60), rng.randrange(4, 60)
            c = (*rng.choice([light, highlight]), 255)
            d.line((x, y+3, x-1, y), fill=c, width=1)
            d.point((x+2, y+1), fill=c)
    elif name == "stone":
        for _ in range(9):
            x, y = rng.randrange(4, 54), rng.randrange(4, 54)
            d.line((x, y, x+4, y-2), fill=(*highlight, 255), width=1)
            d.point((x+5, y+1), fill=(*base, 255))
    elif name == "water":
        # Broken horizontal glints follow the diagonal 3/4 ground plane.
        for _ in range(16):
            x, y = rng.randrange(3, 52), rng.randrange(4, 60)
            length = rng.randrange(3, 9)
            d.line((x, y, min(62, x+length), y-1), fill=(*highlight, 210), width=1)
            if rng.random() < .45:
                d.point((x+1, y+1), fill=(*light, 255))
    elif name in ("dirt", "forest_path", "mud", "sand"):
        for _ in range(12):
            x, y = rng.randrange(3, 60), rng.randrange(3, 60)
            d.rectangle((x, y, x+2, y+1), fill=(*highlight, 255))
    return im

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = list(PALETTES)
    tiles = []
    for i, name in enumerate(names):
        tile = make_tile(name, PALETTES[name], SEED+i*97)
        tile.save(OUT / f"{name}.png", optimize=True)
        tiles.append(tile)
    cols, rows = 4, (len(tiles)+3)//4
    atlas = Image.new("RGBA", (cols*SIZE, rows*SIZE), (0, 0, 0, 0))
    for i, tile in enumerate(tiles):
        atlas.alpha_composite(tile, ((i%cols)*SIZE, (i//cols)*SIZE))
    atlas.save(OUT / "forest_ground_atlas.png", optimize=True)
    (OUT / "tileset.json").write_text(
        '{\n  "tile_size": 64,\n  "columns": 4,\n  "tiles": '+str(names).replace("'", '"')+
        ',\n  "projection": "diagonal 3/4",\n  "generated_by": "tools/generate_forest_tiles.py"\n}\n',
        encoding="utf-8")
    print(f"Generated {len(tiles)} separate tiles and atlas in {OUT}")

if __name__ == "__main__":
    main()
