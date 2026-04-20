from dataclasses import dataclass
from functools import partial, singledispatch
from math import pi

record = partial(dataclass, frozen=True, slots=True)


@record
class Circle:
    radius: float


@record
class Square:
    side: float


@singledispatch
def area(shape: object) -> float:
    raise NotImplementedError(f"area for {type(shape).__name__}")


@area.register
def _(shape: Circle) -> float:
    return pi * shape.radius ** 2


@area.register
def _(shape: Square) -> float:
    return shape.side ** 2
