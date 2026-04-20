from dataclasses import dataclass
from functools import partial
from math import hypot

record = partial(dataclass, frozen=True, slots=True)


@record
class Point:
    x: float
    y: float


def distance(a: Point, b: Point) -> float:
    return hypot(a.x - b.x, a.y - b.y)
