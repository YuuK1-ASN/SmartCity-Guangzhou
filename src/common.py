from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PRO = ROOT / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PRO.mkdir(parents=True, exist_ok=True)

GZ_CENTER = (23.1291, 113.2644)
GZ_BBOX = [112.90, 22.90, 113.75, 23.60]


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少环境变量: {name}")
    return value


GZ_LINE_COLORS = {
    "1号线": "#F4D233",
    "2号线": "#00629B",
    "3号线": "#EF7C1C",
    "3号线北延段": "#EF7C1C",
    "4号线": "#00843D",
    "5号线": "#BB1E10",
    "6号线": "#80276C",
    "7号线": "#97D700",
    "8号线": "#0095DA",
    "9号线": "#71C5E8",
    "13号线": "#F58220",
    "14号线": "#0077C8",
    "21号线": "#92278F",
    "APM线": "#A8D18D",
    "广佛线": "#2BB673",
}
