import json

from typing import List, Tuple, Optional, Set
from geometry import Point, Number
from bounding_box import Coords, BoundingBox

from utils import subarray
from relationships import (
    get_point_of_intersections,
    get_passthroughs,
    get_inlines,
    get_line,
    InLines,
    PointOfIntersections,
    Line
)

Vertices = Tuple[
    Coords,
    Coords,
    Coords,
    Coords,
    Optional[int],
]

BBoxVertices = List[Vertices]

Lines = List[Line]


def to_bbox_object(bbox: Vertices) -> BoundingBox:

    return BoundingBox(
        p1=bbox[0],
        p2=bbox[1],
        p3=bbox[2],
        p4=bbox[3],
        idx=bbox[4],
    )


def get_overlaps(
    line: List[int], bboxes: List[BoundingBox]
) -> List[Tuple[int, int]]:

    overlaps = []

    for i in range(len(line)):
        for j in range(i + 1, len(line)):
            bbox1 = bboxes[line[i]]
            bbox2 = bboxes[line[j]]
            is_overlapping, percentage = bbox1.is_overlapping(bbox2)
            if is_overlapping and percentage > 50:
                overlaps.append((line[i], line[j]))

    return overlaps

def resolve_overlaps(
    bboxes: List[BoundingBox], line: List[int], pois, tolerance
) -> Lines:

    bboxes_subset = [bboxes[idx] for idx in line]
    new_passthroughs = get_passthroughs(bboxes_subset, tolerance)

    new_inlines = get_inlines(
        bboxes_subset,
        pois,
        new_passthroughs
    )
    non_overlap_lines = get_lines(
        new_inlines,
        bboxes_subset,
        pois,
        tolerance
    )

    for i, new_line in enumerate(non_overlap_lines):
        for j, idx in enumerate(new_line):
            non_overlap_lines[i][j] = line[idx]

    return non_overlap_lines

def get_lines(
    inlines: InLines,
    bboxes: List[BoundingBox],
    pois: PointOfIntersections,
    tolerance: float
) -> Lines:

    n = len(inlines)
    lines = []
    visited: Set[int] = set()

    while len(visited) < n:

        next_idx = next(idx for idx in range(n) if idx not in visited)
        line = get_line(inlines, next_idx)
        overlaps = get_overlaps(line, bboxes)

        if overlaps:
            pois_subarray = subarray(pois, line)
            resolved_lines = resolve_overlaps(
                bboxes=bboxes,
                line=line,
                pois=pois_subarray,
                tolerance=tolerance - 0.05
            )
            lines.extend(resolved_lines)
        else:
            lines.append(line)

        visited.update(line)

    return lines

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

    pois = get_point_of_intersections(bboxes, _endpoints)
    passthroughs = passthroughs = get_passthroughs(bboxes, 1)

    inlines = get_inlines(bboxes, pois, passthroughs)

    # from copy import deepcopy
    # print_inlines = deepcopy(inlines)
    # for idx, i in enumerate(print_inlines):
    #     print_inlines[idx] = [words[idx]] + print_inlines[idx]
    # print_inlines = [[' '] + words] + print_inlines
    # print(print_inlines)
    # print_matrix(print_inlines)

    lines = get_lines(inlines, bboxes, pois, 1.0)
    print(lines)

    if words:
        for line in lines:
            wrds = [words[idx] for idx in line]
            print(' '.join(wrds))


if __name__ == "__main__":

    data_path = '../datasets/1018-new-google-api.json'

    with open(data_path, 'r') as j:
        annotations = json.load(j)

    ocr_text = annotations['textAnnotations']
    bounding_boxes_annotation = ocr_text[1::]

    # idxs_to_inlcude = [66, 67, 55, 56, 57, 58, 59]
    # bounding_boxes_annotation = [bounding_boxes_annotation[i] for i in idxs_to_inlcude]

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

    # process(vertices, words, [(0, 0), (670, 0), (670, 1000), (0, 1000)])
    process(vertices, words, [(125, 0), (750, 0), (750, 1000), (0, 1000)])
