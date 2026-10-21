#!/usr/bin/env python3
"""Check generated glyph coverage, DDS payloads, SVG sources, and DXML references."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    inventory = json.loads((root / "assets/manifest/icons.json").read_text(encoding="utf-8"))
    replacements = json.loads((root / "assets/manifest/icon_replacements.json").read_text(encoding="utf-8"))
    source_ids = {item["technical_id"] for item in inventory["markers"]}
    rows = replacements.get("markers", [])
    replacement_ids = {item["technical_id"] for item in rows}
    exclusions = replacements.get("documented_exclusions", [])
    excluded_ids = {item["technical_id"] for item in exclusions}
    if source_ids != replacement_ids | excluded_ids:
        errors.append(f"replacement/exclusion coverage mismatch: missing={sorted(source_ids-replacement_ids-excluded_ids)[:8]}, extra={sorted((replacement_ids|excluded_ids)-source_ids)[:8]}")
    if replacement_ids & excluded_ids:
        errors.append(f"IDs cannot be both replaced and excluded: {sorted(replacement_ids & excluded_ids)}")

    glyphs = {row["glyph"] for row in rows}
    for glyph in sorted(glyphs):
        svg = root / "assets/sources/icons" / f"{glyph}.svg"
        dds = root / "gamedata/textures/ui/anomalyhope/pda/icons" / f"{glyph}.dds"
        if not svg.is_file():
            errors.append(f"missing SVG source: {svg.relative_to(root)}")
        if not dds.is_file():
            errors.append(f"missing runtime DDS: {dds.relative_to(root)}")
            continue
        with dds.open("rb") as stream:
            data = stream.read(128)
        if len(data) < 128 or data[:4] != b"DDS ":
            errors.append(f"invalid DDS header: {dds.relative_to(root)}")
            continue
        height, width = struct.unpack_from("<II", data, 12)
        fourcc = data[84:88].decode("ascii", errors="replace").rstrip("\0")
        if (width, height) != (128, 128) or fourcc != "DXT5":
            errors.append(f"unexpected DDS format/dimensions for {glyph}: {fourcc} {width}x{height}")

    script_path = root / "gamedata/scripts/modxml_anomalyhope_pda_icons.script"
    if not script_path.is_file():
        errors.append("missing generated DXML runtime script")
    else:
        script = script_path.read_text(encoding="utf-8")
        for marker_id in sorted(replacement_ids):
            if f'["{marker_id}"]' not in script:
                errors.append(f"DXML script has no mapping for {marker_id}")
        for marker_id in sorted(excluded_ids):
            if f'["{marker_id}"]' in script:
                errors.append(f"DXML script unexpectedly modifies documented exclusion {marker_id}")
        if "map_spots_16.xml" not in script or "removeElementAttr" not in script:
            errors.append("DXML script is missing widescreen or atlas-coordinate patch logic")

    if errors:
        print("FAIL: " + "\nFAIL: ".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(replacement_ids)} marker IDs use {len(glyphs)} SVG/DDS glyphs; {len(excluded_ids)} IDs have documented exclusions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
