# Forest ground tiles — first generated pack

Run:

```bash
python -m pip install -r requirements-assets.txt
python tools/generate_forest_tiles.py
```

The generator exports eight independent 64×64 RGBA PNG ground tiles and a 4×2 atlas:
grass_deep, grass_light, dirt, forest_path, stone, sand, water, mud.

GitHub Actions workflow **Generate forest terrain assets** runs the generator and
publishes the PNGs as a downloadable workflow artifact. These are a first
functional prototype pack, not final approved art: edge transitions, autotile
rules, and visual review against the supplied reference remain required.
