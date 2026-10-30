#!/usr/bin/env python3
"""Generate a deterministic 64px forest ground material prototype.

Every tonal field uses integer-frequency Fourier harmonics with a 64px period.
Decorative clusters stay away from borders so repeated tiles do not expose
randomly cut details at their joins. This is a base material pack, not final
hand-painted environment art.
"""
from pathlib import Path
import math
import random
import json
from PIL import Image, ImageDraw

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

# Integer frequency pairs make the sampled field periodic at exactly 64px.
HARMONICS = (
    (1, 0, .22), (0, 1, .19), (1, 1, .17), (2, -1, .14),
    (1, 2, .11), (2, 1, .09), (3, 0, .07), (0, 3, .07),
)

def periodic_noise(x, y, seed):
    total = 0.0
    weight = 0.0
    phase_base = seed * .017
    for i, (kx, ky, amplitude) in enumerate(HARMONICS):
        phase = phase_base * (i + 1)
        angle = 2 * math.pi * (kx * x + ky * y) / S + phase
        total += math.sin(angle) * amplitude
        weight += amplitude
    return total / weight

def tonal_color(value, palette):
    # Four deliberately limited colors keep the material in a pixel-art range.
    if value < .31:
        return palette[0]
    if value < .54:
        return palette[1]
    if value < .78:
        return palette[2]
    return palette[3]

def put_pattern(image, x, y, pattern, color):
    # Keep all authored marks inside a safe border; only the periodic field
    # reaches the tile boundary.
    for dx, dy in pattern:
        px, py = x + dx, y + dy
        if 3 <= px < S - 3 and 3 <= py < S - 3:
            image.putpixel((px, py), (*color, 255))

def decorate(name, image, palette, seed):
    rng = random.Random(seed ^ 0x5A17)
    base, mid, light, high = palette

    if name.startswith("grass"):
        tufts = [
            ((0, 2), (1, 1), (2, 0), (2, 2)),
            ((0, 1), (1, 0), (1, 2), (2, 1)),
            ((0, 2), (1, 1), (2, 1), (3, 0)),
            ((0, 1), (1, 0), (2, 1)),
        ]
        for _ in range(24):
            put_pattern(image, rng.randrange(5, 55), rng.randrange(5, 55),
                        rng.choice(tufts), rng.choice((light, light, high, base)))

    elif name == "dirt":
        pebbles = [
            ((0, 0), (1, 0), (0, 1)),
            ((0, 0), (1, 0), (2, 0), (1, 1)),
            ((0, 0), (0, 1), (1, 1), (2, 1)),
        ]
        for _ in range(25):
            put_pattern(image, rng.randrange(5, 55), rng.randrange(5, 55),
                        rng.choice(pebbles), rng.choice((base, mid, high)))

    elif name == "forest_path":
        for _ in range(19):
            x, y = rng.randrange(5, 54), rng.randrange(5, 54)
            pattern = rng.choice((
                ((0, 0), (1, 0), (2, 0), (3, 0)),
                ((0, 1), (1, 0), (2, 0)),
                ((0, 0), (1, 0), (1, 1), (2, 1)),
            ))
            put_pattern(image, x, y, pattern, rng.choice((base, mid, light)))

    elif name == "stone":
        for _ in range(13):
            x, y = rng.randrange(6, 53), rng.randrange(6, 53)
            put_pattern(image, x, y, ((0, 0), (1, 0), (1, 1), (2, 1)),
                        rng.choice((base, mid)))
        for _ in range(11):
            put_pattern(image, rng.randrange(5, 55), rng.randrange(5, 55),
                        ((0, 0), (1, 0)), rng.choice((light, high)))

    elif name == "sand":
        for _ in range(28):
            x, y = rng.randrange(5, 55), rng.randrange(5, 55)
            put_pattern(image, x, y,
                        rng.choice((((0, 0), (1, 0), (2, 0)),
                                    ((0, 0), (1, 0)),
                                    ((0, 1), (1, 0), (2, 0)))),
                        rng.choice((mid, light, high)))

    elif name == "water":
        for _ in range(17):
            x, y = rng.randrange(5, 52), rng.randrange(5, 55)
            put_pattern(image, x, y,
                        rng.choice((((0, 0), (1, 0), (2, 0), (3, 0)),
                                    ((0, 0), (1, 0), (2, 0)),
                                    ((0, 1), (1, 0), (2, 0)))),
                        rng.choice((light, high)))

    elif name == "mud":
        for _ in range(20):
            x, y = rng.randrange(5, 55), rng.randrange(5, 55)
            put_pattern(image, x, y,
                        rng.choice((((0, 0), (1, 0), (0, 1), (1, 1)),
                                    ((0, 0), (1, 0), (2, 0)),
                                    ((0, 0), (0, 1), (1, 1)))),
                        rng.choice((base, mid, light)))

def make_material(name, palette, seed):
    image = Image.new("RGBA", (S, S), (0, 0, 0, 255))
    for y in range(S):
        for x in range(S):
            value = max(0.0, min(1.0, .5 + periodic_noise(x, y, seed) * .47))
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
        "note": "Procedural base materials for iteration; not final hand-painted production art."
    }
    (OUT / "tileset.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(tiles)} 64x64 materials and a {columns}x{rows} atlas in {OUT}")

if __name__ == "__main__":
    main()
