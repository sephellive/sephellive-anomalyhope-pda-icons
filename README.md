# AnomalyHope PDA Icons

An original, tactical-style replacement set for S.T.A.L.K.E.R. Anomaly 1.5.3 PDA map markers. The base-game marker inventory is complete; the runtime patch, asset build, and in-game validation remain in progress.

## Requirements

- S.T.A.L.K.E.R. Anomaly 1.5.3
- [Anomaly Modded Exes](https://github.com/themrdemonized/xray-monolith) with DXML support
- Python 3.11+ for inventory and build tools
- Git LFS for generated DDS assets

## Status

No release is available yet. This branch is research and implementation work, not a finished or tested game add-on. Do not install it into an active game profile until the release checks are complete. The intended distribution is a separate Mod Organizer 2 mod containing only runtime files under `gamedata/`.

## Inventory

`assets/manifest/icons.json` records the standard and widescreen marker definitions, their bindings, original texture references, atlas regions, dimensions, state attributes, implementation status, and in-game verification status. Rebuild and validate it from a locally installed game:

```powershell
./tools/extract_anomaly_resources.ps1 -GamePath 'D:\Hope\Anomaly' -OutputPath "$env:TEMP\AnomalyHope-icons"
python ./tools/inventory_icons.py --config-root "$env:TEMP\AnomalyHope-icons\configs\configs" --textures-root "$env:TEMP\AnomalyHope-icons\textures" --output ./assets/manifest/icons.json
python ./tools/validate_icon_inventory.py --manifest ./assets/manifest/icons.json --textures-root "$env:TEMP\AnomalyHope-icons\textures"
```

The validator supports a manifest-only mode for CI and checks local source DDS files and atlas bounds when given `--textures-root`. Original game assets are not redistributed.

## Glyph build

The original SVG glyphs are in `assets/sources/icons/`. Build the standalone DDS files and generated DXML map with DirectXTex:

```powershell
python -m pip install -r requirements.txt
python ./tools/build_icons.py --texconv 'C:\Tools\texconv.exe'
python ./tools/validate_icon_build.py
```

The current 20-glyph family is mapped across 249 technical IDs by semantic naming rules. Five non-icon entries are explicit exclusions: `no_spot` (visibility sentinel), `debug_stalker_spot` (debug marker), and the three map-frame border elements. The generated patch retains marker dimensions, color/tint attributes, animation attributes, and texture-layer structure while removing atlas coordinates from replaced texture nodes. This is an initial implementation pass; confirm texture lookup, rendered appearance, marker layering, animations, and third-party behavior in Anomaly before describing it as a release.

See [`docs/research.md`](docs/research.md) for source locations, confirmed behavior, and unresolved compatibility items.

## Architecture

Map marker definitions are XML, so the intended targeted runtime patch uses DXML from Anomaly Modded Exes; DLTX does not apply to those files. Original textures will be replaced by separate generated resources rather than modifying the game's atlas files. Compatibility with third-party marker IDs and the final animation behavior still requires testing.

## License and assets

The repository license applies only to original project material. It does not grant rights to S.T.A.L.K.E.R. Anomaly assets. Generated map and icon files derived from game assets must be built locally from a legally installed game and are not included in public releases without redistribution permission.
