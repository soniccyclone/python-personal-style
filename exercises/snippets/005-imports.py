from __future__ import annotations

import json
import logging
from pathlib import Path


log = logging.getLogger(__name__)


def load_json(path: Path) -> dict:
    log.debug("loading %s", path)
    return json.loads(path.read_text())


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))
