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

def mean_delta(pixels_a, pixels_b):
    count = len(pixels_a)
    total = sum(sum(abs(a - b) for a, b in zip(ca, cb)) / 3
                for ca, cb in zip(pixels_a, pixels_b))
    return total / count

def validate_ground():
    metadata = json.loads((GROUND / "tileset.json").read_text(encoding="utf-8"))
    assert metadata["tile_width"] == S and metadata["tile_height"] == S
    assert len(metadata["materials"]) == len(MATERIALS) == 8
    atlas = Image.open(GROUND / "forest_ground_atlas.png").convert("RGBA")
    assert atlas.size == (4 * S, 2 * S)
    repeat_preview = Image.open(GROUND / "forest_ground_repeat_preview.png").convert("RGBA")
    assert repeat_preview.size == (12 * S, 6 * S)
    for index, name in enumerate(MATERIALS):
        tile = Image.open(GROUND / f"{name}.png").convert("RGBA")
        assert tile.size == (S, S), f"{name}: wrong dimensions"
        assert tile.getchannel("A").getextrema() == (255, 255), f"{name}: unexpected transparency"
        expected = atlas.crop(((index % 4) * S, (index // 4) * S,
                               (index % 4 + 1) * S, (index // 4 + 1) * S))
        assert ImageChops.difference(tile, expected).getbbox() is None, f"{name}: atlas mismatch"
        repeated = repeat_preview.crop(((index % 4) * 3 * S, (index // 4) * 3 * S,
                                        (index % 4 + 1) * 3 * S, (index // 4 + 1) * 3 * S))
        for ry in range(3):
            for rx in range(3):
                cell = repeated.crop((rx * S, ry * S, (rx + 1) * S, (ry + 1) * S))
                assert ImageChops.difference(tile, cell).getbbox() is None, (
                    f"{name}: repeat preview cell {rx},{ry} mismatch")

        px = tile.convert("RGB").load()
        horizontal_seam = mean_delta([px[S - 1, y] for y in range(S)],
                                     [px[0, y] for y in range(S)])
        horizontal_inner = mean_delta(
            [px[x, y] for y in range(S) for x in range(S - 1)],
            [px[x + 1, y] for y in range(S) for x in range(S - 1)])
        vertical_seam = mean_delta([px[x, S - 1] for x in range(S)],
                                   [px[x, 0] for x in range(S)])
        vertical_inner = mean_delta(
            [px[x, y] for x in range(S) for y in range(S - 1)],
            [px[x, y + 1] for x in range(S) for y in range(S - 1)])
        assert horizontal_seam <= horizontal_inner * 2.0 + 2, (
            f"{name}: horizontal seam discontinuity {horizontal_seam:.2f} "
            f"vs all internal edges {horizontal_inner:.2f}")
        assert vertical_seam <= vertical_inner * 2.0 + 2, (
            f"{name}: vertical seam discontinuity {vertical_seam:.2f} "
            f"vs all internal edges {vertical_inner:.2f}")
        print(f"PASS tile {name}: seam H={horizontal_seam:.2f}/{horizontal_inner:.2f}, "
              f"V={vertical_seam:.2f}/{vertical_inner:.2f}")

def validate_masks():
    metadata = json.loads((MASKS / "blob_masks.json").read_text(encoding="utf-8"))
    assert metadata["layout"] == "47-tile-blob"
    entries = metadata["masks"]
    assert len(entries) == 47, f"expected 47 masks, found {len(entries)}"
    assert len({entry["neighbor_mask"] for entry in entries}) == 47
    assert entries[0]["neighbor_mask"] == 0
    atlas = Image.open(MASKS / "forest_blob_masks.png").convert("L")
    assert atlas.size == (8 * S, 6 * S)
    blend_preview = Image.open(MASKS / "forest_blob_blend_preview.png").convert("RGBA")
    assert blend_preview.size == (8 * S, 6 * S)
    for entry in entries:
        mask = Image.open(MASKS / entry["file"]).convert("L")
        assert mask.size == (S, S), f"{entry['file']}: wrong dimensions"
        if entry["neighbor_mask"] != 0:
            assert mask.getextrema()[1] > 0, f"{entry['file']}: unexpected empty nonzero mask"
    print("PASS autotile masks: 47 valid neighbor configurations, mask atlas and blended preview")

if __name__ == "__main__":
    validate_ground()
    validate_masks()
    print("ALL FOREST ASSET CHECKS PASSED")
