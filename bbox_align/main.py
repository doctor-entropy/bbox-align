from math import floor

from typing import List, Tuple, Optional, Set
from .geometry import Point, Number
from .bounding_box import Coords, BoundingBox

from .relationships import (
    InLines,
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

def resolve_overlaps(bboxes: List[BoundingBox], line: Line) -> Lines:

    overlaps = get_overlaps(line, bboxes)

    if not overlaps:
        return [line]

    # Get the overlaps which have the largest height difference
    # This ensures better overlap resolution
    (idx1, idx2) = max(
        overlaps,
        key=lambda pair: abs(
            bboxes[pair[0]].midpoint.y - bboxes[pair[0]].midpoint.y
        ),
        default=(-1, -1)
    )

    if idx1 == -1 or idx2 == -1:
        raise ValueError("Could not find overalps")

    bbox1_mp, bbox2_mp = bboxes[idx1].midpoint, bboxes[idx2].midpoint

    remaining_indices = [idx for idx in line if idx not in {idx1, idx2}]

    first_line, second_line = [idx1], [idx2]
    for idx in remaining_indices:
        bbox_mp = bboxes[idx].midpoint
        if abs(bbox_mp.y - bbox1_mp.y) < abs(bbox_mp.y - bbox2_mp.y):
            first_line.append(idx)
        else:
            second_line.append(idx)

    first_line_resolved = resolve_overlaps(bboxes, first_line)
    second_line_resolved = resolve_overlaps(bboxes, second_line)

    return first_line_resolved + second_line_resolved

def get_lines(
    inlines: InLines,
    bboxes: List[BoundingBox],
) -> Lines:

    n = len(inlines)
    lines = []
    visited: Set[int] = set()

    while len(visited) < n:

        next_idx = next(idx for idx in range(n) if idx not in visited)
        line = get_line(inlines, next_idx)
        overlaps = get_overlaps(line, bboxes)

        if overlaps:
            resolved_lines = resolve_overlaps(bboxes, line)
            lines.extend(resolved_lines)
        else:
            lines.append(line)

        visited.update(line)

    return lines

def process(
    vertices: BBoxVertices,
    endpoints: List[Tuple[Number, Number]],
):

    bboxes = [
        to_bbox_object(vertex, idx)
        for idx, vertex in enumerate(vertices)
    ]

    _endpoints = [Point(*point) for point in endpoints]

    pois = get_point_of_intersections(bboxes, _endpoints)
    passthroughs = passthroughs = get_passthroughs(bboxes, 1)

    inlines = get_inlines(bboxes, pois, passthroughs)

    lines = get_lines(inlines, bboxes)

    return lines
