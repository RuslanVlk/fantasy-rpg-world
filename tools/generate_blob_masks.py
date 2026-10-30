#!/usr/bin/env python3
"""Generate a reusable 47-configuration 8-neighbour blob-mask template set."""
from pathlib import Path
import itertools
import json
import math
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "tilesets" / "forest_ground" / "blob_masks"
S = 64
CARDINALS = {"N": 1, "E": 2, "S": 4, "W": 8}
DIAGONALS = {"NE": 16, "SE": 32, "SW": 64, "NW": 128}
ALL_BITS = {**CARDINALS, **DIAGONALS}

def valid_masks():
    results = []
    for cardinal_bits in range(16):
        active = {
            "N": bool(cardinal_bits & 1),
            "E": bool(cardinal_bits & 2),
            "S": bool(cardinal_bits & 4),
            "W": bool(cardinal_bits & 8),
        }
        allowed = []
        if active["N"] and active["E"]: allowed.append("NE")
        if active["E"] and active["S"]: allowed.append("SE")
        if active["S"] and active["W"]: allowed.append("SW")
        if active["W"] and active["N"]: allowed.append("NW")
        for choices in itertools.product((False, True), repeat=len(allowed)):
            value = cardinal_bits
            for name, enabled in zip(allowed, choices):
                if enabled:
                    value |= DIAGONALS[name]
            results.append(value)
    return sorted(results)

def edge_depth(t, offset):
    wave = (math.sin(2 * math.pi * (t + offset) / S) * 1.5 +
            math.sin(4 * math.pi * (t + offset * 2) / S) * .8)
    return 10 + round(wave)

def build_mask(value):
    image = Image.new("L", (S, S), 0)
    px = image.load()
    north, east, south, west = (bool(value & CARDINALS[k]) for k in ("N", "E", "S", "W"))
    ne, se, sw, nw = (bool(value & DIAGONALS[k]) for k in ("NE", "SE", "SW", "NW"))

    for y in range(S):
        for x in range(S):
            covered = (
                (north and y < edge_depth(x, 0)) or
                (east and x >= S - edge_depth(y, 9)) or
                (south and y >= S - edge_depth(x, 17)) or
                (west and x < edge_depth(y, 25))
            )

            # Diagonal neighbours add a rounded lobe. Missing diagonals where
            # both adjacent sides exist create a concave cut rather than a square.
            corners = (
                ("NE", ne, north and east, x >= S - 20 and y < 20, S - x, y),
                ("SE", se, east and south, x >= S - 20 and y >= S - 20, S - x, S - y),
                ("SW", sw, south and west, x < 20 and y >= S - 20, x, S - y),
                ("NW", nw, west and north, x < 20 and y < 20, x, y),
            )
            for _, diagonal, both_sides, in_zone, dx, dy in corners:
                if both_sides and in_zone:
                    distance_sq = dx * dx + dy * dy
                    if diagonal and distance_sq <= 20 * 20:
                        covered = True
                    elif not diagonal and distance_sq <= 8 * 8:
                        covered = False

            px[x, y] = 255 if covered else 0
    return image

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    values = valid_masks()
    columns, rows = 8, 6
    atlas = Image.new("L", (columns * S, rows * S), 0)
    entries = []
    for index, value in enumerate(values):
        filename = f"mask_{value:03d}.png"
        image = build_mask(value)
        image.save(OUT / filename, optimize=True)
        atlas.paste(image, ((index % columns) * S, (index // columns) * S))
        entries.append({
            "index": index,
            "neighbor_mask": value,
            "file": filename,
            "neighbors": [name for name, bit in ALL_BITS.items() if value & bit],
        })
    atlas.save(OUT / "forest_blob_masks.png", optimize=True)
    metadata = {
        "layout": "47-tile-blob",
        "tile_width": S,
        "tile_height": S,
        "atlas_columns": columns,
        "atlas_rows": rows,
        "white": "overlay terrain A",
        "black": "leave base terrain B visible",
        "bit_flags": ALL_BITS,
        "diagonal_rule": "A diagonal flag is valid only when both adjacent cardinal flags are set.",
        "edge_depth_pixels": 10,
        "masks": entries,
        "note": "Generic alpha templates; the game map renderer must select a mask from the 8-neighbour terrain pattern."
    }
    (OUT / "blob_masks.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(entries)} valid blob masks in {OUT}")

if __name__ == "__main__":
    main()
