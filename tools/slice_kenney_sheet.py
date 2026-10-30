#!/usr/bin/env python3
"""Split every occupied 16x16 tile from Kenney's CC0 3/4 RPG atlas."""
from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "third_party" / "kenney_roguelike" / "roguelikeSheet_transparent.png"
SOURCE_MANIFEST = ROOT / "assets" / "third_party" / "kenney_roguelike" / "manifest.json"
OUT = ROOT / "assets" / "third_party" / "kenney_roguelike" / "tile_cells"
TILE = 16

def main():
    sheet = Image.open(SOURCE).convert("RGBA")
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if sheet.size != (968, 526):
        raise ValueError(f"Unexpected Kenney atlas dimensions: {sheet.size}")

    OUT.mkdir(parents=True, exist_ok=True)
    catalog = []
    for cell in manifest["occupied_cells"]:
        index, col, row = cell["index"], cell["column"], cell["row"]
        x, y = cell["x"], cell["y"]
        sprite = sheet.crop((x, y, x + TILE, y + TILE))
        bounds = sprite.getchannel("A").getbbox()
        if bounds is None:
            continue
        filename = f"tile_{index:04d}_r{row:02d}_c{col:02d}.png"
        sprite.save(OUT / filename, optimize=True)
        catalog.append({
            "id": index,
            "row": row,
            "column": col,
            "source_x": x,
            "source_y": y,
            "file": f"tile_cells/{filename}",
            "alpha_bounds": list(bounds)
        })

    result = {
        "source": "roguelikeSheet_transparent.png",
        "source_manifest": "manifest.json",
        "license": "CC0-1.0",
        "tile_width": TILE,
        "tile_height": TILE,
        "source_spacing": 1,
        "columns": manifest["columns"],
        "rows": manifest["rows"],
        "count": len(catalog),
        "note": "Cells are cut at the source atlas grid. Multi-cell composite objects remain assembled from neighboring cells in the original atlas.",
        "tiles": catalog
    }
    (ROOT / "assets" / "third_party" / "kenney_roguelike" / "tile_catalog.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Split {len(catalog)} non-empty 16x16 cells into independent transparent PNGs.")

if __name__ == "__main__":
    main()
