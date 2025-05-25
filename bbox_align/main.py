import json
from copy import deepcopy
from math import radians, tan, inf

from typing import List, Tuple, Optional, Union
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

PointOfIntersections = List[
    List[Union[Point, None]]
]

PassThroughs = List[
    List[bool]
]

InLines = List[
    List[bool]
]


def to_bbox_object(bbox: Vertices) -> BoundingBox:

    return BoundingBox(
        p1=bbox[0],
        p2=bbox[1],
        p3=bbox[2],
        p4=bbox[3],
        idx=bbox[4],
    )

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
    l1 = Line(bbox1.midpoint, bbox1.approx_orientation)
    d = l1.distance_to_point(bbox2.midpoint)
    is_inline = d <= bbox2.average_height/2

    return (is_inline, d)

'''
Two boxes - box1 and box2 are said to passthrough
if the line passing through the midpoint of box1
and the perpendicular distance from the midpoint
of box2 is less than half of average height of the latter.
In other words the line passes through the second boundingbox
'''
def any_passing_through(bbox1: BoundingBox, bbox2: BoundingBox) -> Tuple[bool, float]:

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

def get_pois_and_passthroughs(
    bboxes: List[BoundingBox], endpoints: List[Point]
) -> Tuple[PointOfIntersections, PassThroughs]:

    n = len(bboxes)
    points_of_intersection: PointOfIntersections = [
        [None for _ in range(n)] for _ in range(n)
    ]
    passthroughs: PassThroughs = [
        [False for _ in range(n)] for _ in range(n)
    ]

    for idx1 in range(n):
        bbox1 = bboxes[idx1]
        line1 = Line(
            p=bbox1.midpoint,
            m=bbox1.approx_orientation
        )
        for idx2 in range(idx1, n):
            bbox2 = bboxes[idx2]
            line2 = Line(
                p=bbox2.midpoint,
                m=bbox2.approx_orientation
            )

            if (idx1 == idx2):
                continue

            poi = line1.point_of_intersection(line2)
            if is_point_in_polygon(poi, endpoints):
                points_of_intersection[idx1][idx2] = poi
                points_of_intersection[idx2][idx1] = poi

            (passes, _) = any_passing_through(bbox1, bbox2)
            if passes:
                passthroughs[idx1][idx2] = True
                passthroughs[idx2][idx1] = True


    return points_of_intersection, passthroughs

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
        if min_value != inf:
            inlines[idx][argmin_idx] = True

    return inlines

def process(
    vertices: BBoxVertices,
    words: Optional[List[str]],
    endpoints: List[Tuple[Number, Number]],
):

    bboxes = [
        to_bbox_object(vertex)
        for vertex in vertices
    ]

    _endpoints = [Point(*point) for point in endpoints]
    pois, passthroughs = get_pois_and_passthroughs(
        bboxes, _endpoints
    )

    inlines = get_inlines(bboxes, pois, passthroughs)
    print(inlines)
    # print(pois)
    # print(passthroughs)

    # inlines = vertical_distances(bboxes, pois)
    # print(inlines)

    # lines = group_in_lines(bboxes)

    # if words:
    #     for line in lines:
    #         wrds = [words[bbox.idx] for bbox in line]
    #         print(' '.join(wrds))


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
