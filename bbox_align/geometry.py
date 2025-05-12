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

        return x0, y0

    def angle_of_intersection(self, l2: "Line") -> float:
        '''
        Calculates the angle of intersection between two lines in degrees.
        Returns the acute angle between the lines.
        '''
        try:
            # Slopes of the two lines
            m1 = self._m
            m2 = l2._m

            # Formula for angle between two lines: tan(theta) = |(m2 - m1) / (1 + m1 * m2)|
            tan_theta = abs((m2 - m1) / (1 + m1 * m2))
            theta = atan(tan_theta)  # Angle in radians

            return degrees(theta)  # Convert to degrees
        except ZeroDivisionError:
            # Handle the case where lines are perpendicular
            return 90.0
        # try:
        #     m1 = self._m
        #     m2 = l2._m

        #     # Formula for angle between two lines:
        #     # tan(theta) = |(m2 - m1) / (1 + m1 * m2)|
        #     tan_theta = (m2 - m1) / (1 + m1 * m2)
        #     theta = atan(tan_theta)  # Angle in radians

        #     angle = degrees(theta)

        #     if angle < 0:
        #         angle += 180

        #     return angle
        # except ZeroDivisionError:
        #     # Handle the case where lines are perpendicular
        #     return 90.0