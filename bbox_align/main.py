import os
import json

from typing import List, Tuple
from bounding_box import Coords, BoundingBox


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
    )


def process(bounding_boxes: BBoxVertices):

    bboxes = map(
        lambda bbox: to_bbox_object(bbox),
        bounding_boxes
    )

    for bbox in list(bboxes):
        print(bbox)
        print()


if __name__ == "__main__":

    data_path = '../datasets/1000-receipt_ocr.json'

    with open(data_path, 'r') as j:
        annotations = json.load(j)

    ocr_text = annotations['ocr_text']
    bounding_boxes_annotation = ocr_text[1::]

    def vertices_to_tuples(verts):

        return (
            (verts[0]['x'], verts[0]['y']),
            (verts[1]['x'], verts[1]['y']),
            (verts[2]['x'], verts[2]['y']),
            (verts[3]['x'], verts[3]['y'])
        )


    vertices: BBoxVertices = list(map(
        lambda x: vertices_to_tuples(
            x['boundingPoly']['vertices']
        ),
        bounding_boxes_annotation
    ))

    process(vertices)
