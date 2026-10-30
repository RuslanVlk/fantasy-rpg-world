#!/usr/bin/env python3
"""Generate seamless, editable 64px forest ground tiles and an atlas.

Textures are deterministic and tileable: the noise field wraps on both axes,
so adjacent copies do not create hard seams. This is a prototype material
library; hand-authored transition masks and reference matching are later steps.
"""
from pathlib import Path
import math
import random
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "tilesets" / "forest_ground"
S = 64
SEED = 20261030

# Dark base, midtone, light, highlight. Shared lighting: upper-left.
MATERIALS = {
    "grass_deep": ((34, 65, 43), (52, 91, 53), (75, 112, 62), (101, 132, 72)),
    "grass_light": ((48, 79, 43), (69, 106, 53), (96, 130, 66), (125, 149, 82)),
    "dirt": ((69, 48, 34), (96, 66, 43), (122, 88, 57), (147, 111, 73)),
    "forest_path": ((78, 57, 39), (105, 77, 51), (133, 101, 67), (157, 125, 86)),
    "stone": ((63, 68, 66), (88, 94, 88), (116, 119, 107), (145, 144, 126)),
    "sand": ((124, 105, 68), (154, 133, 85), (181, 158, 104), (204, 181, 126)),
    "water": ((24, 59, 77), (31, 82, 99), (43, 108, 119), (70, 135, 137)),
    "mud": ((56, 57, 42), (79, 76, 51), (105, 97, 62), (130, 117, 77)),
}

def wrapped_noise(x, y, period, phase):
    # Periodic harmonics ensure values and derivatives meet at tile boundaries.
    a = math.sin(2*math.pi*x/period + phase)
    b = math.cos(2*math.pi*y/period + phase*1.7)
    c = math.sin(2*math.pi*(x+y)/(period*1.5) + phase*.7)
    return (a*.36 + b*.34 + c*.30)

def make_material(name, palette, seed):
    rng = random.Random(seed)
    im = Image.new("RGBA", (S, S))
    pix = im.load()
    base, mid, light, high = palette
    for y in range(S):
        for x in range(S):
            n = (wrapped_noise(x, y, 31, seed*.013) +
                 .45*wrapped_noise(x, y, 13, seed*.021))
            t = max(0.0, min(1.0, .48 + n*.34))
            if t < .5:
                q=t*2
                c=tuple(round(base[k]*(1-q)+mid[k]*q) for k in range(3))
            else:
                q=(t-.5)*2
                c=tuple(round(mid[k]*(1-q)+light[k]*q) for k in range(3))
            pix[x,y]=(*c,255)

    d=ImageDraw.Draw(im)
    # Discrete clustered pixel details; coordinates wrap to preserve tiling.
    for _ in range(110):
        x,y=rng.randrange(S),rng.randrange(S)
        c=rng.choices([base,mid,light,high],[2,5,3,1])[0]
        w=rng.choice([1,2,2,3])
        h=rng.choice([1,1,2])
        for yy in range(h):
            for xx in range(w):
                im.putpixel(((x+xx)%S,(y+yy)%S),(*c,255))

    if name.startswith("grass"):
        for _ in range(22):
            x,y=rng.randrange(S),rng.randrange(S)
            c=(*rng.choice([light,high]),255)
            d.point((x,y),fill=c)
            d.point(((x+1)%S,(y-1)%S),fill=c)
            d.point(((x+2)%S,y),fill=c)
    elif name=="water":
        for _ in range(20):
            x,y=rng.randrange(S),rng.randrange(S)
            length=rng.randrange(3,8)
            c=(*high,220)
            for i in range(length):
                im.putpixel(((x+i)%S,y),c)
    elif name=="stone":
        for _ in range(13):
            x,y=rng.randrange(S),rng.randrange(S)
            im.putpixel((x,y),(*high,255))
            im.putpixel(((x+1)%S,y),(*light,255))
    return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    names=list(MATERIALS)
    tiles=[]
    for i,(name,palette) in enumerate(MATERIALS.items()):
        tile=make_material(name,palette,SEED+i*101)
        tile.save(OUT/f"{name}.png",optimize=True)
        tiles.append(tile)
    cols=4
    rows=(len(tiles)+cols-1)//cols
    atlas=Image.new("RGBA",(cols*S,rows*S),(0,0,0,0))
    for i,tile in enumerate(tiles):
        atlas.alpha_composite(tile,((i%cols)*S,(i//cols)*S))
    atlas.save(OUT/"forest_ground_atlas.png",optimize=True)
    import json
    metadata={
        "tile_width":S,"tile_height":S,"atlas_columns":cols,
        "atlas_rows":rows,"projection":"diagonal 3/4",
        "materials":[{"id":i,"name":n,"file":f"{n}.png"} for i,n in enumerate(names)],
        "note":"Seamless prototype textures; not final hand-painted production art."
    }
    (OUT/"tileset.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(f"OK: {len(tiles)} seamless tiles + atlas -> {OUT}")

if __name__=="__main__":
    main()
