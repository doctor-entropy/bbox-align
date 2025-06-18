from typing import Tuple, Optional, Union
from .types import Coords
from .geometry import Number, Point


class BoundingBox:

    '''
    Assign rectangle points in a clockwise manner
    top-left, top-right, bottom-right, bottom-left order
    '''
    def __init__(self, p1: Coords, p2: Coords, p3: Coords, p4: Coords, idx: Optional[int]):

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
        self.h_avg = (abs(dp1.y) + abs(dp2.y)) / 2

        # average width of the rectangle
        dp3 = self._p1 - self._p2
        dp4 = self._p3 - self._p4
        self.w_avg = (abs(dp3.x) + abs(dp4.x)) / 2

        self._index = idx

    @property
    def idx(self) -> Union[int, None]:

        return self._index

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

    def is_overlapping(self, other: "BoundingBox") -> Tuple[bool, float]:

        # Extract coordinates for this bounding box
        x1_min, _ = self._p1.co_ordinates
        x1_max, _ = self._p3.co_ordinates

        # Extract coordinates for the other bounding box
        x2_min, _ = other._p1.co_ordinates
        x2_max, _ = other._p3.co_ordinates

        # Check for overlap
        if x1_max < x2_min or x2_max < x1_min:
            return False, 0.0

        # Calculate the intersection width
        overlap_width = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))

        # Calculate the percentage of overlap relative to the smaller box
        bbox1_width = x1_max - x1_min
        bbox2_width = x2_max - x2_min
        smaller_width = min(bbox1_width, bbox2_width)

        overlap_percentage = (overlap_width / smaller_width) * 100 if smaller_width > 0 else 0.0

        return True, overlap_percentage
