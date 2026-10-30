#!/usr/bin/env python3
"""Generate a deterministic, tileable 64px forest ground material prototype.

The base texture is built from wrapped value-noise fields at multiple scales,
then quantized to a restrained palette. Material-specific pixel clusters add
recognizable grass, grit, stone, sand and water marks. This is a technical
prototype pack, not final hand-painted environment art.
"""
from pathlib import Path
import math
import random
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "tilesets" / "forest_ground"
S = 64
SEED = 20261030

MATERIALS = {
    "grass_deep": ((32, 59, 39), (49, 82, 48), (76, 108, 59), (107, 137, 76)),
    "grass_light": ((43, 70, 39), (65, 98, 49), (94, 126, 65), (127, 151, 85)),
    "dirt": ((66, 45, 32), (91, 61, 41), (119, 84, 55), (151, 111, 76)),
    "forest_path": ((72, 52, 37), (101, 73, 49), (130, 98, 67), (158, 126, 88)),
    "stone": ((59, 64, 62), (83, 88, 83), (113, 115, 104), (148, 146, 127)),
    "sand": ((119, 101, 66), (150, 130, 84), (181, 158, 106), (210, 188, 134)),
    "water": ((20, 53, 72), (27, 76, 94), (40, 105, 119), (75, 143, 148)),
    "mud": ((51, 52, 39), (75, 72, 49), (105, 96, 62), (136, 122, 81)),
}

def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)

def make_periodic_noise(grid, seed):
    """Return a smooth noise sampler with an exact 64px repeat period."""
    rng = random.Random(seed + grid * 997)
    lattice = [[rng.random() * 2.0 - 1.0 for _ in range(grid)]
               for _ in range(grid)]

    def sample(x, y):
        gx = x * grid / S
        gy = y * grid / S
        ix, iy = int(gx), int(gy)
        fx, fy = smoothstep(gx - ix), smoothstep(gy - iy)
        a = lattice[iy % grid][ix % grid]
        b = lattice[iy % grid][(ix + 1) % grid]
        c = lattice[(iy + 1) % grid][ix % grid]
        d = lattice[(iy + 1) % grid][(ix + 1) % grid]
        top = a * (1.0 - fx) + b * fx
        bottom = c * (1.0 - fx) + d * fx
        return top * (1.0 - fy) + bottom * fy

    return sample

def tonal_color(value, palette):
    if value < .35:
        return palette[0]
    if value < .49:
        return palette[1]
    if value < .63:
        return palette[2]
    return palette[3]

def put_pattern(image, x, y, pattern, color):
    # Decorative clusters stay inside a four-pixel safety border. Only the
    # periodic material field reaches the tile edges.
    for dx, dy in pattern:
        px, py = x + dx, y + dy
        if 4 <= px < S - 4 and 4 <= py < S - 4:
            image.putpixel((px, py), (*color, 255))

def decorate(name, image, palette, seed):
    rng = random.Random(seed ^ 0x5A17)
    base, mid, light, high = palette

    if name.startswith("grass"):
        tufts = (
            ((0, 2), (1, 1), (2, 0), (2, 2)),
            ((0, 1), (1, 0), (1, 2), (2, 1)),
            ((0, 2), (1, 1), (2, 1), (3, 0)),
            ((0, 1), (1, 0), (2, 1)),
        )
        for _ in range(22):
            put_pattern(image, rng.randrange(6, 54), rng.randrange(6, 54),
                        rng.choice(tufts), rng.choice((light, light, high, base)))

    elif name == "dirt":
        pebbles = (
            ((0, 0), (1, 0), (0, 1)),
            ((0, 0), (1, 0), (2, 0), (1, 1)),
            ((0, 0), (0, 1), (1, 1), (2, 1)),
        )
        for _ in range(23):
            put_pattern(image, rng.randrange(6, 54), rng.randrange(6, 54),
                        rng.choice(pebbles), rng.choice((base, mid, high)))

    elif name == "forest_path":
        for _ in range(18):
            pattern = rng.choice((
                ((0, 0), (1, 0), (2, 0), (3, 0)),
                ((0, 1), (1, 0), (2, 0)),
                ((0, 0), (1, 0), (1, 1), (2, 1)),
            ))
            put_pattern(image, rng.randrange(6, 53), rng.randrange(6, 53),
                        pattern, rng.choice((base, mid, light)))

    elif name == "stone":
        for _ in range(12):
            put_pattern(image, rng.randrange(6, 53), rng.randrange(6, 53),
                        ((0, 0), (1, 0), (1, 1), (2, 1)), rng.choice((base, mid)))
        for _ in range(10):
            put_pattern(image, rng.randrange(6, 54), rng.randrange(6, 54),
                        ((0, 0), (1, 0)), rng.choice((light, high)))

    elif name == "sand":
        for _ in range(25):
            pattern = rng.choice((
                ((0, 0), (1, 0), (2, 0)),
                ((0, 0), (1, 0)),
                ((0, 1), (1, 0), (2, 0)),
            ))
            put_pattern(image, rng.randrange(6, 54), rng.randrange(6, 54),
                        pattern, rng.choice((mid, light, high)))

    elif name == "water":
        for _ in range(16):
            pattern = rng.choice((
                ((0, 0), (1, 0), (2, 0), (3, 0)),
                ((0, 0), (1, 0), (2, 0)),
                ((0, 1), (1, 0), (2, 0)),
            ))
            put_pattern(image, rng.randrange(6, 52), rng.randrange(6, 54),
                        pattern, rng.choice((light, high)))

    elif name == "mud":
        for _ in range(18):
            pattern = rng.choice((
                ((0, 0), (1, 0), (0, 1), (1, 1)),
                ((0, 0), (1, 0), (2, 0)),
                ((0, 0), (0, 1), (1, 1)),
            ))
            put_pattern(image, rng.randrange(6, 54), rng.randrange(6, 54),
                        pattern, rng.choice((base, mid, light)))

def make_material(name, palette, seed):
    fields = [
        make_periodic_noise(grid, seed + index * 173)
        for index, grid in enumerate((4, 8, 16, 32))
    ]
    weights = (.18, .34, .30, .18)
    image = Image.new("RGBA", (S, S), (0, 0, 0, 255))
    for y in range(S):
        for x in range(S):
            noise = sum(weight * field(x, y)
                        for weight, field in zip(weights, fields))
            value = max(0.0, min(1.0, .5 + noise * .34))
            image.putpixel((x, y), (*tonal_color(value, palette), 255))
    decorate(name, image, palette, seed)
    return image

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = list(MATERIALS)
    tiles = []
    for index, (name, palette) in enumerate(MATERIALS.items()):
        tile = make_material(name, palette, SEED + index * 101)
        tile.save(OUT / f"{name}.png", optimize=True)
        tiles.append(tile)

    columns = 4
    rows = (len(tiles) + columns - 1) // columns
    atlas = Image.new("RGBA", (columns * S, rows * S), (0, 0, 0, 0))
    for index, tile in enumerate(tiles):
        atlas.alpha_composite(tile, ((index % columns) * S, (index // columns) * S))
    atlas.save(OUT / "forest_ground_atlas.png", optimize=True)

    metadata = {
        "tile_width": S,
        "tile_height": S,
        "atlas_columns": columns,
        "atlas_rows": rows,
        "projection": "diagonal 3/4",
        "materials": [
            {"id": index, "name": name, "file": f"{name}.png"}
            for index, name in enumerate(names)
        ],
        "generator_seed": SEED,
        "tileable": True,
        "texture_method": "multi-scale periodic value noise plus material-specific pixel clusters",
        "note": "Procedural base materials for iteration; not final hand-painted production art."
    }
    (OUT / "tileset.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(tiles)} 64x64 materials and a {columns}x{rows} atlas in {OUT}")

if __name__ == "__main__":
    main()
