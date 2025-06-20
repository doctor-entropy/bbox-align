import statistics
from math import inf
from copy import deepcopy
from functools import reduce

from typing import Tuple, List, Union, Optional
from .types import (
    PointOfIntersections,
    PassThroughs,
    InLines,
    Line,
    Lines
)
from .geometry import Point, Line as GeometryLine
from .bounding_box import BoundingBox


'''
-------------           -------------
-           -           -           -
-   m1*.....-...........-.....*m2   -
-           -     l     -           -
-------------           -------------
  rect1                      rect2
                       height=H

'd' is the perpendicular distance between
line 'l' and 'm2'.

m1 and m2 are the midpoints of the boxes shown above
'''
def is_passing_through(
    bbox1: BoundingBox, bbox2: BoundingBox
) -> Tuple[bool, float]:

    l1 = GeometryLine(bbox1.midpoint, bbox1.approx_orientation)
    d = l1.distance_to_point(bbox2.midpoint)
    is_inline = d <= bbox2.average_height / 2

    return (is_inline, d)

'''
Two boxes - box1 and box2 are said to passthrough
if the line passing through the midpoint of box1
and the perpendicular distance from the midpoint
of box2 is less than half of average height of the latter.
In other words the line passes through the second boundingbox
'''
def any_passing_through(
    bbox1: BoundingBox, bbox2: BoundingBox
) -> Tuple[bool, float]:

    (passes12, d12) = is_passing_through(bbox1, bbox2)
    (passes21, d21) = is_passing_through(bbox2, bbox1)

    return (passes12 or passes21, (d12 + d21) / 2)

def is_point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    """
    Check if a point is inside a polygon using the ray-casting algorithm.

    :param point: The point to check (x, y).
    :param polygon: A tuple of four points representing the polygon (x, y).
    :return: True if the point is inside the polygon, False otherwise.
    """
    x, y = point.co_ordinates
    n = len(polygon)
    inside = False

    px, py = polygon[-1].co_ordinates  # Start with the last vertex
    for i in range(n):
        qx, qy = polygon[i].co_ordinates
        if ((py > y) != (qy > y)) and (x < (qx - px) * (y - py) / (qy - py) + px):
            inside = not inside
        px, py = qx, qy

    return inside

def get_point_of_intersections(
    bboxes: List[BoundingBox], endpoints: List[Point]
) -> PointOfIntersections:

    n = len(bboxes)
    points_of_intersection: PointOfIntersections = [
        [None for _ in range(n)] for _ in range(n)
    ]

    for idx1 in range(n):
        bbox1 = bboxes[idx1]
        line1 = GeometryLine(
            p=bbox1.midpoint,
            m=bbox1.approx_orientation
        )
        for idx2 in range(idx1, n):
            bbox2 = bboxes[idx2]
            line2 = GeometryLine(
                p=bbox2.midpoint,
                m=bbox2.approx_orientation
            )

            poi = line1.point_of_intersection(line2)
            if is_point_in_polygon(poi, endpoints):
                points_of_intersection[idx1][idx2] = poi
                points_of_intersection[idx2][idx1] = poi


    return points_of_intersection

def get_passthroughs(bboxes: List[BoundingBox]) -> PassThroughs:

    n = len(bboxes)

    passthroughs: PassThroughs = [
        [False for _ in range(n)] for _ in range(n)
    ]

    for idx1 in range(n):
        bbox1 = bboxes[idx1]

        for idx2 in range(idx1, n):
            bbox2 = bboxes[idx2]

            if (idx1 == idx2):
                passthroughs[idx1][idx2] = True
                continue

            (passes, _) = any_passing_through(
                bbox1, bbox2
            )
            if passes:
                passthroughs[idx1][idx2] = True
                passthroughs[idx2][idx1] = True

    return passthroughs

def sum_vertical_distances(
    bbox1: BoundingBox, bbox2: BoundingBox, poi: Point
) -> float:

    m1 = bbox1.midpoint
    m2 = bbox2.midpoint

    return abs((m1 - poi).y) + abs((m2 - poi).y)

def safe_sum_vertical_distances(
    bbox1: BoundingBox, bbox2: BoundingBox, poi: Union[Point, None]
) -> float:

    if poi is None or bbox1.idx == bbox2.idx:
        return inf
    else:
        return sum_vertical_distances(bbox1, bbox2, poi)

def get_inlines(
    bboxes: List[BoundingBox],
    pois: PointOfIntersections,
    passthroughs: PassThroughs
) -> InLines:

    n = len(bboxes)

    inlines: InLines = deepcopy(passthroughs)

    for idx in range(n):

        point_of_intersections = pois[idx]
        vertical_distances = [
            safe_sum_vertical_distances(
                bbox1=bboxes[idx],
                bbox2=bboxes[_idx],
                poi=poi
            )
            for _idx, poi in enumerate(point_of_intersections)
        ]
        argmin_idx = min(
            range(len(vertical_distances)),
            key=vertical_distances.__getitem__
        )
        min_value = vertical_distances[argmin_idx]

        bbox1, bbox2 = bboxes[idx], bboxes[argmin_idx]
        is_overlapping, percentage = bbox1.is_overlapping(bbox2)

        if min_value != inf and not (is_overlapping and percentage > 50):
            inlines[idx][argmin_idx] = True

    return inlines

def get_line(
    inlines: List[List[bool]],
    start_idx: int,
    visited: Optional[set] = None
) -> Line:

    if visited is None:
        visited = set()

    # Add the current index to the visited set
    visited.add(start_idx)

    # Get the row corresponding to the current index
    row = inlines[start_idx]

    # Iterate through the row to find connected indices
    for idx, is_true in enumerate(row):
        if is_true and idx not in visited:
            get_line(inlines, idx, visited)

    return list(visited)

def sort_lines_horizontally(lines: Lines, bboxes: List[BoundingBox]) -> Lines:

    return [
        sorted(line, key=lambda idx: bboxes[idx].midpoint.x)
        for line in lines
    ]

def vertical_score(line: Line, bboxes: List[BoundingBox]) -> float:

    n = len(line)

    _bboxes = [bboxes[idx] for idx in line]

    slopes = [bbox.approx_orientation for bbox in _bboxes]
    average_slop = sum(slopes) / n

    sum_of_midpoints = reduce(
        lambda p1, p2: p1 + p2,
        [bbox.midpoint for bbox in _bboxes]
    )
    average_midpoint = sum_of_midpoints / n

    _line = GeometryLine(
        p=average_midpoint,
        m=average_slop,
    )

    y = average_midpoint.y
    c = _line.intercept

    return (y + c) / 2


def sort_lines_vertically(lines: Lines, bboxes: List[BoundingBox]) -> Lines:

    scores = [vertical_score(line, bboxes) for line in lines]

    return [x for _, x in sorted(zip(scores, lines))]

def sort(lines, bboxes) -> Lines:

    x_sorted = sort_lines_horizontally(lines, bboxes)
    fully_sorted = sort_lines_vertically(x_sorted, bboxes)

    return fully_sorted
