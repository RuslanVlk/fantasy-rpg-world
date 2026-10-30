#!/usr/bin/env python3
"""Generate a reusable 47-configuration 8-neighbour blob-mask template set."""
from pathlib import Path
import itertools
import json
import math
from PIL import Image, ImageDraw

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

def build_mask(value):
    image = Image.new("L", (S, S), 0)
    draw = ImageDraw.Draw(image)

    north, east, south, west = (bool(value & CARDINALS[k]) for k in ("N", "E", "S", "W"))
    ne, se, sw, nw = (bool(value & DIAGONALS[k]) for k in ("NE", "SE", "SW", "NW"))

    # Every cell has a central body. Connected cardinal neighbours extend it
    # to the corresponding edge through broad rounded necks.
    draw.ellipse((20, 20, 44, 44), fill=255)
    if north:
        draw.rounded_rectangle((17, -16, 47, 39), radius=15, fill=255)
    if east:
        draw.rounded_rectangle((25, 17, 80, 47), radius=15, fill=255)
    if south:
        draw.rounded_rectangle((17, 25, 47, 80), radius=15, fill=255)
    if west:
        draw.rounded_rectangle((-16, 17, 39, 47), radius=15, fill=255)

    # A valid diagonal fills the outside corner. When both cardinals connect
    # but the diagonal does not, an inward bite creates a concave inner corner.
    corners = (
        ("NE", ne, north and east, (64, 0)),
        ("SE", se, east and south, (64, 64)),
        ("SW", sw, south and west, (0, 64)),
        ("NW", nw, west and north, (0, 0)),
    )
    for name, diagonal, both_sides, (cx, cy) in corners:
        if not both_sides:
            continue
        if diagonal:
            draw.ellipse((cx - 23, cy - 23, cx + 23, cy + 23), fill=255)
        else:
            draw.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=0)

    return image

