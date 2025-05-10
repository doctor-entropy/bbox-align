import os
import json
from math import radians, tan

from copy import copy

from typing import List, Tuple
from geometry import Line
from bounding_box import Coords, BoundingBox


SLOPE_TOLERANCE_IN_DEGREES = 3
SLOPE_TOLERANCE = tan(radians(SLOPE_TOLERANCE_IN_DEGREES))

Vertices = Tuple[
    Coords,
    Coords,
    Coords,
    Coords
]

BBoxVertices = List[Vertices]


def to_bbox_object(bbox: Vertices) -> BoundingBox:

    return BoundingBox(
        p1=bbox[0],
        p2=bbox[1],
        p3=bbox[2],
        p4=bbox[3],
        word=bbox[4],
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

    lines = []

    for bbox in bboxes:
        line_number = None
        for idx, line in enumerate(lines):
            if bbox_is_in_line(bbox, line):
                line_number = idx

        if line_number:
            lines[line_number].append(bbox)
        else:
            lines.append([bbox])

    return lines

def process(vertices: BBoxVertices):

    bboxes = list(map(
        lambda bbox: to_bbox_object(bbox),
        vertices
    ))

    lines = group_in_lines(bboxes)

    for line in lines:
        words = [bbox.word for bbox in line]
        print(' '.join(words))


if __name__ == "__main__":

    data_path = '../datasets/1000-receipt_ocr.json'

    with open(data_path, 'r') as j:
        annotations = json.load(j)

    ocr_text = annotations['ocr_text']
    bounding_boxes_annotation = ocr_text[1:3]

    def vertices_to_tuples(verts, word):

        return (
            (verts[0]['x'], verts[0]['y']),
            (verts[1]['x'], verts[1]['y']),
            (verts[2]['x'], verts[2]['y']),
            (verts[3]['x'], verts[3]['y']),
            word,
        )


    vertices: BBoxVertices = list(map(
        lambda x: vertices_to_tuples(
            x['boundingPoly']['vertices'],
            x['description']
        ),
        bounding_boxes_annotation
    ))

    process(vertices)
