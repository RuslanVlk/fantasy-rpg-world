#!/usr/bin/env python3
"""Compose a deterministic forest test map from generated terrain and CC0 props."""
from pathlib import Path
import json
import math
import random
from PIL import Image
from forest_autotile import neighbor_mask, mask_filename

ROOT = Path(__file__).resolve().parents[1]
GROUND = ROOT / "assets" / "tilesets" / "forest_ground"
MASK_DIR = GROUND / "blob_masks"
TREE_DIR = ROOT / "assets" / "environment" / "forest" / "trees"
PLANT_DIR = ROOT / "assets" / "environment" / "forest" / "plants"
OUT = ROOT / "assets" / "maps" / "forest_demo"

CELL = 64
MAP_W = 20
MAP_H = 14
SEED = 20261030

def disk_cells(cx, cy, radius):
    result = set()
    for y in range(max(0, math.floor(cy - radius)), min(MAP_H, math.ceil(cy + radius) + 1)):
        for x in range(max(0, math.floor(cx - radius)), min(MAP_W, math.ceil(cx + radius) + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                result.add((x, y))
    return result

def line_cells(points):
    result = set()
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx - dy
        x, y = x0, y0
        while True:
            result.add((x, y))
            if (x, y) == (x1, y1):
                break
            doubled = 2 * error
            if doubled > -dy:
                error -= dy
                x += sx
            if doubled < dx:
                error += dx
                y += sy
    return result

def within_map(cells):
    return {(x, y) for x, y in cells if 0 <= x < MAP_W and 0 <= y < MAP_H}

def build_terrain_layers():
    water = set()
    for x in range(MAP_W):
        center_y = round(4.0 + 1.45 * math.sin(x * 0.34) + 0.45 * math.sin(x * 0.77))
        water.add((x, center_y))
        water.add((x, center_y + 1))
    water |= disk_cells(3, 8, 1.5)

    sand = set(water)
    for x, y in water:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < MAP_W and 0 <= yy < MAP_H:
                    sand.add((xx, yy))

    path = line_cells(((0, 12), (4, 11), (8, 12), (12, 11), (16, 12), (19, 10)))
    path = within_map(path) - water - sand

    light_grass = set()
    for cx, cy, radius in ((2, 2, 1.5), (7, 8, 1.5), (13, 8, 1.3), (18, 8, 1.4), (10, 1, 1.2)):
        light_grass |= disk_cells(cx, cy, radius)
    light_grass = within_map(light_grass) - sand - path

    stone = set()
    for cx, cy in ((8, 7), (16, 8)):
        stone |= disk_cells(cx, cy, 0.9)
    stone = within_map(stone) - sand - path - light_grass

    return {
        "grass_light": light_grass,
        "sand": sand,
        "water": water,
        "forest_path": path,
        "stone": stone,
    }

def load_material_records():
    metadata = json.loads((GROUND / "tileset.json").read_text(encoding="utf-8"))
    records = {item["name"]: item["variants"] for item in metadata["materials"]}
    cache = {}
    for name, filenames in records.items():
        cache[name] = [
            (relative, Image.open(GROUND / relative).convert("RGBA"))
            for relative in filenames
        ]
    return cache

def choose_texture(material, texture_cache, rng):
    choices = texture_cache[material]
    relative, texture = rng.choice(choices)
    return relative, texture

def place_overlay(canvas, cells, material, texture_cache, rng):
    grid = {coord: material for coord in cells}
    records = []
    for x, y in sorted(cells, key=lambda point: (point[1], point[0])):
        value = neighbor_mask(grid, x, y, material)
        mask_path = MASK_DIR / mask_filename(value)
        mask = Image.open(mask_path).convert("L")
        relative, texture = choose_texture(material, texture_cache, rng)
        box = (x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL)
        base_cell = canvas.crop(box)
        canvas.paste(Image.composite(texture, base_cell, mask), (x * CELL, y * CELL))
        records.append({
            "x": x, "y": y, "material": material,
            "neighbor_mask": value,
            "mask": f"assets/tilesets/forest_ground/blob_masks/{mask_filename(value)}",
            "texture": f"assets/tilesets/forest_ground/{relative}"
        })
    return records

def make_base_layer(texture_cache, rng):
    image = Image.new("RGBA", (MAP_W * CELL, MAP_H * CELL), (0, 0, 0, 255))
    records = []
    for y in range(MAP_H):
        for x in range(MAP_W):
            relative, texture = choose_texture("grass_deep", texture_cache, rng)
            image.paste(texture, (x * CELL, y * CELL))
            records.append({
                "x": x, "y": y, "material": "grass_deep",
                "texture": f"assets/tilesets/forest_ground/{relative}"
            })
    return image, records

def load_props():
    trees = json.loads((TREE_DIR / "trees.json").read_text(encoding="utf-8"))["sprites"]
    plants = json.loads((PLANT_DIR / "plants.json").read_text(encoding="utf-8"))["sprites"]
    return trees, plants

def select_props(terrain_layers, rng):
    blocked = set().union(*terrain_layers.values())
    tree_manifest, plant_manifest = load_props()
    tree_records = {item["id"]: item for item in tree_manifest}
    plant_records = {item["id"]: item for item in plant_manifest}

    candidates = [
        (1, 1, "tree_tall_01"), (5, 1, "tree_tall_03"),
        (9, 2, "tree_dead_01"), (14, 1, "tree_tall_06"),
        (18, 1, "tree_tall_05"), (1, 8, "tree_small_02"),
        (6, 9, "tree_fruit_01"), (12, 9, "tree_tall_04"),
        (17, 8, "tree_small_05"), (4, 9, "tree_tall_02"),
        (10, 9, "tree_small_03"), (19, 8, "tree_small_01"),
        (15, 9, "tree_small_04"), (11, 9, "tree_small_06"),
    ]
    selected_trees = []
    occupied = set()
    for x, y, sprite_id in candidates:
        if (x, y) in blocked or (x, y) in occupied:
            continue
        entry = tree_records[sprite_id]
        height_cells = max(1, math.ceil(entry["size"][1] / 16))
        footprint = {(x, y - offset) for offset in range(height_cells)}
        if footprint & blocked:
            continue
        if any(abs(x - old_x) <= 1 and abs(y - old_y) <= 1
               for old_x, old_y, _ in selected_trees):
            continue
        selected_trees.append((x, y, sprite_id))
        occupied.add((x, y))

    open_cells = [
        (x, y) for y in range(MAP_H) for x in range(MAP_W)
        if (x, y) not in blocked and (x, y) not in occupied
    ]
    rng.shuffle(open_cells)
    plant_ids = list(plant_records)
    selected_plants = []
    for x, y in open_cells:
        if len(selected_plants) >= 18:
            break
        if any(abs(x - tx) <= 1 and abs(y - ty) <= 1 for tx, ty, _ in selected_trees):
            continue
        selected_plants.append((x, y, rng.choice(plant_ids)))

    result = []
    for x, y, sprite_id in selected_trees:
        entry = tree_records[sprite_id]
        result.append({
            "id": f"prop_{len(result) + 1:03d}",
            "type": "tree",
            "sprite": f"assets/environment/forest/trees/{entry['file']}",
            "sprite_id": sprite_id,
            "cell": [x, y],
            "size": entry["size"],
            "anchor": "bottom_center",
            "sort_y": (y + 1) * CELL
        })
    for x, y, sprite_id in selected_plants:
        entry = plant_records[sprite_id]
        result.append({
            "id": f"prop_{len(result) + 1:03d}",
            "type": "plant",
            "sprite": f"assets/environment/forest/plants/{entry['file']}",
            "sprite_id": sprite_id,
            "cell": [x, y],
            "size": entry["size"],
            "anchor": "bottom_center",
            "sort_y": (y + 1) * CELL
        })
    return result

def render_props(props):
    canvas = Image.new("RGBA", (MAP_W * CELL, MAP_H * CELL), (0, 0, 0, 0))
    for item in sorted(props, key=lambda record: (record["sort_y"], record["cell"][0])):
        path = ROOT / item["sprite"]
        sprite = Image.open(path).convert("RGBA")
        sprite = sprite.resize((sprite.width * 4, sprite.height * 4), Image.Resampling.NEAREST)
        x, y = item["cell"]
        px = x * CELL + (CELL - sprite.width) // 2
        py = (y + 1) * CELL - sprite.height
        canvas.alpha_composite(sprite, (px, py))
        item["pixel_position"] = [px, py]
        item["display_size"] = list(sprite.size)
    return canvas

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    texture_cache = load_material_records()
    layers = build_terrain_layers()
    ground, base_records = make_base_layer(texture_cache, rng)

    layer_records = [{"name": "base", "material": "grass_deep", "cells": base_records}]
    for material in ("grass_light", "sand", "water", "stone", "forest_path"):
        records = place_overlay(ground, layers[material], material, texture_cache, rng)
        layer_records.append({"name": material, "material": material, "cells": records})

    props = select_props(layers, rng)
    prop_image = render_props(props)
    final_image = Image.alpha_composite(ground, prop_image)

    ground.save(OUT / "forest_demo_ground.png", optimize=True)
    prop_image.save(OUT / "forest_demo_props.png", optimize=True)
    final_image.save(OUT / "forest_demo_map.png", optimize=True)
    final_image.resize((final_image.width * 2, final_image.height * 2),
                       Image.Resampling.NEAREST).save(OUT / "forest_demo_map_2x.png", optimize=True)

    manifest = {
        "format": "fantasy-rpg-forest-demo-v1",
        "seed": SEED,
        "projection": "diagonal 3/4",
        "grid": {"width": MAP_W, "height": MAP_H, "tile_width": CELL, "tile_height": CELL},
        "render_size": list(final_image.size),
        "layers": layer_records,
        "objects": props,
        "previews": {
            "combined": "forest_demo_map.png",
            "ground": "forest_demo_ground.png",
            "props": "forest_demo_props.png",
            "combined_2x": "forest_demo_map_2x.png"
        },
        "notes": [
            "This is a composition and autotile smoke-test map, not a finished game level.",
            "Ground cell textures use deterministic random selection from four variants per material.",
            "Tree and plant sprites are scaled 4x with nearest-neighbour filtering for the 64px ground grid.",
            "The source props are Kenney Roguelike/RPG assets under CC0-1.0."
        ]
    }
    (OUT / "forest_demo_map.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Forest demo map\n\n"
        "A 20×14 composition smoke test built from the procedural ground materials, 47 connected blob masks, "
        "and independently extracted CC0 tree/plant PNG sprites. It includes a winding river with sand bank, "
        "a dirt footpath, stone patches, mixed grass and layered props.\n\n"
        "Files: forest_demo_map.png (combined preview), forest_demo_ground.png (terrain only), "
        "forest_demo_props.png (transparent prop layer), forest_demo_map_2x.png (nearest-neighbour 2× preview), "
        "and forest_demo_map.json (cell layers and prop placements).\n\n"
        "This is an integration test map, not final hand-authored world art.\n",
        encoding="utf-8"
    )
    print(f"Rendered {MAP_W}x{MAP_H} forest demo map with {len(props)} props in {OUT}")

if __name__ == "__main__":
    main()
