#!/usr/bin/env python3
"""Extract small forest flowers and ground-cover sprites from the CC0 atlas."""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "third_party" / "kenney_roguelike" / "roguelikeSheet_transparent.png"
OUT = ROOT / "assets" / "environment" / "forest" / "plants"
TILE = 16
STRIDE = 17

# Coordinates are source atlas cells, independently checked in the sheet preview.
PLANTS = [
    ("flower_blue_01", 28, 9, "small blue flower tuft"),
    ("flower_orange_01", 29, 9, "small orange flower tuft"),
    ("flower_purple_01", 30, 9, "small purple flower tuft"),
    ("flower_white_01", 25, 11, "small white flower cluster"),
    ("ground_cover_01", 26, 11, "small leafy ground-cover clump"),
    ("ground_cover_02", 28, 11, "small leafy ground-cover clump"),
]

def main():
    sheet = Image.open(SOURCE).convert("RGBA")
    if sheet.size != (968, 526):
        raise ValueError(f"Unexpected source sheet size: {sheet.size}")
    OUT.mkdir(parents=True, exist_ok=True)

    entries = []
    previews = []
    for name, column, row, description in PLANTS:
        x, y = column * STRIDE, row * STRIDE
        sprite = sheet.crop((x, y, x + TILE, y + TILE))
        if sprite.getchannel("A").getbbox() is None:
            raise ValueError(f"Empty forest plant cell: {name}")
        sprite.save(OUT / f"{name}.png", optimize=True)
        entries.append({
            "id": name,
            "file": f"{name}.png",
            "size": [16, 16],
            "source_cells": [{"row": row, "column": column}],
            "source_description": description
        })
        previews.append((name, sprite))

    cell_w, cell_h = 80, 80
    contact = Image.new("RGBA", (3 * cell_w, 2 * cell_h), (37, 43, 39, 255))
    draw = ImageDraw.Draw(contact)
    for index, (name, sprite) in enumerate(previews):
        col, row = index % 3, index // 3
        enlarged = sprite.resize((48, 48), Image.Resampling.NEAREST)
        x = col * cell_w + (cell_w - 48) // 2
        y = row * cell_h + 20
        contact.alpha_composite(enlarged, (x, y))
        draw.text((col * cell_w + 3, row * cell_h + 3), name, fill=(235, 235, 225, 255))
    contact.save(OUT / "plants_contact_sheet.png", optimize=True)

    manifest = {
        "asset_pack": "Kenney Roguelike/RPG pack",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "source_atlas": "assets/third_party/kenney_roguelike/roguelikeSheet_transparent.png",
        "tile_size": 16,
        "count": len(entries),
        "sprites": entries,
        "note": "Separate native-resolution transparent PNGs; contact sheet is a preview."
    }
    (OUT / "plants.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Forest plants and ground cover\n\n"
        "Six separate transparent PNG sprites extracted from the Kenney Roguelike/RPG CC0 atlas: "
        "four flower variants and two ground-cover clumps.\n\n"
        "Source cells and license are recorded in plants.json. Use the individual PNGs for map placement.\n",
        encoding="utf-8"
    )
    print(f"Extracted {len(entries)} individual flower and ground-cover sprites.")

if __name__ == "__main__":
    main()
