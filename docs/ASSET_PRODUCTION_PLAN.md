# Asset Production Plan

## Phase 1 — Foundation

1. Confirm the reference image and define a measurable pixel scale.
2. Establish palette swatches, outline rules, lighting direction, and tile dimensions.
3. Choose the map grid and document how diagonal 3/4 perspective aligns with the grid.
4. Create a small quality-controlled test set before expanding production.

## Phase 2 — Terrain tilesets

Build modular terrain groups with all required edge and corner transitions:
- Grass and forest floor.
- Soil and dirt paths.
- Sand and shoreline.
- Shallow and deep water.
- Stone and rocky ground.
- Mossy stone and ruin flooring.

Each terrain group should include center tiles, edges, corners, inner corners, transition pieces, and useful variants. Autotile rules must be documented and tested.

## Phase 3 — Nature assets

Create independent transparent assets with varied silhouettes:
- Trees in multiple species and sizes.
- Bushes, ferns, flowers, roots, and ground cover.
- Rocks, boulders, and moss formations.
- Logs, stumps, mushrooms, and small forest details.

Avoid visible copy-paste repetition. Variants must be genuinely distinct, not simple hue swaps.

## Phase 4 — Water and landmarks

- River and lake sections with modular banks.
- Waterfall tops, falling-water segments, and splash pools.
- Bridges and crossing pieces.
- Cave entrance.
- Small house.
- Ruins and shrine.

Landmarks should be assembled from separate components where possible.

## Phase 5 — Characters and props

- Player character and NPCs as separate sprites.
- Directional movement and idle animation sets as required by the game.
- Independent props such as signs, crates, lanterns, fences, containers, and interactable objects.

Character reference designs take priority over new interpretation.

## Phase 6 — Map assembly and validation

Assemble the forest region from tiles and independent objects. Validate:
- No terrain seams or broken autotile transitions.
- Consistent object scale and perspective.
- Readable navigation and landmarks.
- Clear foreground/background layering.
- Stable performance and manageable texture sizes.
- Every source asset remains independently editable.

## Delivery conventions

- Keep source files and exports.
- Use transparent PNG for standalone sprites.
- Document tile size, canvas size, pivot/origin, animation frame size, and intended layer.
- Include a short README in each substantial asset folder.
- Track third-party provenance and license before integrating external assets.
