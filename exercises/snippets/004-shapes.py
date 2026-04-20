from dataclasses import dataclass
from functools import partial, singledispatch
from math import pi
from typing import overload

record = partial(dataclass, frozen=True, slots=True)


@record
class Circle:
    radius: float


@record
class Square:
    side: float


Shape = Circle | Square


@overload
def area(shape: Circle) -> float: ...
@overload
def area(shape: Square) -> float: ...


@singledispatch
def area(shape: Shape) -> float:
    raise NotImplementedError(f"area for {type(shape).__name__}")


@area.register
def area_circle(shape: Circle) -> float:
    return pi * shape.radius ** 2


@area.register
def area_square(shape: Square) -> float:
    return shape.side ** 2
