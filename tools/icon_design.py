#!/usr/bin/env python3
"""Original minimalist PDA icon system used by the local and release builders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ATLAS_SIZE = 1024
CELL_SIZE = 64
ATLAS_TEXTURE = r"ui\anomalyhope\pda\modern_icons"

PALETTE = {
    "panel": (18, 21, 20, 232),
    "ivory": (229, 218, 194, 255),
    "amber": (215, 153, 56, 255),
    "rust": (188, 73, 49, 255),
    "sage": (137, 166, 132, 255),
    "steel": (137, 153, 156, 255),
    "muted": (135, 128, 114, 255),
    "olive": (142, 151, 101, 255),
    "umber": (152, 118, 86, 255),
    "burgundy": (165, 80, 68, 255),
    "forest": (112, 157, 104, 255),
    "ochre": (190, 156, 78, 255),
    "slate": (103, 137, 149, 255),
    "ash": (159, 160, 151, 255),
    "violet": (139, 114, 144, 255),
    "teal": (92, 144, 139, 255),
    "transparent": (0, 0, 0, 0),
}


@dataclass(frozen=True)
class IconSpec:
    name: str
    glyph: str
    color: str
    framed: bool = True


ICONS = (
    IconSpec("transition", "chevron", "ivory"),
    IconSpec("pointer", "chevron", "ivory", False),
    IconSpec("player", "player", "ivory"),
    IconSpec("primary_task", "star", "amber"),
    IconSpec("secondary_task", "diamond_dot", "amber"),
    IconSpec("target", "target", "amber"),
    IconSpec("danger", "warning", "rust"),
    IconSpec("anomaly", "anomaly", "rust"),
    IconSpec("anomaly_chemical", "anomaly", "sage"),
    IconSpec("anomaly_electric", "anomaly", "ochre"),
    IconSpec("anomaly_gravitational", "anomaly", "slate"),
    IconSpec("anomaly_radioactive", "anomaly", "violet"),
    IconSpec("anomaly_thermal", "anomaly", "rust"),
    IconSpec("anomaly_disabled", "anomaly", "muted"),
    IconSpec("friendly", "friendly", "sage"),
    IconSpec("neutral", "dot", "ivory"),
    IconSpec("companion", "companion", "sage"),
    IconSpec("trader", "trade", "sage"),
    IconSpec("mechanic", "wrench", "sage"),
    IconSpec("medic", "medical", "sage"),
    IconSpec("guide", "compass", "sage"),
    IconSpec("sleep", "moon", "sage"),
    IconSpec("stash", "crate", "amber"),
    IconSpec("artifact", "artifact", "amber"),
    IconSpec("faction", "shield", "steel"),
    IconSpec("faction_stalker", "shield", "amber"),
    IconSpec("faction_army", "shield", "olive"),
    IconSpec("faction_bandit", "shield", "umber"),
    IconSpec("faction_duty", "shield", "burgundy"),
    IconSpec("faction_freedom", "shield", "forest"),
    IconSpec("faction_csky", "shield", "slate"),
    IconSpec("faction_ecolog", "shield", "ochre"),
    IconSpec("faction_killer", "shield", "ash"),
    IconSpec("faction_monolith", "shield", "ivory"),
    IconSpec("faction_greh", "shield", "violet"),
    IconSpec("faction_isg", "shield", "teal"),
    IconSpec("faction_renegade", "shield", "rust"),
    IconSpec("faction_zombied", "shield", "muted"),
    IconSpec("faction_mutant", "shield", "rust"),
    IconSpec("base", "base", "steel"),
    IconSpec("territory", "flag", "steel"),
    IconSpec("resource", "crate", "steel"),
    IconSpec("science", "flask", "steel"),
    IconSpec("squad", "squad", "steel"),
    IconSpec("ammo", "ammo", "amber"),
    IconSpec("drink", "drink", "amber"),
    IconSpec("food", "food", "amber"),
    IconSpec("kit", "kit", "amber"),
    IconSpec("mine", "mine", "rust"),
    IconSpec("deadbody", "deadbody", "muted"),
    IconSpec("user", "pin", "ivory"),
    IconSpec("pulse", "ring", "amber", False),
    IconSpec("blank", "blank", "transparent", False),
)


def classify_marker(technical_id: str) -> str | None:
    """Map every useful runtime marker to one compact semantic icon."""
    name = technical_id.lower()
    if name in {"no_spot", "level_map_spot_border", "mini_map_spot_border", "complex_map_spot_border"}:
        return None
    if name.startswith("crlc_big") or name.startswith("crlc_mdl") or name.startswith("crlc_small"):
        return None
    if "pointer" in name:
        return "danger" if "combat" in name or "enemy" in name else "pointer"
    if "level_changer" in name:
        return "transition"
    if "sleep" in name:
        return "sleep"
    if "actor_" in name or "mp_self" in name:
        return "player"
    if "storyline" in name or "primary" in name or "selected_target" in name:
        return "primary_task"
    if "secondary_task" in name or "quest_npc" in name:
        return "secondary_task"
    if "combat" in name or "enemy" in name or name.startswith("red_") or "squad_enemy" in name:
        return "danger"
    if "anomaly_chemical" in name:
        return "anomaly_chemical"
    if "anomaly_electric" in name:
        return "anomaly_electric"
    if "anomaly_gravitational" in name:
        return "anomaly_gravitational"
    if "anomaly_radioactive" in name:
        return "anomaly_radioactive"
    if "anomaly_thermal" in name:
        return "anomaly_thermal"
    if "anomaly_disabled" in name:
        return "anomaly_disabled"
    if "anomaly" in name or name.startswith("anom_"):
        return "anomaly"
    if "artefact" in name or "artifact" in name or "_af_" in name:
        return "artifact"
    if "treasure" in name:
        return "stash"
    if "trader" in name or "barman" in name:
        return "trader"
    if "mechanic" in name:
        return "mechanic"
    if "medic" in name or "medical" in name:
        return "medic"
    if "scout" in name or "guider" in name or "fast_travel" in name:
        return "guide"
    if "player_mine" in name:
        return "mine"
    if "companion" in name:
        return "companion"
    if "deadbody" in name:
        return "deadbody"
    if name.startswith("item_ammo"):
        return "ammo"
    if name.startswith("item_drink"):
        return "drink"
    if name.startswith("item_food"):
        return "food"
    if name.startswith("item_kit"):
        return "kit"
    if name.startswith("item_"):
        return "stash"
    if "science" in name:
        return "science"
    if "resource" in name:
        return "resource"
    if "territory" in name:
        return "territory"
    if "base" in name:
        return "base"
    if "squad" in name:
        return "squad"
    if "friend" in name or "allies" in name or name.startswith("green_"):
        return "friendly"
    if "neutral" in name or name.startswith("blue_"):
        return "neutral"
    faction_aliases = {
        "stalker": "stalker", "army": "army", "bandit": "bandit",
        "dolg": "duty", "duty": "duty", "freedom": "freedom",
        "csky": "csky", "ecolog": "ecolog", "killer": "killer",
        "monolith": "monolith", "greh": "greh", "isg": "isg",
        "renegade": "renegade", "zombied": "zombied", "mutant": "mutant",
        "monster": "mutant",
    }
    if "faction" in name or name.startswith("circle_") or name.startswith("warfare_"):
        for token, alias in faction_aliases.items():
            if token in name:
                return f"faction_{alias}"
        return "faction"
    if "target" in name:
        return "target"
    if "explo" in name:
        return "danger"
    if "user_defined" in name or "special_location" in name:
        return "user"
    if "spot" in name or name.endswith("_tex"):
        return "neutral"
    return None


def marker_size(technical_id: str, category: str) -> tuple[int, int]:
    name = technical_id.lower()
    mini = "mini" in name
    if category == "pointer":
        return (3, 8) if mini or "small" in name else (4, 10)
    if category == "transition":
        return (3, 3) if mini else (5, 5)
    if category == "primary_task":
        return (5, 5) if mini else (7, 7)
    if category in {"secondary_task", "target"}:
        return (4, 4) if mini else (6, 6)
    if category.startswith("anomaly") or category in {"squad", "danger", "friendly", "neutral"}:
        return (3, 3) if mini else (4, 4)
    if category == "player":
        return (4, 4) if mini else (6, 6)
    return (4, 4) if mini else (5, 5)


def atlas_regions() -> dict[str, dict[str, int]]:
    regions: dict[str, dict[str, int]] = {}
    for index, spec in enumerate(ICONS):
        regions[spec.name] = {
            "x": (index % (ATLAS_SIZE // CELL_SIZE)) * CELL_SIZE,
            "y": (index // (ATLAS_SIZE // CELL_SIZE)) * CELL_SIZE,
            "width": CELL_SIZE,
            "height": CELL_SIZE,
        }
    return regions


def build_marker_plan(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for marker in manifest["markers"]:
        grouped.setdefault(str(marker["technical_id"]), []).append(marker)
    regions = atlas_regions()
    plan: dict[str, dict[str, object]] = {}
    for technical_id, definitions in sorted(grouped.items()):
        category = classify_marker(technical_id)
        layer_count = max(len(item.get("texture_layers", [])) for item in definitions)
        if not category or not layer_count:
            continue
        width, height = marker_size(technical_id, category)
        layers = [category]
        for _ in range(1, layer_count):
            layers.append("pulse" if category in {"primary_task", "secondary_task", "target"} else "blank")
        plan[technical_id] = {
            "category": category,
            "width": width,
            "height": height,
            "layers": [{"texture": ATLAS_TEXTURE, **regions[name]} for name in layers],
        }
    return plan


def _poly(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: tuple[int, ...]) -> None:
    draw.polygon(points, fill=fill)


def _draw_glyph(draw: ImageDraw.ImageDraw, glyph: str, color: tuple[int, ...]) -> None:
    line = 5
    if glyph == "blank":
        return
    if glyph == "chevron":
        draw.line([(22, 36), (32, 26), (42, 36)], fill=color, width=7, joint="curve")
    elif glyph == "player":
        _poly(draw, [(32, 14), (45, 46), (32, 40), (19, 46)], color)
        _poly(draw, [(32, 25), (37, 39), (32, 36), (27, 39)], PALETTE["panel"])
    elif glyph == "star":
        _poly(draw, [(32, 15), (37, 26), (49, 27), (40, 35), (43, 47), (32, 41), (21, 47), (24, 35), (15, 27), (27, 26)], color)
    elif glyph == "diamond_dot":
        draw.line([(32, 15), (48, 32), (32, 49), (16, 32), (32, 15)], fill=color, width=line, joint="curve")
        draw.ellipse((28, 28, 36, 36), fill=color)
    elif glyph == "target":
        draw.ellipse((18, 18, 46, 46), outline=color, width=4)
        draw.ellipse((27, 27, 37, 37), fill=color)
        draw.line((32, 12, 32, 22), fill=color, width=4)
        draw.line((32, 42, 32, 52), fill=color, width=4)
        draw.line((12, 32, 22, 32), fill=color, width=4)
        draw.line((42, 32, 52, 32), fill=color, width=4)
    elif glyph == "warning":
        _poly(draw, [(32, 13), (51, 48), (13, 48)], color)
        draw.line((32, 25, 32, 37), fill=PALETTE["panel"], width=5)
        draw.ellipse((29, 41, 35, 47), fill=PALETTE["panel"])
    elif glyph == "anomaly":
        draw.ellipse((17, 17, 47, 47), outline=color, width=4)
        draw.arc((23, 13, 49, 39), 80, 260, fill=color, width=4)
        draw.arc((15, 25, 41, 51), 260, 80, fill=color, width=4)
    elif glyph == "friendly":
        draw.ellipse((17, 17, 47, 47), outline=color, width=4)
        draw.line((23, 33, 29, 39, 42, 24), fill=color, width=5, joint="curve")
    elif glyph == "dot":
        draw.ellipse((25, 25, 39, 39), fill=color)
    elif glyph == "companion":
        draw.ellipse((18, 20, 30, 32), fill=color)
        draw.ellipse((34, 20, 46, 32), fill=color)
        draw.arc((14, 27, 34, 48), 190, 350, fill=color, width=5)
        draw.arc((30, 27, 50, 48), 190, 350, fill=color, width=5)
    elif glyph == "trade":
        draw.line((17, 24, 43, 24, 47, 39, 23, 39, 17, 19), fill=color, width=4, joint="curve")
        draw.ellipse((25, 42, 31, 48), fill=color)
        draw.ellipse((40, 42, 46, 48), fill=color)
    elif glyph == "wrench":
        draw.line((20, 45, 43, 22), fill=color, width=7)
        draw.arc((34, 13, 52, 31), 80, 270, fill=color, width=6)
        draw.ellipse((14, 40, 24, 50), outline=color, width=4)
    elif glyph == "medical":
        draw.rounded_rectangle((27, 15, 37, 49), radius=2, fill=color)
        draw.rounded_rectangle((15, 27, 49, 37), radius=2, fill=color)
    elif glyph == "compass":
        draw.ellipse((16, 16, 48, 48), outline=color, width=4)
        _poly(draw, [(38, 20), (34, 36), (20, 44), (28, 28)], color)
    elif glyph == "moon":
        draw.ellipse((18, 15, 45, 48), fill=color)
        draw.ellipse((28, 11, 50, 40), fill=PALETTE["panel"])
    elif glyph == "crate":
        draw.rectangle((17, 20, 47, 46), outline=color, width=4)
        draw.line((18, 21, 46, 45), fill=color, width=3)
        draw.line((46, 21, 18, 45), fill=color, width=3)
    elif glyph == "artifact":
        _poly(draw, [(32, 13), (48, 28), (40, 49), (24, 49), (16, 28)], color)
        _poly(draw, [(32, 22), (39, 30), (35, 41), (29, 41), (25, 30)], PALETTE["panel"])
    elif glyph == "shield":
        _poly(draw, [(32, 14), (47, 20), (44, 40), (32, 50), (20, 40), (17, 20)], color)
        draw.line((32, 20, 32, 43), fill=PALETTE["panel"], width=3)
    elif glyph == "base":
        _poly(draw, [(14, 30), (32, 15), (50, 30), (46, 48), (18, 48)], color)
        draw.rectangle((28, 34, 36, 48), fill=PALETTE["panel"])
    elif glyph == "flag":
        draw.line((22, 14, 22, 50), fill=color, width=5)
        _poly(draw, [(24, 16), (47, 20), (38, 32), (24, 29)], color)
    elif glyph == "flask":
        draw.line((27, 15, 37, 15), fill=color, width=4)
        draw.line((29, 17, 29, 30, 18, 47, 46, 47, 35, 30, 35, 17), fill=color, width=4, joint="curve")
        draw.line((22, 39, 42, 39), fill=color, width=3)
    elif glyph == "squad":
        draw.ellipse((15, 27, 25, 37), fill=color)
        draw.ellipse((27, 19, 37, 29), fill=color)
        draw.ellipse((39, 27, 49, 37), fill=color)
    elif glyph == "ammo":
        for x in (22, 31, 40):
            draw.rounded_rectangle((x, 19, x + 6, 46), radius=3, fill=color)
    elif glyph == "drink":
        draw.line((23, 19, 41, 19, 38, 48, 26, 48, 23, 19), fill=color, width=4, joint="curve")
        draw.line((26, 30, 38, 30), fill=color, width=3)
    elif glyph == "food":
        draw.ellipse((17, 25, 47, 45), outline=color, width=4)
        draw.arc((19, 14, 45, 36), 180, 360, fill=color, width=4)
    elif glyph == "kit":
        draw.rounded_rectangle((16, 21, 48, 47), radius=4, outline=color, width=4)
        draw.line((25, 21, 25, 16, 39, 16, 39, 21), fill=color, width=4)
    elif glyph == "mine":
        draw.ellipse((18, 22, 46, 50), outline=color, width=4)
        draw.line((32, 13, 32, 24), fill=color, width=4)
        draw.line((17, 18, 24, 26), fill=color, width=4)
        draw.line((47, 18, 40, 26), fill=color, width=4)
    elif glyph == "deadbody":
        draw.line((20, 20, 44, 44), fill=color, width=6)
        draw.line((44, 20, 20, 44), fill=color, width=6)
    elif glyph == "pin":
        draw.ellipse((20, 13, 44, 37), outline=color, width=4)
        _poly(draw, [(23, 33), (41, 33), (32, 51)], color)
        draw.ellipse((28, 21, 36, 29), fill=color)
    elif glyph == "ring":
        draw.ellipse((8, 8, 56, 56), outline=color, width=3)


def render_atlas(path: Path) -> dict[str, dict[str, int]]:
    atlas = Image.new("RGBA", (ATLAS_SIZE, ATLAS_SIZE), PALETTE["transparent"])
    regions = atlas_regions()
    for spec in ICONS:
        region = regions[spec.name]
        cell = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), PALETTE["transparent"])
        draw = ImageDraw.Draw(cell)
        color = PALETTE[spec.color]
        if spec.framed:
            draw.rounded_rectangle((8, 8, 56, 56), radius=14, fill=PALETTE["panel"], outline=color, width=4)
        _draw_glyph(draw, spec.glyph, color)
        atlas.alpha_composite(cell, (region["x"], region["y"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(path, "PNG", optimize=False)
    return regions


def render_preview(path: Path) -> None:
    columns = 3
    tile_w, tile_h = 280, 96
    rows = (len(ICONS) + columns - 1) // columns
    preview = Image.new("RGB", (columns * tile_w, rows * tile_h), (31, 32, 29))
    atlas = Image.new("RGBA", (ATLAS_SIZE, ATLAS_SIZE), PALETTE["transparent"])
    temporary = path.with_suffix(".atlas.tmp.png")
    render_atlas(temporary)
    atlas = Image.open(temporary).convert("RGBA")
    temporary.unlink()
    regions = atlas_regions()
    font = ImageFont.load_default(size=16)
    draw = ImageDraw.Draw(preview)
    for index, spec in enumerate(ICONS):
        x = (index % columns) * tile_w
        y = (index // columns) * tile_h
        region = regions[spec.name]
        icon = atlas.crop((region["x"], region["y"], region["x"] + CELL_SIZE, region["y"] + CELL_SIZE))
        preview.paste(icon, (x + 12, y + 16), icon)
        draw.text((x + 86, y + 38), spec.name, fill=(226, 219, 202), font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    preview.save(path, "PNG", optimize=True)
