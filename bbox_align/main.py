import os
import json
from math import radians, tan, inf

from collections import namedtuple

from typing import List, Tuple, Optional
from geometry import Line, Point, Number
from bounding_box import Coords, BoundingBox


SLOPE_TOLERANCE_IN_DEGREES = 3
SLOPE_TOLERANCE = tan(radians(SLOPE_TOLERANCE_IN_DEGREES))

Vertices = Tuple[
    Coords,
    Coords,
    Coords,
    Coords,
    Optional[int],
]

BBoxVertices = List[Vertices]

LineOfBBoxes = List[BoundingBox]


def to_bbox_object(bbox: Vertices) -> BoundingBox:

    return BoundingBox(
        p1=bbox[0],
        p2=bbox[1],
        p3=bbox[2],
        p4=bbox[3],
        idx=bbox[4],
    )

'''
Two boxes - box1 and box2 are said to be parallel
if the line passing through the midpoint of box1
and the perpendicular distance from the midpoint
of box2 is less than half of average height of the latter.
In other words the line passes through the second boundingbox
'''
def _parallel(bbox1: BoundingBox, bbox2: BoundingBox):

    l = Line(bbox1.midpoint, bbox1.approx_orientation)
    d = l.distance_to_point(bbox2.midpoint)

    return d <= bbox2.average_height/2

def parallel(bbox1, bbox2):

    return any((
        _parallel(bbox1, bbox2),
        _parallel(bbox2, bbox1)
    ))

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
def is_inline(rect1: BoundingBox, rect2:  BoundingBox):

    m1 = rect1.approx_orientation
    m2 = rect2.approx_orientation

    # comparing boxes that are of same orientation
    # else they MAY not be in the same line
    # skewed boxes (due to folds, crinkles) are addressed
    # in the next step
    if  abs(m1 - m2) <= SLOPE_TOLERANCE and \
        parallel(rect1, rect2):
        # if the line passes through the rectangle
        # then we assume that the boxes are parallel
        # to eachother and hence in the same line
        return True
    else:
        return False

def bbox_is_in_line(bbox: BoundingBox, line: List[BoundingBox]) -> bool:

    return any(
        is_inline(bbox, bbox2)
        for bbox2 in line
    )

def group_in_lines(bboxes: List[BoundingBox]):

    lines: List[LineOfBBoxes] = []

    for bbox in bboxes:
        for line in lines:
            if bbox_is_in_line(bbox, line):
                line.append(bbox)
                break
        else:
            # No line found, create a new one
            lines.append([bbox])

    return lines

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
):

    n = len(bboxes)
    points_of_intersection = [[None for _ in range(n)] for _ in range(n)]

    for bbox1 in bboxes:
        idx1 = bbox1.idx
        line1 = Line(
            p=bbox1.midpoint,
            m=bbox1.approx_orientation
        )
        for bbox2 in bboxes:
            idx2 = bbox2.idx
            line2 = Line(
                p=bbox2.midpoint,
                m=bbox2.approx_orientation
            )

            if (idx1 == idx2):
                continue

            poi = line1.point_of_intersection(line2)
            print(poi)
            if is_point_in_polygon(poi, endpoints):
                points_of_intersection[idx1][idx2] = poi

    return points_of_intersection


def process(
    vertices: BBoxVertices,
    words: Optional[List[str]],
    endpoints: List[Tuple[Number, Number]],
):

    bboxes = [
        to_bbox_object(vertex)
        for vertex in vertices
    ]

    endpoints = [Point(*point) for point in endpoints]
    pois = get_point_of_intersections(bboxes, endpoints)

    lines = group_in_lines(bboxes)

    if words:
        for line in lines:
            wrds = [words[bbox.idx] for bbox in line]
            print(' '.join(wrds))


if __name__ == "__main__":

    data_path = '../datasets/1018-receipt_ocr.json'

    with open(data_path, 'r') as j:
        annotations = json.load(j)

    ocr_text = annotations['ocr_text']
    bounding_boxes_annotation = ocr_text[1::]

    def vertices_to_tuples(verts, idx: int):

        return (
            (verts[0]['x'], verts[0]['y']),
            (verts[1]['x'], verts[1]['y']),
            (verts[2]['x'], verts[2]['y']),
            (verts[3]['x'], verts[3]['y']),
            idx,
        )

    vertices: BBoxVertices = [
        vertices_to_tuples(x['boundingPoly']['vertices'], idx)
        for idx, x in enumerate(bounding_boxes_annotation)
    ]

    words = [x['description'] for x in bounding_boxes_annotation]

    process(vertices, words, [(0, 0), (670, 0), (670, 1000), (0, 1000)])
