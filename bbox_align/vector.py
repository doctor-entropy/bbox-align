from math import (
    sqrt,
    cos,
    acos,
    atan,
    degrees,
    radians
)
from typing import Union, Tuple
from geometry import Point, Number


class Vector:

    def __init__(self, p: Union[Point, Tuple[Number, Number]]):

        if isinstance(p, Point):
            self._x, self._y = p.co_ordinates
        elif isinstance(p, tuple):
            (self._x, self._y) = p

        self._magnitude = sqrt(self._x ** 2 + self._y ** 2)
        self._theta = degrees(atan(self._y / self.x))

    @property
    def x(self) -> Number:
        return self._x

    @property
    def y(self) -> Number:
        return self._y

    @property
    def magnitude(self) -> float:
        return self._magnitude

    @property
    def angle(self):
        return self._theta

    @property
    def theta(self) -> float:
        return self._theta

    def __repr__(self) -> str:

        return f"Vector({self._x}, {self._y})"

    def __add__(self, v: "Vector") -> "Vector":

        return Vector((self._x + v.x, self._y + v.y))

    def __sub__(self, v: "Vector") -> "Vector":

        return Vector((self._x - v.x, self._y - v.y))

    def unit(self) -> "Vector":

        return Vector(
            (
                self._x / self.magnitude,
                self._y / self.magnitude,
            )
        )

    def dot(self, b: "Vector", theta = None) -> float:

        if theta is not None:
            # Use the formula |A| * |B| * cos(theta)
            return self.magnitude * b.magnitude * cos(radians(theta))
        else:
            # Use the component-wise formula: a.x * b.x + a.y * b.y
            return self.x * b.x + self.y * b.y

    def angle_between_vector(self, b: "Vector") -> float:
        return degrees(
            acos(
                self.dot(b) /
                (self.magnitude * b.magnitude)
            )
        )


def get_vector_between_two_points(p: Point, q: Point) -> Vector:

    return Vector(q) - Vector(p)