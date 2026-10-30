#!/usr/bin/env python3
"""Export the generated forest demo as an editable Tiled JSON map."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / "assets" / "maps" / "forest_demo"
GROUND_DIR = ROOT / "assets" / "tilesets" / "forest_ground"
TREE_DIR = ROOT / "assets" / "environment" / "forest" / "trees"
PLANT_DIR = ROOT / "assets" / "environment" / "forest" / "plants"

def main():
    source = json.loads((MAP_DIR / "forest_demo_map.json").read_text(encoding="utf-8"))
    grid = source["grid"]
    width, height = grid["width"], grid["height"]
    tile_w, tile_h = grid["tile_width"], grid["tile_height"]
    ground_png = ImageInfo.from_png(MAP_DIR / "forest_demo_ground.png")

    ground_tileset = {
        "type": "tileset",
        "version": "1.10",
        "tiledversion": "1.12.2",
        "name": "ForestDemoGround",
        "tilewidth": tile_w,
        "tileheight": tile_h,
        "tilecount": width * height,
        "columns": width,
        "image": "forest_demo_ground.png",
        "imagewidth": ground_png.width,
        "imageheight": ground_png.height,
        "margin": 0,
        "spacing": 0
    }
    (MAP_DIR / "forest_demo_ground.tsj").write_text(
        json.dumps(ground_tileset, indent=2) + "\n", encoding="utf-8"
    )

    tree_meta = json.loads((TREE_DIR / "trees.json").read_text(encoding="utf-8"))
    plant_meta = json.loads((PLANT_DIR / "plants.json").read_text(encoding="utf-8"))
    collection = []
    tile_ids = {}
    for category, base_dir, records in (
        ("tree", TREE_DIR, tree_meta["sprites"]),
        ("plant", PLANT_DIR, plant_meta["sprites"])
    ):
        for entry in records:
            tile_id = len(collection)
            tile_ids[(category, entry["id"])] = tile_id
            collection.append({
                "id": tile_id,
                "image": str(Path("..", "..", "environment", "forest",
                                  "trees" if category == "tree" else "plants",
                                  entry["file"])).replace("\\", "/"),
                "imagewidth": entry["size"][0],
                "imageheight": entry["size"][1],
                "type": category,
                "class": category
            })

    props_tileset = {
        "type": "tileset",
        "version": "1.10",
        "tiledversion": "1.12.2",
        "name": "ForestDemoProps",
        "tilewidth": tile_w,
        "tileheight": tile_h,
        "tilecount": len(collection),
        "columns": 0,
        "objectalignment": "bottom",
        "tiles": collection
    }
    (MAP_DIR / "forest_demo_props.tsj").write_text(
        json.dumps(props_tileset, indent=2) + "\n", encoding="utf-8"
    )

    ground_gids = list(range(1, width * height + 1))
    ground_layer = {
        "id": 1,
        "name": "Ground",
        "type": "tilelayer",
        "width": width,
        "height": height,
        "x": 0,
        "y": 0,
        "opacity": 1,
        "visible": True,
        "data": ground_gids
    }

    objects = []
    for object_id, obj in enumerate(
        sorted(source["objects"], key=lambda item: (item["sort_y"], item["cell"][0])),
        start=1
    ):
        category = obj["type"]
        tile_id = tile_ids[(category, obj["sprite_id"])]
        image_w, image_h = obj["display_size"]
        pixel_x, pixel_y = obj["pixel_position"]
        objects.append({
            "id": object_id,
            "name": obj["sprite_id"],
            "class": category,
            "type": category,
            "gid": width * height + 1 + tile_id,
            "x": pixel_x + image_w / 2,
            "y": pixel_y + image_h,
            "width": image_w,
            "height": image_h,
            "rotation": 0,
            "visible": True
        })

    object_layer = {
        "id": 2,
        "name": "Forest Props",
        "type": "objectgroup",
        "draworder": "topdown",
        "x": 0,
        "y": 0,
        "opacity": 1,
        "visible": True,
        "objects": objects
    }

    tiled_map = {
        "type": "map",
        "version": "1.10",
        "tiledversion": "1.12.2",
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "width": width,
        "height": height,
        "tilewidth": tile_w,
        "tileheight": tile_h,
        "infinite": False,
        "nextlayerid": 3,
        "nextobjectid": len(objects) + 1,
        "backgroundcolor": "#22362a",
        "layers": [ground_layer, object_layer],
        "tilesets": [
            {"firstgid": 1, "source": "forest_demo_ground.tsj"},
            {"firstgid": width * height + 1, "source": "forest_demo_props.tsj"}
        ],
        "properties": [
            {"name": "projection", "type": "string", "value": "diagonal 3/4"},
            {"name": "source_manifest", "type": "string", "value": "forest_demo_map.json"},
            {"name": "ground_note", "type": "string",
             "value": "Each rendered ground cell is a unique image-atlas tile for easy cell-level editing."}
        ]
    }
    (MAP_DIR / "forest_demo_map.tmj").write_text(
        json.dumps(tiled_map, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Exported Tiled map: {width}x{height}, {len(objects)} prop objects, "
          f"{len(collection)} image-collection sprites")

class ImageInfo:
    def __init__(self, width, height):
        self.width, self.height = width, height

    @staticmethod
    def from_png(path):
        from PIL import Image
        with Image.open(path) as image:
            return ImageInfo(*image.size)

if __name__ == "__main__":
    main()
