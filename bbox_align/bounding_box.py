from typing import Tuple
from geometry import Number, Point, Line

Coords = Tuple[Number, Number]


class BoundingBox:

    '''
    Assign rectangle points in a clockwise manner
    top-left, top-right, bottom-right, bottom-left order
    '''
    def __init__(self, p1: Coords, p2: Coords, p3: Coords, p4: Coords):

        self._p1 = Point(*p1)
        self._p2 = Point(*p2)
        self._p3 = Point(*p3)
        self._p4 = Point(*p4)


        # Midpoint of the bounding box
        self._pm = (self._p1 + self._p3 ) / 2

        # Average slope to calculate the
        # approximate orientation of the rectangle
        m1 = self._p1.slope_wrt(self._p2)
        m2 = self._p3.slope_wrt(self._p4)
        self._m = (m1 + m2) / 2

        # Average height of the rectangle
        dp1 = self._p1 - self._p4
        dp2 = self._p2 - self._p3

        (_, dh1) = dp1.co_ordinates
        (_, dh2) = dp2.co_ordinates

        self.h_avg = (abs(dh1) + abs(dh2)) / 2

        # average width of the rectangle
        dp3 = self._p1 - self._p2
        dp4 = self._p3 - self._p4

        (dw1, _) = dp3.co_ordinates
        (dw2, _) = dp4.co_ordinates
        self.w_avg = (abs(dw1) + abs(dw2)) / 2

    def __lt__(self, other: "BoundingBox"):

        return self.midpoint.is_left_of(other.midpoint)

    def __str__(self) -> str:

        return f"{self._p1}, {self._p2}\n{self._p4}, {self._p3}"

    @property
    def midpoint(self) -> Point:

        return self._pm

    @property
    def p1(self) -> Point:

        return self._p1

    @property
    def p2(self) -> Point:

        return self._p2

    @property
    def p3(self) -> Point:

        return self._p3

    @property
    def p4(self) -> Point:

        return self._p4

    @property
    def approx_orientation(self) -> float:

        return self._m

    @property
    def average_height(self) -> float:

        return self.h_avg

    @property
    def average_width(self) -> float:

        return self.w_avg
