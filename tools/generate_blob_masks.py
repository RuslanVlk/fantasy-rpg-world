#!/usr/bin/env python3
"""Generate reusable, connected 47-configuration 8-neighbour terrain masks."""
from pathlib import Path
import itertools
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
GROUND = ROOT / "assets" / "tilesets" / "forest_ground"
OUT = GROUND / "blob_masks"
S = 64
CARDINALS = {"N": 1, "E": 2, "S": 4, "W": 8}
DIAGONALS = {"NE": 16, "SE": 32, "SW": 64, "NW": 128}
ALL_BITS = {**CARDINALS, **DIAGONALS}

def valid_masks():
    result = []
    for cardinal_bits in range(16):
        active = {name: bool(cardinal_bits & bit) for name, bit in CARDINALS.items()}
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
            result.append(value)
    return sorted(result)

def build_mask(value):
    mask = Image.new("L", (S, S), 0)
    draw = ImageDraw.Draw(mask)
    n, e, s, w = (bool(value & CARDINALS[k]) for k in ("N", "E", "S", "W"))
    ne, se, sw, nw = (bool(value & DIAGONALS[k]) for k in ("NE", "SE", "SW", "NW"))

    # The center remains a connected terrain body even when surrounded by
    # base terrain. Cardinal neighbours extend that body to the tile edges.
    draw.ellipse((20, 20, 44, 44), fill=255)
    if n: draw.ellipse((15, -18, 49, 44), fill=255)
    if e: draw.ellipse((20, 15, 82, 49), fill=255)
    if s: draw.ellipse((15, 20, 49, 82), fill=255)
    if w: draw.ellipse((-18, 15, 44, 49), fill=255)

    corners = (
        (ne, n and e, (64, 0)),
        (se, e and s, (64, 64)),
        (sw, s and w, (0, 64)),
        (nw, w and n, (0, 0)),
    )
    for diagonal, both_sides, (cx, cy) in corners:
        if not both_sides:
            continue
        if diagonal:
            draw.ellipse((cx - 23, cy - 23, cx + 23, cy + 23), fill=255)
        else:
            draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=0)
    return mask

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    values = valid_masks()
    if len(values) != 47 or len(set(values)) != 47:
        raise ValueError(f"Expected 47 unique valid masks, got {len(values)}")

    columns, rows = 8, 6
    atlas = Image.new("L", (columns * S, rows * S), 0)
    entries = []
    for index, value in enumerate(values):
        filename = f"mask_{value:03d}.png"
        mask = build_mask(value)
        if mask.getextrema()[1] == 0:
            raise ValueError(f"Generated empty mask for neighbor configuration {value}")
        mask.save(OUT / filename, optimize=True)
        atlas.paste(mask, ((index % columns) * S, (index // columns) * S))
        entries.append({
            "index": index,
            "neighbor_mask": value,
            "file": filename,
            "neighbors": [name for name, bit in ALL_BITS.items() if value & bit],
        })
    atlas.save(OUT / "forest_blob_masks.png", optimize=True)

    grass = Image.open(GROUND / "grass_deep.png").convert("RGBA")
    dirt = Image.open(GROUND / "dirt.png").convert("RGBA")
    blend_preview = Image.new("RGBA", (columns * S, rows * S), (0, 0, 0, 0))
    for index, value in enumerate(values):
        mask = Image.open(OUT / f"mask_{value:03d}.png").convert("L")
        blended = Image.composite(grass, dirt, mask)
        blend_preview.alpha_composite(blended, ((index % columns) * S, (index // columns) * S))
    blend_preview.save(OUT / "forest_blob_blend_preview.png", optimize=True)

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
        "blend_preview": "forest_blob_blend_preview.png",
        "masks": entries,
        "note": "Connected mask templates. For a cell assigned overlay terrain A, set bits for its adjacent A cells and composite A over base B using the selected mask."
    }
    (OUT / "blob_masks.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(entries)} valid connected blob masks in {OUT}")

if __name__ == "__main__":
    main()
