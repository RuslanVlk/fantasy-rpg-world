#!/usr/bin/env python3
"""Decode and validate the CC0 Kenney Roguelike/RPG spritesheet source."""
from pathlib import Path
import base64
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source" / "kenney_roguelike" / "roguelikeSheet_transparent.png.b64"
OUT = ROOT / "assets" / "third_party" / "kenney_roguelike"
EXPECTED_SIZE = (968, 526)
TILE = 16
SPACING = 1
COLUMNS = 57
ROWS = 31
UPSTREAM_BLOB_SHA = "32e606ca0596611d977d7ab5b29d6f2b23cfe212"

def main():
    target = OUT / "roguelikeSheet_transparent.png"
    manifest_path = OUT / "manifest.json"

    # The workflow removes the temporary base64 bootstrap file after the
    # first successful import. Later rebuilds validate and reuse the committed
    # CC0 source atlas instead of requiring the bootstrap payload again.
    if not SOURCE.exists():
        if not target.exists() or not manifest_path.exists():
            raise FileNotFoundError("Neither temporary base64 source nor imported Kenney atlas exists.")
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing_image = Image.open(target).convert("RGBA")
        if existing_image.size != EXPECTED_SIZE or existing.get("license") != "CC0-1.0":
            raise ValueError("Existing Kenney source atlas failed provenance or dimension checks.")
        preview_path = OUT / "roguelikeSheet_preview_3x.png"
        if not preview_path.exists():
            existing_image.resize((existing_image.width * 3, existing_image.height * 3),
                                  Image.Resampling.NEAREST).save(preview_path, optimize=True)
        print("Validated and reused committed Kenney CC0 source atlas.")
        return

    encoded = "".join(SOURCE.read_text(encoding="ascii").split())
    raw = base64.b64decode(encoded, validate=True)
    image = Image.open(__import__("io").BytesIO(raw)).convert("RGBA")
    if image.size != EXPECTED_SIZE:
        raise ValueError(f"Unexpected source sheet size {image.size}; expected {EXPECTED_SIZE}")

    OUT.mkdir(parents=True, exist_ok=True)
    image.save(target, optimize=True)

    preview = image.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST)
    preview.save(OUT / "roguelikeSheet_preview_3x.png", optimize=True)

    occupied = []
    for row in range(ROWS):
        for col in range(COLUMNS):
            x = col * (TILE + SPACING)
            y = row * (TILE + SPACING)
            crop = image.crop((x, y, x + TILE, y + TILE))
            if crop.getchannel("A").getbbox():
                occupied.append({"index": row * COLUMNS + col, "column": col, "row": row,
                                 "x": x, "y": y})

    manifest = {
        "asset": "Kenney Roguelike/RPG pack",
        "author": "Kenney",
        "official_source": "https://kenney.nl/assets/roguelike-rpg-pack",
        "download_source": "https://kenney.nl/media/pages/assets/roguelike-rpg-pack/12c03cd78b-1677697420/kenney_roguelike-rpg-pack.zip",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "perspective": "3/4 RPG",
        "tile_size": TILE,
        "spacing": SPACING,
        "columns": COLUMNS,
        "rows": ROWS,
        "source_dimensions": list(EXPECTED_SIZE),
        "source_repository_mirror": "https://github.com/cosmic-canopy-studio/rimpocalypse",
        "source_path": "assets/sprite_sheets/roguelikeSheet_transparent.png",
        "source_git_blob_sha": UPSTREAM_BLOB_SHA,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "occupied_cells": occupied,
        "notes": [
            "Original source atlas retained unchanged apart from PNG optimization.",
            "Do not assume every cell belongs in the final forest biome; select after visual review.",
            "This pack is a visual base/reference library, not a replacement for the project's supplied art direction."
        ]
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "CREDITS.md").write_text(
        "# Kenney Roguelike/RPG pack\n\n"
        "Author: Kenney. Official asset page: https://kenney.nl/assets/roguelike-rpg-pack\n"
        "License: CC0-1.0 (public domain dedication): https://creativecommons.org/publicdomain/zero/1.0/\n"
        "The official page identifies the pack as 16×16 2D assets under Creative Commons CC0.\n\n"
        "The source sheet is stored as an unchanged atlas. Source file mirror: "
        "https://github.com/cosmic-canopy-studio/rimpocalypse/blob/main/assets/sprite_sheets/roguelikeSheet_transparent.png\n"
        "Original sheet blob SHA: " + UPSTREAM_BLOB_SHA + "\n",
        encoding="utf-8"
    )

    SOURCE.unlink()
    print(f"Imported Kenney CC0 sheet: {image.width}x{image.height}, "
          f"{len(occupied)} occupied 16x16 cells -> {OUT}")

if __name__ == "__main__":
    main()
