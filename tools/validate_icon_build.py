#!/usr/bin/env python3
"""Validate the semantic icon plan and, optionally, a generated game package."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

from icon_design import ATLAS_SIZE, ATLAS_TEXTURE, build_marker_plan


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
        raise ValueError(f"Invalid DDS file: {path}")
    height, width = struct.unpack_from("<II", data, 12)
    mips = struct.unpack_from("<I", data, 28)[0] or 1
    fourcc = data[84:88].decode("ascii", errors="replace").rstrip("\0")
    return width, height, fourcc, mips


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=project / "assets/manifest/icons.json")
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--report-path", type=Path,
                        help="Optional report path when validating a committed package")
    args = parser.parse_args()
    errors: list[str] = []
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    plan = build_marker_plan(manifest)
    categories = {str(rule["category"]) for rule in plan.values()}

    expected_categories = {
        "transition", "pointer", "player", "primary_task", "secondary_task", "danger",
        "anomaly", "friendly", "neutral", "companion", "trader", "mechanic", "medic",
        "guide", "sleep", "stash", "artifact", "faction", "base", "territory",
        "resource", "science", "squad", "ammo", "drink", "food", "kit", "mine",
        "deadbody", "user",
    }
    missing_categories = expected_categories - categories
    if missing_categories:
        errors.append(f"semantic categories missing from plan: {sorted(missing_categories)}")
    if len(plan) < 220:
        errors.append(f"expected broad marker coverage, found only {len(plan)} marker rules")
    for required in ("level_changer_up_spot", "storyline_task_spot", "secondary_task_spot",
                     "ui_pda2_trader_location_spot", "anomaly_thermal_spot"):
        if required not in plan:
            errors.append(f"required marker rule missing: {required}")
    for technical_id, rule in plan.items():
        if int(rule["width"]) <= 0 or int(rule["height"]) <= 0:
            errors.append(f"invalid display size for {technical_id}")
        if not rule["layers"]:
            errors.append(f"marker has no texture layers: {technical_id}")
        for layer in rule["layers"]:
            if layer["texture"] != ATLAS_TEXTURE:
                errors.append(f"unexpected atlas path for {technical_id}")

    if args.output_root:
        root = args.output_root.resolve()
        report_path = args.report_path.resolve() if args.report_path else root / "build_report.json"
        script_path = root / "gamedata/scripts/modxml_anomalyhope_pda_icons.script"
        atlas_path = root / "gamedata/textures/ui/anomalyhope/pda/modern_icons.dds"
        for path in (report_path, script_path, atlas_path):
            if not path.is_file():
                errors.append(f"generated file missing: {path}")
        if report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if report.get("marker_rule_count") != len(plan):
                errors.append("build report marker count differs from semantic plan")
            if report.get("atlas_texture") != ATLAS_TEXTURE:
                errors.append("build report atlas texture differs from design")
            if atlas_path.is_file() and digest(atlas_path) != report.get("atlas", {}).get("sha256"):
                errors.append("atlas hash differs from build report")
        if atlas_path.is_file():
            width, height, fourcc, mips = dds_header(atlas_path)
            if (width, height) != (ATLAS_SIZE, ATLAS_SIZE):
                errors.append(f"unexpected atlas dimensions: {width}x{height}")
            if fourcc != "DXT5" or mips != 1:
                errors.append(f"unexpected atlas layout: {fourcc}, mips={mips}")
        if script_path.is_file():
            script = script_path.read_text(encoding="utf-8")
            if script.count("layers = {") != len(plan):
                errors.append("DXML rule count differs from semantic plan")
            if "r = 255, g = 255, b = 255" not in script:
                errors.append("DXML does not neutralize legacy marker tint")
            if "height = rule.height, scale = 0" not in script:
                errors.append("DXML does not disable zoom-driven marker growth")
            if 'element_name == "static_border"' not in script:
                errors.append("DXML does not resize nested objective borders")
            for name in ("map_spots.xml", "map_spots_16.xml", "map_spots_complex.xml"):
                if name not in script:
                    errors.append(f"DXML target missing: {name}")

    if errors:
        print("FAIL: " + "\nFAIL: ".join(errors), file=sys.stderr)
        return 1
    suffix = f"; local build at {args.output_root} verified" if args.output_root else ""
    print(f"PASS: {len(plan)} markers mapped to {len(categories)} minimalist semantic categories{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
