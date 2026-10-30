#!/usr/bin/env python3
"""Shared 8-neighbour mask selection for the forest blob-autotile prototype."""
from collections.abc import Mapping

CARDINALS = {"N": 1, "E": 2, "S": 4, "W": 8}
DIAGONALS = {"NE": 16, "SE": 32, "SW": 64, "NW": 128}
ALL_BITS = {**CARDINALS, **DIAGONALS}

def neighbor_mask(grid: Mapping[tuple[int, int], str], x: int, y: int, terrain: str) -> int:
    """Return the valid 47-layout mask for neighbours matching terrain."""
    active = {
        "N": grid.get((x, y - 1)) == terrain,
        "E": grid.get((x + 1, y)) == terrain,
        "S": grid.get((x, y + 1)) == terrain,
        "W": grid.get((x - 1, y)) == terrain,
    }
    value = sum(CARDINALS[name] for name, enabled in active.items() if enabled)
    corners = (
        ("NE", "N", "E"),
        ("SE", "E", "S"),
        ("SW", "S", "W"),
        ("NW", "W", "N"),
    )
    for diagonal, first, second in corners:
        if active[first] and active[second] and grid.get((
            x + (1 if "E" in diagonal else -1 if "W" in diagonal else 0),
            y + (1 if "S" in diagonal else -1 if "N" in diagonal else 0)
        )) == terrain:
            value |= DIAGONALS[diagonal]
    return value

def mask_filename(value: int) -> str:
    if not 0 <= value <= 255:
        raise ValueError(f"Mask value must be between 0 and 255, got {value}")
    return f"mask_{value:03d}.png"
