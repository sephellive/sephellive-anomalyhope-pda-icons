# AnomalyHope PDA Icons

A modern, compact marker system for the S.T.A.L.K.E.R. Anomaly 1.5.3 PDA. It replaces the oversized cyan-heavy presentation with original minimalist artwork and an information-first palette.

## Visual system

- warm ivory: transitions, neutral navigation, player and user markers;
- amber: primary and secondary objectives, stashes, artifacts and supplies;
- rust red: combat, mines, hostile activity and anomalies;
- muted sage: allies and services;
- steel gray: factions, bases, squads and strategic resources.

Transition markers use a compact chevron badge instead of the old cyan house outline. Their runtime size is 5×5, zoom-driven growth is disabled, and mini-map variants use 3×3. Secondary layers become either a tightly fitted objective ring or transparency, so stacked markers no longer turn into visual noise. The atlas and every glyph are original project assets.

## Requirements

- [Anomaly Modded Exes](https://github.com/themrdemonized/xray-monolith) with DXML support

The main release archive is ready for MO2 and needs no build tools. Python 3.11+, Pillow, and DirectXTex `texconv.exe` are required only when rebuilding the atlas from source.

## Build the MO2 add-on

Install `AnomalyHope-PDA-Icons-v0.2.0.zip` as a separate MO2 mod and place it below Anomaly Modded Exes.

To rebuild the original atlas from source:

```powershell
python -m pip install -r requirements.txt
./tools/build_local.ps1 `
  -OutputPath 'D:\Hope\mo2\mods\AnomalyHope PDA Icons' `
  -ArchivePath 'D:\Hope\AnomalyHope-PDA-Icons-v0.2.0.zip'
```

If `texconv.exe` is not in `PATH`, add `-TexconvPath 'C:\path\to\texconv.exe'`.

## Technical coverage

`assets/manifest/icons.json` inventories 472 definitions and 254 technical IDs from the standard, widescreen, multiplayer, relation, and complex marker XML files.

The generated DXML patch maps 247 visible marker IDs to 50 semantic categories. It changes icon artwork, palette and display size while keeping bindings, directional headings, map levels, scaling rules, blink timing and XML ordering intact. Structural nodes and definitions without a texture are left untouched.

Run the checks directly with:

```powershell
python ./tools/validate_icon_inventory.py
python ./tools/validate_icon_build.py
python ./tools/validate_icon_build.py --output-root 'D:\Hope\mo2\mods\AnomalyHope PDA Icons'
```

See [`docs/research.md`](docs/research.md) for the resource analysis and known limits.

## License

The source, DXML patch and modern icon atlas in this repository are original project assets covered by the repository license. The inventory describes Anomaly configuration but does not include original game textures.
