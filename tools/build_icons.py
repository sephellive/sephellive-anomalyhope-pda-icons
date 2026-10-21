#!/usr/bin/env python3
"""Generate original SVG glyphs, DDS textures, and a DXML replacement script."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import cairosvg

GLYPHS = {
    "player": ("#C8D0D0", '<path d="M32 5 52 57 32 47 12 57Z"/>'),
    "mission_primary": ("#D98C65", '<path d="m32 5 8 18 19 2-14 13 4 20-17-10-17 10 4-20-14-13 19-2Z"/>'),
    "mission_side": ("#E6BA62", '<path d="M18 9h28a5 5 0 0 1 5 5v36a5 5 0 0 1-5 5H18a5 5 0 0 1-5-5V14a5 5 0 0 1 5-5Z"/><path d="M23 22h18M23 32h18M23 42h9"/>'),
    "mission_done": ("#83B9A0", '<path d="m12 33 13 13 28-29"/>'),
    "stash": ("#83B9A0", '<path d="M12 22h40v31H12zM17 22l4-11h22l4 11M12 32h40M27 32v7h10v-7"/>'),
    "exit": ("#C8D0D0", '<path d="M10 32h35M31 17l15 15-15 15M48 11h7v42h-7"/>'),
    "fast_travel": ("#7EAEC9", '<circle cx="32" cy="32" r="24"/><path d="M32 8v15M32 41v15M8 32h15M41 32h15M32 23l7 9-7 9-7-9Z"/>'),
    "person": ("#C8D0D0", '<circle cx="32" cy="18" r="9"/><path d="M14 56c1-13 7-21 18-21s17 8 18 21M22 56V44M42 44v12"/>'),
    "merchant": ("#E6BA62", '<path d="M12 25h40v30H12zM9 25l5-14h36l5 14M25 25v-7h14v7M21 40h22"/>'),
    "mechanic": ("#C8D0D0", '<path d="M39 12a15 15 0 0 0-18 19L9 43a7 7 0 0 0 10 10l12-12a15 15 0 0 0 19-18l-9 9-10-10Z"/>'),
    "medic": ("#CD6868", '<path d="M24 8h16v16h16v16H40v16H24V40H8V24h16Z"/>'),
    "guide": ("#7EAEC9", '<circle cx="32" cy="32" r="24"/><path d="m42 20-6 16-16 8 6-16Z"/><circle cx="32" cy="32" r="3"/>'),
    "faction": ("#7EAEC9", '<path d="M32 6 53 14v17c0 13-9 22-21 27C20 53 11 44 11 31V14Z"/><path d="m32 17 4 9 10 1-7 7 2 10-9-5-9 5 2-10-7-7 10-1Z"/>'),
    "hostile": ("#CD6868", '<path d="M32 7 59 55H5Z"/><path d="M32 22v15M32 45v1"/>'),
    "anomaly": ("#CD6868", '<circle cx="32" cy="32" r="5"/><path d="M32 8v12M32 44v12M8 32h12M44 32h12M15 15l9 9M40 40l9 9M49 15l-9 9M24 40l-9 9"/>'),
    "artifact": ("#E6BA62", '<path d="m32 6 18 17-8 34H22l-8-34Z"/><path d="m14 23 18 9 18-9M32 32v25M23 14l9 18 9-18"/>'),
    "base": ("#83B9A0", '<path d="M9 54V10l17 7 14-7v44l-14-7Z"/><path d="M17 29h16M17 38h16"/>'),
    "item": ("#C8D0D0", '<path d="M10 20h44v35H10zM10 20l8-10h28l8 10M32 20v35M18 31h7"/>'),
    "marker": ("#778185", '<circle cx="32" cy="32" r="19"/><circle cx="32" cy="32" r="5"/>'),
    "combat": ("#CD6868", '<circle cx="32" cy="32" r="22"/><path d="M32 5v14M32 45v14M5 32h14M45 32h14M22 32h20M32 22v20"/>'),
}

EXCLUSIONS = {
    "no_spot": "Invisible sentinel; replacing it with a visible glyph would reveal markers the base UI suppresses.",
    "debug_stalker_spot": "Debug-only invalid-hint marker, retained as configured for troubleshooting.",
    "complex_map_spot_border": "Structural border overlay, not a map marker glyph.",
    "level_map_spot_border": "Structural border overlay, not a map marker glyph.",
    "mini_map_spot_border": "Structural border overlay, not a map marker glyph.",
}


def category(marker_id: str) -> str:
    name = marker_id.lower()
    if "pointer" in name and "mp_" not in name:
        return "player"
    if "storyline" in name or "primary" in name:
        return "mission_primary"
    if "secondary_task" in name or "stask" in name:
        return "mission_side"
    if "treasure_searched" in name:
        return "mission_done"
    if "treasure" in name or "stash" in name or "box_location" in name or "player_mine" in name:
        return "stash"
    if "mechanic" in name:
        return "mechanic"
    if "medic" in name or "medical" in name:
        return "medic"
    if "trader" in name or "barman" in name:
        return "merchant"
    if "guider" in name or "scout" in name:
        return "guide"
    if "companion" in name or "friend" in name or "allies" in name or "friendly" in name:
        return "person"
    if "enemy" in name or "hostile" in name or "attack" in name or "fight" in name or "combat" in name:
        return "combat"
    if "anomaly" in name or "anom_zone" in name:
        return "anomaly"
    if "artefact" in name or "artifact" in name:
        return "artifact"
    if "level_changer" in name:
        return "exit"
    if "fast_travel" in name:
        return "fast_travel"
    if "item_" in name:
        return "item"
    if name in {"circle_red_spot", "circle_green_spot", "circle_yellow_spot", "circle_empty_spot"}:
        return "marker"
    if name == "circle_target_spot":
        return "hostile"
    if "faction" in name or name.startswith("circle_") or "warfare_" in name or "team_base" in name:
        return "faction"
    if "base" in name or "territory" in name or "smart" in name:
        return "base"
    if "task" in name or "quest" in name:
        return "mission_side"
    if "target" in name or "explo" in name or "deadbody" in name:
        return "hostile"
    if name in {"no_spot", "debug_stalker_spot", "complex_map_spot_border", "level_map_spot_border", "mini_map_spot_border"}:
        return "marker"
    if "actor" in name or "npc" in name or "stalker" in name or "neutral" in name:
        return "person"
    return "marker"


def lua_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "assets/manifest/icons.json")
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--texconv", type=Path, required=True)
    parser.add_argument("--size", type=int, default=128)
    args = parser.parse_args()
    root = args.output_root.resolve()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("base_marker_definition_inventory_complete") is not True:
        raise SystemExit("Refusing generation: marker definition inventory is incomplete")
    marker_categories = {
        marker["technical_id"]: category(marker["technical_id"])
        for marker in manifest["markers"]
        if marker["technical_id"] not in EXCLUSIONS
    }
    source_dir = root / "assets/sources/icons"
    texture_dir = root / "gamedata/textures/ui/anomalyhope/pda/icons"
    source_dir.mkdir(parents=True, exist_ok=True)
    texture_dir.mkdir(parents=True, exist_ok=True)
    for glyph_id, (color, artwork) in GLYPHS.items():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
            'width="64" height="64"><g fill="none" stroke="' + color + '" '
            'stroke-width="4" stroke-linecap="round" stroke-linejoin="round">'
            + artwork + '</g></svg>\n'
        )
        svg_path = source_dir / f"{glyph_id}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        png = cairosvg.svg2png(bytestring=svg.encode(), output_width=args.size, output_height=args.size)
        with tempfile.TemporaryDirectory(prefix="anomalyhope-icon-") as temporary:
            png_path = Path(temporary) / f"{glyph_id}.png"
            png_path.write_bytes(png)
            result = subprocess.run(
                [str(args.texconv), "-nologo", "-y", "-f", "DXT5", "-o", str(temporary), str(png_path)],
                check=False, capture_output=True, text=True,
            )
            dds_path = Path(temporary) / f"{glyph_id}.dds"
            if result.returncode or not dds_path.is_file():
                raise SystemExit(f"texconv failed for {glyph_id}: {result.stdout}\n{result.stderr}")
            (texture_dir / dds_path.name).write_bytes(dds_path.read_bytes())

    map_data = {
        "schema_version": 1,
        "method": "technical_id_semantic_rules",
        "in_game_verification": "pending",
        "documented_exclusions": [
            {"technical_id": marker_id, "reason": reason}
            for marker_id, reason in sorted(EXCLUSIONS.items())
            if marker_id in {item["technical_id"] for item in manifest["markers"]}
        ],
        "markers": [
            {"technical_id": marker_id, "glyph": glyph_id,
             "texture": f"ui\\anomalyhope\\pda\\icons\\{glyph_id}"}
            for marker_id, glyph_id in sorted(marker_categories.items())
        ],
    }
    (root / "assets/manifest/icon_replacements.json").write_text(
        json.dumps(map_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lua_entries = ",\n".join(
        f"\t[{lua_quote(marker_id)}] = {lua_quote(glyph_id)}"
        for marker_id, glyph_id in sorted(marker_categories.items())
    )
    lua = f'''-- Generated by tools/build_icons.py. Do not edit by hand.
local replacements = {{
{lua_entries}
}}

local target_files = {{
    [ [[ui\\map_spots.xml]] ] = true,
    [ [[ui\\map_spots_16.xml]] ] = true,
    [ [[ui\\map_spots_mp.xml]] ] = true,
    [ [[ui\\map_spots_relations.xml]] ] = true,
    [ [[ui\\map_spots_complex.xml]] ] = true,
}}

local function replace_textures(xml_obj, node, glyph)
    xml_obj:iterateChildren(node, function(child)
        if not xml_obj:isElement(child) then return end
        if xml_obj:getElementName(child) == "texture" then
            xml_obj:setText(child, "ui\\\\anomalyhope\\\\pda\\\\icons\\\\" .. glyph)
            xml_obj:removeElementAttr(child, {{"x", "y", "width", "height"}})
        else
            replace_textures(xml_obj, child, glyph)
        end
    end)
end

function on_xml_read()
    RegisterScriptCallback("on_xml_read", function(xml_file_name, xml_obj)
        if not target_files[xml_file_name] then return end
        for marker_id, glyph in pairs(replacements) do
            local matches = xml_obj:query(marker_id)
            for _, node in ipairs(matches) do
                replace_textures(xml_obj, node, glyph)
            end
        end
    end)
end
'''
    runtime = root / "gamedata/scripts/modxml_anomalyhope_pda_icons.script"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text(lua, encoding="utf-8")
    print(f"Built {len(GLYPHS)} standalone DDS glyphs and mapped {len(marker_categories)} marker IDs.")


if __name__ == "__main__":
    main()
