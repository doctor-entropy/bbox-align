from math import inf, atan, degrees, radians
from typing import Union, Tuple

Number = Union[float, int]


class Point:

    def __init__(self, x: Number, y: Number):

        self._x = x
        self._y = y

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Point):
            return NotImplemented

        return self._x == other.x and self._y == other.y

    def __ne__(self, other: object) -> bool:

        if not isinstance(other, Point):
            return NotImplemented

        return self._x != other.x or self._y != other.y

    def __add__(self, other: "Point") -> "Point":

        return Point(self._x + other.x, self._y + other.y)

    def __sub__(self, other: "Point") -> "Point":

        return Point(self._x - other.x, self._y - other.y)

    def __floordiv__(self, scalar: Number) -> "Point":

        return Point(self._x // scalar, self._y // scalar)

    def __truediv__(self, scalar: Number) -> "Point":

        return Point(self._x / scalar, self._y / scalar)

    def __str__(self) -> str:

        return f"({self._x}, {self._y})"

    def __repr__(self) -> str:

        return self.__str__()

    def is_above(self, other: "Point") -> bool:

        return self._y > other.y

    def is_below(self, other: "Point") -> bool:

        return self._y < other.y

    def is_left_of(self, other: "Point") -> bool:

        return self._x < other.x

    def is_right_of(self, other: "Point") -> bool:

        return self._x > other.x

    @property
    def co_ordinates(self) -> Tuple[Number, Number]:

        return (self._x, self._y)

    @property
    def x(self) -> Number:

        return self._x

    @property
    def y(self) -> Number:

        return self._y

    def slope_wrt(self, other: "Point") -> float:

        (dx, dy) = (self - other).co_ordinates

        try:
            return dy / dx
        except ZeroDivisionError:
            return inf

    def distance_to_point(self, other: "Point") -> float:

        (dx, dy) = (self - other).co_ordinates

        return (dx**2 + dy**2) ** 0.5

    '''
    finding the shortest distance between
    the line and a point, which return the
    perpendicular distance
    '''
    def distance_to_line(self, l: "Line") -> float:

        A, B, C = l.standard_form_coeffs

        return abs(A*self._x + B*self._y + C) / (A**2 + B**2) ** 0.5

    def reflect_on_line(self, l: "Line") -> "Point":

        return l.reflect_point(self)


class Line:

    '''
    Accepts parameters of line in Point-Slope form
    '''
    def __init__(self, p: Point, m: Number):

        self._m = m

        x, y = p.co_ordinates
        self._c = y - (x * self._m)

    '''
    print in slope-intercept form y = mx + c
    '''
    def __str__(self) -> str:

        return f"y = {self._m}.x + {self._c}"

    '''
    returns coeffecients of standard form
    0 = Ax + By + C
    '''
    @property
    def standard_form_coeffs(self) -> Tuple[Number, int, Number]:

        return self._m, -1, self._c

    '''
    finding the shortest distance between
    the line and a point, which return the
    perpendicular distance
    '''
    def distance_to_point(self, p: Point):

        return p.distance_to_line(self)

    def find_x(self, y: Number) -> Number:

        try:
            return (y - self._c) / self._m
        except ZeroDivisionError:
            return inf

    def find_y(self, x: Number) -> Number:

        return self._m * x + self._c

    def point_position(self, p: Point) -> Number:

        x, y = p.co_ordinates

        y_bar = self.find_y(x)

        return y_bar - y

    def point_of_intersection(self, l2: "Line") -> Tuple[float, float]:

        A1, B1, C1 = self.standard_form_coeffs
        A2, B2, C2 = l2.standard_form_coeffs

        try:
            denom = (A1*B2) - (A2*B1)

            x0 = (B1*C2 - B2*C1) / denom
            y0 = (C1*A2 - C2*A1) / denom

        except ZeroDivisionError:

            x0, y0 = inf, inf

        return Point(x0, y0)

    def reflect_point(self, p: Point) -> Point:
        """
        Reflects a point across the line.

        :param p: The point to reflect.
        :return: The reflected point.
        """
        # Line coefficients: Ax + By + C = 0
        A, B, C = self.standard_form_coeffs

        # Coordinates of the point
        x1, y1 = p.co_ordinates

        # Formula for reflection:
        # x' = x - 2 * A * (A*x + B*y + C) / (A^2 + B^2)
        # y' = y - 2 * B * (A*x + B*y + C) / (A^2 + B^2)
        denom = A**2 + B**2
        x_reflected = x1 - 2 * A * (A * x1 + B * y1 + C) / denom
        y_reflected = y1 - 2 * B * (A * x1 + B * y1 + C) / denom

        return Point(x_reflected, y_reflected)
