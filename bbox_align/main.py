from typing import List, Tuple, Optional, Set
from .geometry import Point, Number
from .bounding_box import Coords, BoundingBox

from .utils import subarray
from .relationships import (
    InLines,
    PointOfIntersections,
    Line,
    get_point_of_intersections,
    get_passthroughs,
    get_inlines,
    get_line,
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


def to_bbox_object(vertices: Vertices, idx: int) -> BoundingBox:

    return BoundingBox(
        p1=vertices[0],
        p2=vertices[1],
        p3=vertices[2],
        p4=vertices[3],
        idx=idx,
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
    bboxes: List[BoundingBox], line: List[int], pois, tolerance, words
) -> Lines:

    if tolerance < 0.0:
        return []

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
        tolerance,
        words
    )

    for i, new_line in enumerate(non_overlap_lines):
        for j, idx in enumerate(new_line):
            non_overlap_lines[i][j] = line[idx]

    return non_overlap_lines

def get_lines(
    inlines: InLines,
    bboxes: List[BoundingBox],
    pois: PointOfIntersections,
    tolerance: float,
    words
) -> Lines:

    tolerance = round(tolerance, 2)

    n = len(inlines)
    lines = []
    visited: Set[int] = set()

    while len(visited) < n:

        next_idx = next(idx for idx in range(n) if idx not in visited)
        line = get_line(inlines, next_idx)
        overlaps = get_overlaps(line, bboxes)

        if overlaps:
            sub_words = [words[idx] for idx in line]
            pois_subarray = subarray(pois, line)
            resolved_lines = resolve_overlaps(
                bboxes=bboxes,
                line=line,
                pois=pois_subarray,
                tolerance=tolerance - 0.1,
                words=sub_words
            )

            if not resolved_lines:
                if tolerance == 1.0:
                    lines.append(line)
                else:
                    return []
            else:
                lines.extend(resolved_lines)

        else:
            lines.append(line)

        visited.update(line)

    return lines

def process(
    vertices: BBoxVertices,
    endpoints: List[Tuple[Number, Number]],
    words
):

    bboxes = [
        to_bbox_object(vertex, idx)
        for idx, vertex in enumerate(vertices)
    ]

    _endpoints = [Point(*point) for point in endpoints]

    pois = get_point_of_intersections(bboxes, _endpoints)
    passthroughs = passthroughs = get_passthroughs(bboxes, 1)

    inlines = get_inlines(bboxes, pois, passthroughs)

    lines = get_lines(inlines, bboxes, pois, 1.0, words)

    return lines
