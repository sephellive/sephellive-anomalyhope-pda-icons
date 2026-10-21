#!/usr/bin/env python3
"""Validate the HD atlas plan and, optionally, a local generated build."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from build_icons import collect_rules


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def dds_header(path: Path) -> tuple[int, int, str, int]:
    with path.open("rb") as stream:
        data = stream.read(128)
    if len(data) != 128 or data[:4] != b"DDS ":
        raise ValueError(f"Invalid DDS header: {path}")
    height, width = struct.unpack_from("<II", data, 12)
    mips = struct.unpack_from("<I", data, 28)[0] or 1
    fourcc = data[84:88].decode("ascii", errors="replace").rstrip("\0")
    return width, height, fourcc, mips


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=project / "assets/manifest/icons.json")
    parser.add_argument("--output-root", type=Path, help="Local output from build_icons.py")
    args = parser.parse_args()
    errors: list[str] = []
    inventory = json.loads(args.manifest.read_text(encoding="utf-8"))
    try:
        rules, unresolved = collect_rules(inventory, 2)
    except ValueError as error:
        errors.append(str(error))
        rules, unresolved = {}, set()

    source_files = {str(rule["source_file"]) for rule in rules.values()}
    if len(rules) != 94:
        errors.append(f"expected 94 distinct resolved layer rules, found {len(rules)}")
    if len(source_files) != 5:
        errors.append(f"expected five source atlases, found {sorted(source_files)}")
    if unresolved != {"ui_alife_combat"}:
        errors.append(f"unexpected unresolved symbols: {sorted(unresolved)}")
    for key, rule in rules.items():
        if any(int(rule[field]) <= 0 for field in ("width", "height")):
            errors.append(f"invalid target rectangle for {key}: {rule}")
        if any(int(rule[field]) % 2 for field in ("x", "y", "width", "height")):
            errors.append(f"target rectangle is not an exact 2x mapping for {key}")

    if args.output_root:
        root = args.output_root.resolve()
        report_path = root / "build_report.json"
        script_path = root / "gamedata/scripts/modxml_anomalyhope_pda_icons.script"
        if not report_path.is_file():
            errors.append("local build has no build_report.json")
        if not script_path.is_file():
            errors.append("local build has no generated DXML script")
        if report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if report.get("layer_rule_count") != len(rules):
                errors.append("build report layer count differs from manifest plan")
            if set(report.get("unresolved_texture_ids_left_unchanged", [])) != unresolved:
                errors.append("build report unresolved symbols differ from manifest plan")
            atlases = report.get("atlases", [])
            if len(atlases) != len(source_files):
                errors.append("build report atlas coverage is incomplete")
            for atlas in atlases:
                output = (root / atlas["output_file"]).resolve()
                if root not in output.parents or not output.is_file():
                    errors.append(f"missing or unsafe atlas output: {output}")
                    continue
                width, height, fourcc, mips = dds_header(output)
                source = atlas["source"]
                if (width, height) != (source["width"] * 2, source["height"] * 2):
                    errors.append(f"atlas is not exactly 2x: {output.name}")
                if fourcc != "DXT5" or mips != 1:
                    errors.append(f"unexpected DDS layout for {output.name}: {fourcc}, mips={mips}")
                if digest(output) != atlas["output"]["sha256"]:
                    errors.append(f"atlas hash differs from report: {output.name}")
        if script_path.is_file():
            script = script_path.read_text(encoding="utf-8")
            if script.count("texture = ") != len(rules):
                errors.append("DXML rule count differs from manifest plan")
            if "removeElementAttr" in script:
                errors.append("DXML must preserve layer attributes rather than remove them")
            for name in ("map_spots.xml", "map_spots_16.xml", "map_spots_complex.xml"):
                if name not in script:
                    errors.append(f"DXML target missing: {name}")

    if errors:
        print("FAIL: " + "\nFAIL: ".join(errors), file=sys.stderr)
        return 1
    suffix = f"; local build at {args.output_root} verified" if args.output_root else ""
    print(f"PASS: {len(rules)} layer rules preserve five original atlas families; unresolved: {sorted(unresolved)}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
