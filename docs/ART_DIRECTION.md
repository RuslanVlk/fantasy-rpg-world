# Art Direction

## Target look

Use the user's approved forest reference as the primary visual authority. The target is detailed 2D pixel art viewed from a diagonal 3/4 angle, close to an isometric presentation but with the exact projection and proportions of the reference.

The result should feel like a coherent hand-crafted game world, not a collection of unrelated asset packs.

## Perspective and readability

- Keep a consistent diagonal 3/4 view across terrain, buildings, props, and characters.
- Show enough top surfaces to communicate depth while keeping vertical faces readable.
- Keep object footprints and collision-friendly silhouettes clear.
- Do not mix top-down, side-view, and true-isometric assets.

## Pixel-art treatment

- Use deliberate pixel clusters and clean, controlled edges.
- Maintain consistent pixel density and a restrained outline approach.
- Use material-specific texture: foliage, bark, water, stone, soil, sand, and timber must read differently.
- Use controlled highlights and shadows; avoid random noise, excessive dithering, blur, and anti-aliased edges.
- Preserve silhouette quality at normal gameplay zoom.

## Environment and palette

The first region is a lush forest environment. It includes water, shoreline, grass, soil, sand, stone, timber, moss, and ruins. Transitions between materials must look natural and should be supported by edge and corner variants.

Use a cohesive palette with clear value separation. Water should have readable flow and depth; waterfalls should connect naturally to the water below. Vegetation should vary in silhouette, height, density, and hue.

## Asset quality rules

- No primitive geometric stand-ins in deliverables.
- No obvious repeated copies of the same tree, rock, bush, or decoration.
- Provide meaningful variants and rotations only where they remain visually plausible.
- Do not merge an entire scene into one image.
- Keep source assets at native resolution with transparent backgrounds where appropriate.
- Keep spritesheet frames aligned and documented.
- Do not invent missing character details when a character reference is supplied; preserve the approved design.

## Review checklist

Before accepting an asset:
- Does its perspective match the reference?
- Does its scale match neighboring assets?
- Is its silhouette clean and readable?
- Does its palette and lighting belong to the same world?
- Are transparent pixels clean, without halos or stray artifacts?
- Can it be placed next to other assets without visible seams?
- Does it avoid obvious duplication?
