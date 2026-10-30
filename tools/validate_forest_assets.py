#!/usr/bin/env python3
"""Validate generated forest terrain and blob-mask resources."""
from pathlib import Path
import json
import sys
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
GROUND = ROOT / "assets" / "tilesets" / "forest_ground"
MASKS = GROUND / "blob_masks"
sys.path.insert(0, str(ROOT / "tools"))
from generate_forest_tiles import MATERIALS, S

def mean_rgb_delta(a, b):
    pa, pb = list(a.convert("RGB").getdata()), list(b.convert("RGB").getdata())
    return sum(sum(abs(x - y) for x, y in zip(ca, cb)) / 3 for ca, cb in zip(pa, pb)) / len(pa)

def validate_ground():
    metadata = json.loads((GROUND / "tileset.json").read_text(encoding="utf-8"))
    assert metadata["tile_width"] == S and metadata["tile_height"] == S
    assert len(metadata["materials"]) == len(MATERIALS) == 8
    atlas = Image.open(GROUND / "forest_ground_atlas.png").convert("RGBA")
    assert atlas.size == (4 * S, 2 * S)
    for index, name in enumerate(MATERIALS):
        tile = Image.open(GROUND / f"{name}.png").convert("RGBA")
        assert tile.size == (S, S), f"{name}: wrong dimensions"
        assert tile.getchannel("A").getextrema() == (255, 255), f"{name}: unexpected transparency"
        expected = atlas.crop(((index % 4) * S, (index // 4) * S,
                               (index % 4 + 1) * S, (index // 4 + 1) * S))
        assert ImageChops.difference(tile, expected).getbbox() is None, f"{name}: atlas mismatch"

        rgb = tile.convert("RGB")
        horizontal_seam = mean_rgb_delta(rgb.crop((0, 0, 1, S)),
                                         rgb.crop((S - 1, 0, S, S)))
        horizontal_inner = mean_rgb_delta(rgb.crop((0, 0, 1, S)),
                                          rgb.crop((1, 0, 2, S)))
        vertical_seam = mean_rgb_delta(rgb.crop((0, 0, S, 1)),
                                       rgb.crop((0, S - 1, S, S)))
        vertical_inner = mean_rgb_delta(rgb.crop((0, 0, S, 1)),
                                        rgb.crop((0, 1, S, 2)))
        assert horizontal_seam <= horizontal_inner * 2.6 + 4, (
            f"{name}: horizontal seam discontinuity {horizontal_seam:.2f} "
            f"vs internal {horizontal_inner:.2f}")
        assert vertical_seam <= vertical_inner * 2.6 + 4, (
            f"{name}: vertical seam discontinuity {vertical_seam:.2f} "
            f"vs internal {vertical_inner:.2f}")
        print(f"PASS tile {name}: seam H={horizontal_seam:.2f}/{horizontal_inner:.2f}, "
              f"V={vertical_seam:.2f}/{vertical_inner:.2f}")

def validate_masks():
    metadata = json.loads((MASKS / "blob_masks.json").read_text(encoding="utf-8"))
    assert metadata["layout"] == "47-tile-blob"
    entries = metadata["masks"]
    assert len(entries) == 47, f"expected 47 masks, found {len(entries)}"
    atlas = Image.open(MASKS / "forest_blob_masks.png").convert("L")
    assert atlas.size == (8 * S, 6 * S)
    for entry in entries:
        mask = Image.open(MASKS / entry["file"]).convert("L")
        assert mask.size == (S, S), f"{entry['file']}: wrong dimensions"
        assert mask.getextrema()[1] > 0, f"{entry['file']}: empty mask"
    print("PASS autotile masks: 47 valid neighbor configurations, 64x64 each")

if __name__ == "__main__":
    validate_ground()
    validate_masks()
    print("ALL FOREST ASSET CHECKS PASSED")
