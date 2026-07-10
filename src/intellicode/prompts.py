from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PromptTemplate:
    system: str
    user: str

    def render(self, **values: Any) -> tuple[str, str]:
        normalized = {
            key: value if isinstance(value, str) else json.dumps(value, indent=2)
            for key, value in values.items()
        }
        return self.system.format(**normalized), self.user.format(**normalized)


class PromptRegistry:
    def __init__(self, path: str | Path):
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self._templates = {
            name: PromptTemplate(system=value["system"], user=value["user"])
            for name, value in raw.items()
        }

    def get(self, name: str) -> PromptTemplate:
        if name not in self._templates:
            raise KeyError(f"Unknown prompt template: {name}")
        return self._templates[name]
