from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class Point:
    x: float
    y: float


def distance(a: Point, b: Point) -> float:
    return hypot(a.x - b.x, a.y - b.y)
