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
            move_x = doubled > -dy
            move_y = doubled < dx
            old_x, old_y = x, y
            if move_x:
                error -= dy
                x += sx
            if move_y:
                error += dx
                y += sy
            # Insert an orthogonal bridge whenever the line would jump diagonally.
            if x != old_x and y != old_y:
                result.add((x, old_y))
    return result

