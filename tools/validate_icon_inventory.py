#!/usr/bin/env python3
"""Validate inventory structure and, optionally, local DDS references/bounds."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


def dds_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(128)
    if len(header) != 128 or header[:4] != b"DDS ":
        raise ValueError(f"Invalid DDS header: {path}")
    height, width = struct.unpack_from("<II", header, 12)
    return width, height


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "assets/manifest/icons.json")
    parser.add_argument("--textures-root", type=Path, help="Extracted gamedata/textures root; enables DDS lookup and atlas-bound checks")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors: list[str] = []
    markers = data.get("markers")
    if data.get("game") != "S.T.A.L.K.E.R. Anomaly 1.5.3":
        errors.append("unexpected game version")
    if data.get("base_marker_definition_inventory_complete") is not True:
        errors.append("base marker definition inventory is not marked complete")
    if not isinstance(markers, list) or not markers:
        errors.append("markers must be a non-empty list")
        markers = []

    known_unresolved: set[str] = set()
    texture_root = args.textures_root.resolve() if args.textures_root else None
    checked_files: dict[str, tuple[int, int]] = {}
    for index, marker in enumerate(markers):
        marker_id = marker.get("technical_id")
        if not marker_id or not marker.get("source_config"):
            errors.append(f"marker {index} is missing technical_id/source_config")
        if not isinstance(marker.get("texture_layers"), list) or not marker["texture_layers"]:
            errors.append(f"{marker_id or index}: no texture layers")
            continue
        for layer in marker["texture_layers"]:
            status = layer.get("lookup_status")
            if status == "unresolved_symbol" and layer.get("texture_id"):
                known_unresolved.add(layer["texture_id"])
            source = layer.get("original_file")
            rect = layer.get("atlas_rect")
            if texture_root is None:
                continue
            if not source:
                if status != "unresolved_symbol":
                    errors.append(f"{marker_id}: resolved layer has no source file")
                continue
            normalized = source.replace("\\", "/").lstrip("/")
            if ".." in Path(normalized).parts:
                errors.append(f"{marker_id}: unsafe source path {source}")
                continue
            source_path = texture_root.joinpath(*normalized.split("/"))
            if not source_path.is_file():
                errors.append(f"{marker_id}: missing source DDS {source}")
                continue
            if normalized not in checked_files:
                checked_files[normalized] = dds_size(source_path)
            width, height = checked_files[normalized]
            if rect and all(isinstance(rect.get(k), int) for k in ("x", "y", "width", "height")):
                if rect["x"] < 0 or rect["y"] < 0 or rect["width"] <= 0 or rect["height"] <= 0:
                    errors.append(f"{marker_id}: invalid atlas rectangle {rect}")
                elif rect["x"] + rect["width"] > width or rect["y"] + rect["height"] > height:
                    errors.append(f"{marker_id}: atlas rectangle exceeds {source} ({width}x{height}): {rect}")

    declared = set(data.get("unresolved_texture_ids", []))
    if known_unresolved != declared:
        errors.append(f"unresolved texture list differs from layers: {sorted(known_unresolved ^ declared)}")
    if errors:
        print("FAIL: " + "\nFAIL: ".join(errors), file=sys.stderr)
        return 1
    ids = {marker["technical_id"] for marker in markers}
    suffix = f"; checked {len(checked_files)} local DDS files" if texture_root is not None else ""
    print(f"PASS: {len(markers)} marker definitions, {len(ids)} technical IDs{suffix}; unresolved: {sorted(known_unresolved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
