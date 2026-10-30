#!/usr/bin/env python3
"""Extract hand-selected Kenney forest tree variants as independent PNG sprites."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "third_party" / "kenney_roguelike" / "roguelikeSheet_transparent.png"
OUT = ROOT / "assets" / "environment" / "forest" / "trees"
TILE = 16
STRIDE = 17
TREE_COLUMNS = range(13, 19)
SMALL_ROW = 9
TALL_TOP_ROW = 10
TALL_BOTTOM_ROW = 11

def cell(sheet, column, row):
    x = column * STRIDE
    y = row * STRIDE
    return sheet.crop((x, y, x + TILE, y + TILE))

def main():
    sheet = Image.open(SOURCE).convert("RGBA")
    if sheet.size != (968, 526):
        raise ValueError(f"Unexpected source sheet size: {sheet.size}")

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []
    sprites = []

    for variant, column in enumerate(TREE_COLUMNS, start=1):
        small = cell(sheet, column, SMALL_ROW)
        if small.getchannel("A").getbbox() is None:
            raise ValueError(f"Empty small tree source at row {SMALL_ROW}, column {column}")
        small_name = f"tree_small_{variant:02d}.png"
        small.save(OUT / small_name, optimize=True)
        sprites.append((small_name, small))
        entries.append({
            "id": small_name[:-4],
            "file": small_name,
            "size": [16, 16],
            "source_cells": [{"row": SMALL_ROW, "column": column}],
            "source_description": "single-cell tree with canopy and trunk"
        })

        top = cell(sheet, column, TALL_TOP_ROW)
        bottom = cell(sheet, column, TALL_BOTTOM_ROW)
        tall = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
        tall.alpha_composite(top, (0, 0))
        tall.alpha_composite(bottom, (0, 16))
        if tall.getchannel("A").getbbox() is None:
            raise ValueError(f"Empty tall tree source at column {column}")
        tall_name = f"tree_tall_{variant:02d}.png"
        tall.save(OUT / tall_name, optimize=True)
        sprites.append((tall_name, tall))
        entries.append({
            "id": tall_name[:-4],
            "file": tall_name,
            "size": [16, 32],
            "source_cells": [
                {"row": TALL_TOP_ROW, "column": column},
                {"row": TALL_BOTTOM_ROW, "column": column}
            ],
            "source_description": "two-cell vertically assembled tree"
        })

    columns = 6
    cell_w, cell_h = 64, 80
    contact = Image.new("RGBA", (columns * cell_w, 2 * cell_h), (37, 43, 39, 255))
    draw = ImageDraw.Draw(contact)
    for name, sprite in sprites:
        row = 0 if "small" in name else 1
        col = int(name[-6:-4]) - 1
        preview = sprite.resize((sprite.width * 3, sprite.height * 3), Image.Resampling.NEAREST)
        x = col * cell_w + (cell_w - preview.width) // 2
        y = row * cell_h + 18 + (52 - preview.height) // 2
        contact.alpha_composite(preview, (x, y))
        draw.text((col * cell_w + 4, row * cell_h + 3), name.replace(".png", ""), fill=(235, 235, 225, 255))
    contact.save(OUT / "trees_contact_sheet.png", optimize=True)

    manifest = {
        "asset_pack": "Kenney Roguelike/RPG pack",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source_atlas": "assets/third_party/kenney_roguelike/roguelikeSheet_transparent.png",
        "source_atlas_grid": {"tile_size": 16, "spacing": 1, "columns": 57, "rows": 31},
        "view": "3/4 RPG",
        "count": len(entries),
        "sprites": entries,
        "note": "Native-resolution transparent sprites extracted from CC0 source cells. Contact sheet is for preview; use the individual PNG files in maps."
    }
    (OUT / "trees.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Forest tree sprites\n\n"
        "Twelve separate transparent PNG tree sprites extracted from the Kenney Roguelike/RPG CC0 atlas: "
        "six 16x16 small trees and six 16x32 two-cell tall trees.\n\n"
        "Source and license are recorded in trees.json. Original source atlas is preserved under "
        "assets/third_party/kenney_roguelike/.\n\n"
        "trees_contact_sheet.png is a review preview only. Import the individual PNG sprites for map placement.\n",
        encoding="utf-8"
    )
    print(f"Extracted {len(entries)} separate forest tree sprites from six source variants.")

if __name__ == "__main__":
    main()
