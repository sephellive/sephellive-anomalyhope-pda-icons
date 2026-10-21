# AnomalyHope PDA Icons

A conservative 2× HD restoration of the S.T.A.L.K.E.R. Anomaly 1.5.3 PDA marker system. It keeps the original icon silhouettes, proportions, colors, layers, animation attributes, faction emblems, and configured screen sizes. The visual change is limited to cleaner edges and restrained detail recovery after DXT compression.

## Why the release is a local builder

The marker atlases are Anomaly game assets. This repository and its GitHub releases contain the reproducible builder, inventory, validators, and DXML generator. They do not redistribute the original or derived game atlases. The builder reads them from your installed copy and creates an independent MO2-ready add-on.

## Requirements

- S.T.A.L.K.E.R. Anomaly 1.5.3
- [Anomaly Modded Exes](https://github.com/themrdemonized/xray-monolith) with DXML support
- Python 3.11+ and Pillow
- DirectXTex `texconv.exe` available in `PATH`, or passed explicitly

## Build the MO2 add-on

From a release or repository checkout:

```powershell
python -m pip install -r requirements.txt
./tools/build_local.ps1 `
  -GamePath 'D:\Hope\Anomaly' `
  -OutputPath 'D:\Hope\mo2\mods\AnomalyHope PDA Icons' `
  -ArchivePath 'D:\Hope\AnomalyHope-PDA-Icons-v0.1.0.zip'
```

If `texconv.exe` is not in `PATH`, add `-TexconvPath 'C:\path\to\texconv.exe'`. The builder never writes into the Anomaly installation. Enable the output directory as a separate mod in MO2 and keep it below Anomaly Modded Exes.

## Technical coverage

`assets/manifest/icons.json` inventories 472 definitions, 254 technical IDs, 514 texture-layer occurrences, and five original atlas families from the standard, widescreen, multiplayer, relation, and complex marker XML files.

The generated DXML patch has 94 unambiguous layer rules. Each rule changes only the texture path and doubles its source atlas rectangle; marker dimensions, tints, nested borders, blink/light animations, location levels, heading behavior, and layer order stay intact. The undefined base-game symbol `ui_alife_combat` is deliberately left unchanged.

Run the checks directly with:

```powershell
python ./tools/validate_icon_inventory.py
python ./tools/validate_icon_build.py
python ./tools/validate_icon_build.py --output-root 'D:\Hope\mo2\mods\AnomalyHope PDA Icons'
```

See [`docs/research.md`](docs/research.md) for the resource analysis and known limits.

## License

The repository license covers original project code and documentation only. It does not grant rights to S.T.A.L.K.E.R. Anomaly assets. Locally generated DDS files must not be redistributed without permission from the relevant rights holders.
