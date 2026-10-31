#!/usr/bin/env python3
"""Export walkability, tree-footprint collisions and canopy occlusion metadata."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / "assets" / "maps" / "forest_demo"
CELL = 64

def main():
    source = json.loads((MAP_DIR / "forest_demo_map.json").read_text(encoding="utf-8"))
    grid = source["grid"]
    width, height = grid["width"], grid["height"]
    materials = [["grass_deep" for _ in range(width)] for _ in range(height)]
    for layer in source["layers"]:
        material = layer["material"]
        for cell in layer["cells"]:
            materials[cell["y"]][cell["x"]] = material

    # Water is blocked. All other current ground materials are traversable.
    walkable = [[materials[y][x] != "water" for x in range(width)] for y in range(height)]
    collisions = []
    occluders = []
    for item in source["objects"]:
        if item["type"] != "tree":
            continue
        x, y = item["pixel_position"]
        w, h = item["display_size"]
        # A small footprint around the bottom of the trunk, not the whole canopy.
        footprint_w = max(16, min(30, round(w * 0.42)))
        footprint_h = max(12, min(20, round(h * 0.16)))
        left = round(x + (w - footprint_w) / 2)
        top = round(y + h - footprint_h)
        collisions.append({
            "id": item["id"],
            "kind": "tree_trunk",
            "shape": "rectangle",
            "x": left, "y": top,
            "width": footprint_w, "height": footprint_h,
            "blocks_movement": True
        })
        # Runtime renderers can fade this upper visual region while the player walks beneath it.
        canopy_h = max(1, h - footprint_h)
        occluders.append({
            "id": item["id"],
            "kind": "tree_canopy",
            "x": x, "y": y,
            "width": w, "height": canopy_h,
            "alpha_when_player_under": 0.58,
            "sort_anchor_x": round(x + w / 2),
            "sort_anchor_y": round(y + h)
        })

    navigation = {
        "format": "fantasy-rpg-navigation-v1",
        "grid": {"width": width, "height": height, "cell_size": CELL},
        "materials": materials,
        "walkable": walkable,
        "blocked_materials": ["water"],
        "collision_shapes": collisions,
        "canopy_occlusion": occluders,
        "rules": {
            "movement": "grid navigation; reject destination cells where walkable is false or a collision shape overlaps the player footprint",
            "tree_depth": "sort trees by bottom-center ground anchor; canopy occlusion is separate metadata and must not block movement",
            "bridge": "future bridge deck cells must be explicitly marked walkable even when visually spanning water"
        }
    }
    (MAP_DIR / "forest_demo_navigation.json").write_text(
        json.dumps(navigation, indent=2) + "\n", encoding="utf-8"
    )

    tiled_path = MAP_DIR / "forest_demo_map.tmj"
    tiled = json.loads(tiled_path.read_text(encoding="utf-8"))
    # Replace generated collision layer on repeat runs, preserving stable layer IDs.
    tiled["layers"] = [layer for layer in tiled["layers"] if layer.get("name") != "Tree Trunk Collisions"]
    objects = []
    for object_id, shape in enumerate(collisions, start=1):
        objects.append({
            "id": object_id,
            "name": shape["id"],
            "class": "tree_trunk_collision",
            "x": shape["x"], "y": shape["y"],
            "width": shape["width"], "height": shape["height"],
            "rotation": 0, "visible": True,
            "properties": [{"name": "blocks_movement", "type": "bool", "value": True}]
        })
    tiled["layers"].append({
        "id": max(layer["id"] for layer in tiled["layers"]) + 1,
        "name": "Tree Trunk Collisions",
        "type": "objectgroup",
        "draworder": "topdown",
        "opacity": 0.35,
        "visible": True,
        "objects": objects
    })
    tiled["nextlayerid"] = max(layer["id"] for layer in tiled["layers"]) + 1
    tiled.setdefault("properties", []).append({
        "name": "navigation_manifest", "type": "string",
        "value": "forest_demo_navigation.json"
    })
    tiled_path.write_text(json.dumps(tiled, indent=2) + "\n", encoding="utf-8")
    print(f"Exported navigation: {width}x{height}, {len(collisions)} trunk colliders, {len(occluders)} canopy regions")

if __name__ == "__main__":
    main()
