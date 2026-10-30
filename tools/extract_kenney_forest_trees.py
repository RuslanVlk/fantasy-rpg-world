#!/usr/bin/env python3
"""Extract selected Kenney forest tree sprites as independent PNGs."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "third_party" / "kenney_roguelike" / "roguelikeSheet_transparent.png"
OUT = ROOT / "assets" / "environment" / "forest" / "trees"
TILE = 16
STRIDE = 17
TREE_COLUMNS = range(13, 19)

def cell(sheet, column, row):
    x, y = column * STRIDE, row * STRIDE
    return sheet.crop((x, y, x + TILE, y + TILE))

def compose_vertical(sheet, column, rows):
    result = Image.new("RGBA", (TILE, TILE * len(rows)), (0, 0, 0, 0))
    for offset, row in enumerate(rows):
        result.alpha_composite(cell(sheet, column, row), (0, offset * TILE))
    return result

def add_sprite(entries, previews, name, sprite, source_cells, description):
    if sprite.getchannel("A").getbbox() is None:
        raise ValueError(f"Empty tree sprite {name}")
    sprite.save(OUT / f"{name}.png", optimize=True)
    entries.append({
        "id": name,
        "file": f"{name}.png",
        "size": list(sprite.size),
        "source_cells": source_cells,
        "source_description": description
    })
    previews.append((name, sprite))

def main():
    sheet = Image.open(SOURCE).convert("RGBA")
    if sheet.size != (968, 526):
        raise ValueError(f"Unexpected source sheet size: {sheet.size}")
    OUT.mkdir(parents=True, exist_ok=True)
    entries, previews = [], []

    for variant, column in enumerate(TREE_COLUMNS, start=1):
        small = cell(sheet, column, 9)
        add_sprite(entries, previews, f"tree_small_{variant:02d}", small,
                   [{"row": 9, "column": column}],
                   "single-cell tree with canopy and trunk")

        tall = compose_vertical(sheet, column, (10, 11))
        add_sprite(entries, previews, f"tree_tall_{variant:02d}", tall,
                   [{"row": 10, "column": column}, {"row": 11, "column": column}],
                   "two-cell vertically assembled tree")

    for variant, column in enumerate((23, 24), start=1):
        fruit_tree = compose_vertical(sheet, column, (10, 11))
        add_sprite(entries, previews, f"tree_fruit_{variant:02d}", fruit_tree,
                   [{"row": 10, "column": column}, {"row": 11, "column": column}],
                   "two-cell fruit-bearing tree")

    dead_tree = compose_vertical(sheet, 27, (9, 10, 11))
    add_sprite(entries, previews, "tree_dead_01", dead_tree,
               [{"row": 9, "column": 27}, {"row": 10, "column": 27}, {"row": 11, "column": 27}],
               "three-cell bare tree trunk and branches")

    columns, cell_w, cell_h = 6, 48, 112
    contact = Image.new("RGBA", (columns * cell_w, 4 * cell_h), (37, 43, 39, 255))
    draw = ImageDraw.Draw(contact)
    for name, sprite in previews:
        if "small" in name:
            row, col = 0, int(name[-2:]) - 1
        elif "tall" in name:
            row, col = 1, int(name[-2:]) - 1
        elif "fruit" in name:
            row, col = 2, int(name[-2:]) - 1
        else:
            row, col = 3, 0
        preview = sprite.resize((sprite.width * 2, sprite.height * 2), Image.Resampling.NEAREST)
        x = col * cell_w + (cell_w - preview.width) // 2
        y = row * cell_h + 14 + (90 - preview.height) // 2
        contact.alpha_composite(preview, (x, y))
        draw.text((col * cell_w + 2, row * cell_h + 2), name, fill=(235, 235, 225, 255))
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
        "note": "Native-resolution transparent sprites extracted from CC0 source cells. Contact sheet is a preview; use individual PNG files in maps."
    }
    (OUT / "trees.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Forest tree sprites\n\n"
        "Fifteen separate transparent PNGs from the Kenney Roguelike/RPG CC0 atlas: "
        "six small 16x16 trees, six tall 16x32 trees, two fruit trees and one 16x48 dead tree.\n\n"
        "Source cells and license are recorded in trees.json. The original atlas is preserved under "
        "assets/third_party/kenney_roguelike/.\n\n"
        "trees_contact_sheet.png is a review preview only. Import the individual PNG sprites for map placement.\n",
        encoding="utf-8"
    )
    print(f"Extracted {len(entries)} separate tree sprites from nine leafy variants plus a dead tree.")

if __name__ == "__main__":
    main()
