"""Load registry definitions from YAML — edit files under `registry_data/` to extend without code changes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from solution_planning_api.domain import ArchitectureTemplate, CapabilityBlock


def _as_dict_list(data: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if not isinstance(data, dict):
        return []
    for k in keys:
        block = data.get(k)
        if isinstance(block, list):
            return [x for x in block if isinstance(x, dict)]
    return []


def parse_capabilities_yaml(content: str) -> list[CapabilityBlock]:
    raw = yaml.safe_load(content)
    items = _as_dict_list(raw, "capabilities", "items")
    return [CapabilityBlock.model_validate(item) for item in items]


def parse_architecture_templates_yaml(content: str) -> list[ArchitectureTemplate]:
    raw = yaml.safe_load(content)
    items = _as_dict_list(raw, "architecture_templates", "templates", "items")
    return [ArchitectureTemplate.model_validate(item) for item in items]


def load_capabilities_from_path(path: Path) -> list[CapabilityBlock]:
    return parse_capabilities_yaml(path.read_text(encoding="utf-8"))


def load_architecture_templates_from_path(path: Path) -> list[ArchitectureTemplate]:
    return parse_architecture_templates_yaml(path.read_text(encoding="utf-8"))
