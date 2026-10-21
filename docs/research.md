# PDA marker research

**Status: preliminary.** This note records publicly verifiable implementation clues. It is not the required Anomaly 1.5.3 asset inventory. The installed game archives and extracted `gamedata` were not available during this pass, so no marker count, atlas coordinates, animation list, or full compatibility claim is made.

## Findings from existing implementations

- Community Anomaly addons identify `configs/ui/map_spots.xml` and `map_spots_16.xml` as controls for stash marker sizing, `ui_actor_pda_icons.xml` for most PDA icon appearance, and `ui_hud.xml` for the fast travel icon and quest tracker arrow. This is a useful search list, not proof that it is complete for Anomaly 1.5.3. See [Visible PDA MAP Icons - Bigger and Brighter V4](https://www.moddb.com/mods/stalker-anomaly/addons/visible-pda-map-icons-bigger-and-brighter).
- Existing marker addons replace or add dedicated DDS atlases, and one documented Anomaly 1.5.3 addon uses `gamedata/textures/ui/AzzFat_Icons/ui_AzzFat_MapIcons.dds` plus a `modxml_*.script` patch. The author specifically warns about load order and marker `location_level`, indicating that draw order is a behavior that needs verification. See [Vanilla Player Map Marker Revival (DXML)](https://www.moddb.com/mods/stalker-anomaly/addons/vanilla-map-marker-newpda-manarrow-revival).
- DXML operates on XML as it is read via Lua callbacks and requires the modded executable implementation. Its upstream documentation shows the `modxml_<name>.script` convention. See [DXML documentation](https://github.com/themrdemonized/STALKER-Anomaly-modded-exes/blob/main/docs/DXML.md) and [Anomaly Modded Exes](https://github.com/themrdemonized/xray-monolith).
- Anomaly's loose-resource override layout mirrors the packaged archive paths; `gamedata` resources take priority over `.db` content. See the [Anomaly Modding Book folder guide](https://github.com/TheParaziT/anomaly-modding-book/blob/main/docs/getting-started/main-folders-and-files.md).

## Design implications (pending local verification)

1. Inventory the exact 1.5.3 resources before drawing or replacing markers: search extracted XML, LTX, Lua, and DDS files, then cross-reference marker IDs, textures, coordinates, states, dimensions, and map/minimap usage.
2. Prefer a dedicated DDS atlas when the UI XML supports it; this avoids overwriting broad shared UI atlases. Confirm this with actual 1.5.3 references before choosing the implementation.
3. Use DXML only for targeted XML edits that cannot be achieved by a texture-only replacement, and declare Modded Exes as a dependency if required.
4. Preserve marker IDs, atlas coordinate semantics, frame sequences, scaling rules, and draw-layer behavior. Confirm each in-game before release.

## Required next research pass

- Obtain the user's Anomaly 1.5.3 game directory (or a lawful local archive extraction) and record the exact game/build version.
- Extract only relevant UI/config/script resources; enumerate every map marker texture and reference.
- Build `assets/manifest/icons.json` from the extracted files, then validate atlas rectangles and reference coverage before generating the icon set.
- Check for Anomaly Modded Exes and relevant UI/PDA mods in the user's test profile; do not infer those dependencies from public addon examples.

## Sources consulted

- [Visible PDA MAP Icons - Bigger and Brighter V4](https://www.moddb.com/mods/stalker-anomaly/addons/visible-pda-map-icons-bigger-and-brighter)
- [Vanilla Player Map Marker Revival (DXML)](https://www.moddb.com/mods/stalker-anomaly/addons/vanilla-map-marker-newpda-manarrow-revival)
- [DXML documentation](https://github.com/themrdemonized/STALKER-Anomaly-modded-exes/blob/main/docs/DXML.md)
- [Anomaly Modding Book: main folders and files](https://github.com/TheParaziT/anomaly-modding-book/blob/main/docs/getting-started/main-folders-and-files.md)
