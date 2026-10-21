#!/usr/bin/env python3
"""Build a PDA marker inventory from extracted Anomaly resource archives."""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

MAP_SPOT_FILES = (
    "map_spots.xml",
    "map_spots_16.xml",
    "map_spots_mp.xml",
    "map_spots_relations.xml",
    "map_spots_complex.xml",
)
ANIMATION_ATTRS = re.compile(r"anim|blink|frame|pulse|cycle|heading|color", re.I)


def parse_xml(path: Path) -> ET.Element:
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"(?m)^[ \t]*#include[^\r\n]*(?:\r?\n|$)", "", text)
    try:
        return ET.fromstring(text)
    except ET.ParseError:
        # Some Anomaly map_spots include files are XML fragments, not documents.
        return ET.fromstring(f"<map_spots>{text}</map_spots>")


def texture_catalog(config_root: Path) -> dict[str, dict[str, str]]:
    catalog: dict[str, dict[str, str]] = {}
    for path in sorted((config_root / "ui" / "textures_descr").rglob("*.xml")):
        try:
            root = parse_xml(path)
        except ET.ParseError:
            continue
        for file_node in root.iter("file"):
            source = file_node.attrib.get("name")
            if not source:
                continue
            for node in file_node.findall("texture"):
                texture_id = node.attrib.get("id")
                if texture_id:
                    catalog[texture_id] = {
                        "file": source.replace("\\", "/"),
                        **node.attrib,
                    }
    return catalog


def node_path(parent_path: str, node: ET.Element) -> str:
    return f"{parent_path}/{node.tag}" if parent_path else node.tag


def texture_layers(
    node: ET.Element,
    catalog: dict[str, dict[str, str]],
    textures_root: Path,
) -> list[dict[str, object]]:
    layers: list[dict[str, object]] = []

    def walk(current: ET.Element, component: str) -> None:
        for child in current:
            child_path = node_path(component, child)
            if child.tag == "texture":
                texture_id = (child.text or "").strip()
                desc = catalog.get(texture_id, {})
                source = desc.get("file")
                lookup_status = "resolved_descriptor" if desc else "unresolved_symbol"
                if source is None and ("\\" in texture_id or "/" in texture_id):
                    source = texture_id.replace("\\", "/")
                    lookup_status = "direct_resource_path"
                rect = {}
                for key in ("x", "y", "width", "height"):
                    value = child.attrib.get(key, desc.get(key))
                    if value is not None:
                        try:
                            rect[key] = int(float(value))
                        except ValueError:
                            rect[key] = value
                layers.append(
                    {
                        "component": child_path,
                        "texture_id": texture_id or None,
                        "original_file": f"textures/{source}.dds" if source else None,
                        "lookup_status": lookup_status,
                        "source_file_found": bool(
                            source and (textures_root / f"{source}.dds").is_file()
                        ),
                        "atlas_rect": rect or None,
                        "attributes": child.attrib,
                    }
                )
            else:
                walk(child, child_path)

    walk(node, "")
    return layers


def collect_bindings(root: ET.Element) -> dict[str, list[dict[str, str]]]:
    bindings: dict[str, list[dict[str, str]]] = defaultdict(list)
    for node in root.iter():
        for attr in ("spot", "pointer"):
            target = node.attrib.get(attr)
            if target:
                bindings[target].append({"element": node.tag, "attribute": attr})
    return bindings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-root", type=Path, required=True,
                        help="Extracted gamedata/configs directory")
    parser.add_argument("--textures-root", type=Path, required=True,
                        help="Extracted gamedata/textures directory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    catalog = texture_catalog(args.config_root)
    entries = []
    unresolved = set()
    for filename in MAP_SPOT_FILES:
        path = args.config_root / "ui" / filename
        if not path.is_file():
            raise SystemExit(f"Missing required inventory source: {path}")
        root = parse_xml(path)
        bindings = collect_bindings(root)
        for node in root:
            layers = texture_layers(node, catalog, args.textures_root)
            if not layers:
                continue
            for layer in layers:
                if layer["lookup_status"] == "unresolved_symbol" and layer["texture_id"]:
                    unresolved.add(layer["texture_id"])
            attrs = dict(node.attrib)
            entries.append(
                {
                    "technical_id": node.tag,
                    "purpose": node.tag,
                    "source_config": f"configs/ui/{filename}",
                    "size": {
                        key: attrs[key]
                        for key in ("width", "height")
                        if key in attrs
                    } or None,
                    "display_attributes": {
                        key: value
                        for key, value in attrs.items()
                        if key not in ("width", "height")
                    },
                    "bindings": bindings.get(node.tag, []),
                    "texture_layers": layers,
                    "states_and_animation": {
                        key: value
                        for element in node.iter()
                        for key, value in element.attrib.items()
                        if ANIMATION_ATTRS.search(key)
                    },
                    "new_file_or_atlas_region": None,
                    "implementation_status": "not_started",
                    "in_game_verification": "pending",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "game": "S.T.A.L.K.E.R. Anomaly 1.5.3",
                "inventory_basis": [
                    "configs/ui/map_spots.xml",
                    "configs/ui/map_spots_16.xml",
                    "configs/ui/map_spots_mp.xml",
                    "configs/ui/map_spots_relations.xml",
                    "configs/ui/map_spots_complex.xml",
                    "configs/ui/textures_descr/*.xml",
                ],
                "base_marker_definition_inventory_complete": True,
                "texture_resolution_complete": not unresolved,
                "notes": [
                    "Entries record configured marker definitions and atlas layers from base archives.",
                    "Texture references without resolved coordinates need investigation before implementation.",
                    "Other addons may add marker IDs and are outside the base-game inventory.",
                ],
                "unresolved_texture_ids": sorted(unresolved),
                "markers": entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(entries)} marker definitions to {args.output}")
    print(f"Texture IDs without resolved coordinates: {len(unresolved)}")


if __name__ == "__main__":
    main()
