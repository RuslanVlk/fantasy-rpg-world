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

def validate_kenney_source():
    source = ROOT / "assets" / "third_party" / "kenney_roguelike"
    image = Image.open(source / "roguelikeSheet_transparent.png").convert("RGBA")
    assert image.size == (968, 526), f"Kenney source sheet has unexpected dimensions: {image.size}"
    preview = Image.open(source / "roguelikeSheet_preview_3x.png").convert("RGBA")
    assert preview.size == (2904, 1578)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["license"] == "CC0-1.0"
    assert manifest["tile_size"] == 16 and manifest["spacing"] == 1
    assert len(manifest["occupied_cells"]) > 100
    assert (source / "CREDITS.md").exists()
    catalog = json.loads((source / "tile_catalog.json").read_text(encoding="utf-8"))
    tile_dir = source / "tile_cells"
    tile_files = list(tile_dir.glob("*.png"))
    assert catalog["count"] == len(manifest["occupied_cells"]) == len(tile_files)
    for entry in catalog["tiles"]:
        tile = Image.open(source / entry["file"]).convert("RGBA")
        assert tile.size == (16, 16), f"{entry['file']}: wrong dimensions"
        assert tile.getchannel("A").getbbox() is not None, f"{entry['file']}: blank tile"
    print(f"PASS Kenney CC0 source: {catalog['count']} independent 16x16 PNG cells")

def validate_forest_trees():
    tree_dir = ROOT / "assets" / "environment" / "forest" / "trees"
    metadata = json.loads((tree_dir / "trees.json").read_text(encoding="utf-8"))
    assert metadata["license"] == "CC0-1.0"
    assert metadata["count"] == 14
    assert len(metadata["sprites"]) == 14
    for entry in metadata["sprites"]:
        sprite = Image.open(tree_dir / entry["file"]).convert("RGBA")
        assert list(sprite.size) == entry["size"], f"{entry['file']}: wrong dimensions"
        assert sprite.getchannel("A").getbbox() is not None, f"{entry['file']}: blank sprite"
    preview = Image.open(tree_dir / "trees_contact_sheet.png").convert("RGBA")
    assert preview.size == (288, 448)
    print("PASS forest trees: 6 small + 6 tall + 1 fruit + 1 dead tree sprites")

def validate_forest_plants():
    plant_dir = ROOT / "assets" / "environment" / "forest" / "plants"
    metadata = json.loads((plant_dir / "plants.json").read_text(encoding="utf-8"))
    assert metadata["license"] == "CC0-1.0"
    assert metadata["count"] == 8 and len(metadata["sprites"]) == 8
    for entry in metadata["sprites"]:
        sprite = Image.open(plant_dir / entry["file"]).convert("RGBA")
        assert sprite.size == (16, 16), f"{entry['file']}: wrong dimensions"
        assert sprite.getchannel("A").getbbox() is not None, f"{entry['file']}: blank sprite"
    preview = Image.open(plant_dir / "plants_contact_sheet.png").convert("RGBA")
    assert preview.size == (240, 240)
    print("PASS forest plants: 4 flower variants + 2 ground-cover + 2 berry shrubs")

def validate_ground():
    metadata = json.loads((GROUND / "tileset.json").read_text(encoding="utf-8"))
    assert metadata["tile_width"] == S and metadata["tile_height"] == S
    assert len(metadata["materials"]) == len(MATERIALS) == 8
    assert metadata["variants_per_material"] == 4
    atlas = Image.open(GROUND / "forest_ground_atlas.png").convert("RGBA")
    assert atlas.size == (4 * S, 2 * S)
    variants_atlas = Image.open(GROUND / "forest_ground_variants_atlas.png").convert("RGBA")
    assert variants_atlas.size == (4 * S, 8 * S)
    repeat_preview = Image.open(GROUND / "forest_ground_repeat_preview.png").convert("RGBA")
    assert repeat_preview.size == (12 * S, 6 * S)
    for index, name in enumerate(MATERIALS):
        tile = Image.open(GROUND / f"{name}.png").convert("RGBA")
        assert tile.size == (S, S), f"{name}: wrong dimensions"
        assert tile.getchannel("A").getextrema() == (255, 255), f"{name}: unexpected transparency"
        expected = atlas.crop(((index % 4) * S, (index // 4) * S,
                               (index % 4 + 1) * S, (index // 4 + 1) * S))
        assert ImageChops.difference(tile, expected).getbbox() is None, f"{name}: atlas mismatch"
        record = metadata["materials"][index]
        assert record["name"] == name and len(record["variants"]) == 4
        for variant_index, relative_path in enumerate(record["variants"]):
            variant = Image.open(GROUND / relative_path).convert("RGBA")
            assert variant.size == (S, S), f"{relative_path}: wrong dimensions"
            atlas_cell = variants_atlas.crop((variant_index * S, index * S,
                                              (variant_index + 1) * S, (index + 1) * S))
            assert ImageChops.difference(variant, atlas_cell).getbbox() is None, (
                f"{relative_path}: variant atlas mismatch")
            if variant_index:
                assert variant.tobytes() != tile.tobytes(), f"{relative_path}: duplicate of base texture"
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
        print(f"PASS tile {name} + 3 variants: seam H={horizontal_seam:.2f}/{horizontal_inner:.2f}, "
              f"V={vertical_seam:.2f}/{vertical_inner:.2f}")

def validate_forest_demo_map():
    demo = ROOT / "assets" / "maps" / "forest_demo"
    metadata = json.loads((demo / "forest_demo_map.json").read_text(encoding="utf-8"))
    assert metadata["format"] == "fantasy-rpg-forest-demo-v1"
    import hashlib
    generator_path = ROOT / "tools" / "generate_forest_demo_map.py"
    expected_generator_hash = hashlib.sha256(generator_path.read_bytes()).hexdigest()
    assert metadata.get("generator_script_sha256") == expected_generator_hash, (
        "forest demo map is stale: regenerate it with the current map generator")
    grid = metadata["grid"]
    assert grid == {"width": 20, "height": 14, "tile_width": 64, "tile_height": 64}
    expected_size = (grid["width"] * 64, grid["height"] * 64)
    ground = Image.open(demo / "forest_demo_ground.png").convert("RGBA")
    props = Image.open(demo / "forest_demo_props.png").convert("RGBA")
    combined = Image.open(demo / "forest_demo_map.png").convert("RGBA")
    preview_2x = Image.open(demo / "forest_demo_map_2x.png").convert("RGBA")
    assert ground.size == props.size == combined.size == expected_size
    assert props.getchannel("A").getbbox() is not None
    assert preview_2x.size == (expected_size[0] * 2, expected_size[1] * 2)
    rebuilt = Image.alpha_composite(ground, props)
    assert ImageChops.difference(rebuilt, combined).getbbox() is None

    layers = metadata["layers"]
    assert len(layers) == 6
    assert layers[0]["name"] == "base"
    for layer in layers[1:]:
        assert layer["material"] in MATERIALS
        for cell in layer["cells"]:
            assert 0 <= cell["x"] < grid["width"] and 0 <= cell["y"] < grid["height"]
            mask_path = ROOT / cell["mask"]
            texture_path = ROOT / cell["texture"]
            assert mask_path.exists(), f"missing mask {cell['mask']}"
            assert texture_path.exists(), f"missing texture {cell['texture']}"
            assert 0 <= cell["neighbor_mask"] <= 255
    objects = metadata["objects"]
    assert len([obj for obj in objects if obj["type"] == "tree"]) >= 5
    assert len([obj for obj in objects if obj["type"] == "plant"]) >= 8
    for obj in objects:
        assert (ROOT / obj["sprite"]).exists(), f"missing prop sprite {obj['sprite']}"
        px, py = obj["pixel_position"]
        assert px >= 0 and py >= 0, f"prop clipped above/left map bounds: {obj['id']}"
    print(f"PASS forest demo map: {len(layers)} terrain layers + {len(objects)} placed props")

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
        assert mask.getextrema()[1] > 0, f"{entry['file']}: empty terrain body"
        if entry["neighbor_mask"] == 0:
            assert mask.getextrema()[0] == 0, "isolated mask must retain transparent outside"
            bbox = mask.getbbox()
            assert bbox == (20, 20, 45, 45), f"isolated terrain blob has wrong bounds: {bbox}"
        elif entry["neighbor_mask"] == 255:
            assert mask.getextrema() == (255, 255), "fully connected terrain mask must cover its whole cell"
        else:
            assert mask.getextrema()[0] == 0, f"{entry['file']}: transparent terrain complement missing"
    print("PASS autotile masks: 47 connected terrain shapes, isolated body, and fully connected cell")

if __name__ == "__main__":
    validate_kenney_source()
    validate_ground()
    validate_forest_trees()
    validate_forest_plants()
    validate_forest_demo_map()
    validate_masks()
    print("ALL FOREST ASSET CHECKS PASSED")
