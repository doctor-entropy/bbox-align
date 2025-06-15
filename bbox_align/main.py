from math import floor
from itertools import combinations

from typing import List, Tuple, Optional, Set, Literal
from .geometry import Point, Number
from .bounding_box import Coords, BoundingBox

from .relationships import (
    InLines,
    Line,
    PassThroughs,
    PointOfIntersections,
    get_point_of_intersections,
    get_passthroughs,
    get_inlines,
    get_line,
)

from .utils import subarray

Vertices = Tuple[
    Coords,
    Coords,
    Coords,
    Coords,
    Optional[int],
]

BBoxVertices = List[Vertices]

Lines = List[Line]

OverlapResolutionType = Literal[
    'group_by_distance',
    'reduce_tolerance'
]

ITERATION_STEP = 0.1
MAX_ITERATIONS = int(
    floor(1 / ITERATION_STEP)
)


def to_bbox_object(vertices: Vertices, idx: int) -> BoundingBox:

    return BoundingBox(
        p1=vertices[0],
        p2=vertices[1],
        p3=vertices[2],
        p4=vertices[3],
        idx=idx,
    )

def bboxes_overlapping(bbox1: BoundingBox, bbox2: BoundingBox) -> bool:
    is_overlapping, percentage = bbox1.is_overlapping(bbox2)
    return is_overlapping and percentage > 50

def has_any_overlap(line: List[int], bboxes: List[BoundingBox]) -> bool:

    return any(
        bboxes_overlapping(bboxes[line[i]], bboxes[line[j]])
        for i in range(len(line))
        for j in range(i + 1, len(line))
    )

def get_overlaps(
    line: List[int], bboxes: List[BoundingBox]
) -> List[Tuple[int, int]]:

    overlaps = []

    for i in range(len(line)):
        for j in range(i + 1, len(line)):
            bbox1 = bboxes[line[i]]
            bbox2 = bboxes[line[j]]
            if bboxes_overlapping(bbox1, bbox2):
                overlaps.append((line[i], line[j]))

    return overlaps

def resolve_overlaps(bboxes: List[BoundingBox], line: Line) -> Lines:

    if not has_any_overlap(line, bboxes):
        return [line]

    overlaps = get_overlaps(line, bboxes)

    # Get the overlaps which have the largest height difference
    # This ensures better overlap resolution
    (idx1, idx2) = max(
        overlaps,
        key=lambda pair: abs(
            bboxes[pair[0]].midpoint.y - bboxes[pair[0]].midpoint.y
        ),
        default=(-1, -1) # Just for static type check
    )

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

def resolve_overlaps_by_reducing_tolerance(
    bboxes: List[BoundingBox],
    line: List[int],
    pois: PointOfIntersections,
    n_iter: int,
) -> Lines:

    if not (n_iter <= MAX_ITERATIONS):
        return []

    bboxes_subset = [bboxes[idx] for idx in line]
    new_tolerance = 1.0 - (n_iter * ITERATION_STEP)
    new_passthroughs = get_passthroughs(bboxes_subset, new_tolerance)

    new_inlines = get_inlines(
        bboxes_subset,
        pois,
        new_passthroughs
    )
    non_overlap_lines = get_lines(
        new_inlines,
        bboxes_subset,
        pois,
        'reduce_tolerance',
        n_iter + 1,
    )

    for i, non_overlap_line in enumerate(non_overlap_lines):
        for j, idx in enumerate(non_overlap_line):
            non_overlap_lines[i][j] = line[idx]

    return non_overlap_lines

# Update inlines by pass-by-reference
def update_inlines(inlines: InLines, line: Line, resolved_lines: Lines):

    overlap_indices = combinations(line, 2)
    for (idx1, idx2) in overlap_indices:
        inlines[idx1][idx2] = False
        inlines[idx2][idx2] = False

    for resolved_line in resolved_lines:
        resolved_indices = combinations(resolved_line, 2)
        for (idx1, idx2) in resolved_indices:
            inlines[idx1][idx2] = True
            inlines[idx2][idx1] = True

def get_lines(
    inlines: InLines,
    bboxes: List[BoundingBox],
    pois: PointOfIntersections,
    resolution_type: OverlapResolutionType,
    n_iter: int = 0,
) -> Lines:

    n = len(inlines)
    lines = []
    visited: Set[int] = set()

    while len(visited) < n:

        next_idx = next(idx for idx in range(n) if idx not in visited)
        line = get_line(inlines, next_idx)

        if has_any_overlap(line, bboxes) and resolution_type == 'reduce_tolerance':
            pois_subarray = subarray(pois, line)
            resolved_lines = resolve_overlaps_by_reducing_tolerance(
                bboxes=bboxes,
                line=line,
                pois=pois_subarray,
                n_iter=n_iter,
            )
            if not resolved_lines:
                if n_iter == 0:
                    resolved_lines = resolve_overlaps(bboxes, line)
                    # Update inlines as pass-by-reference
                    update_inlines(inlines, line, resolved_lines)
                    lines.extend(resolved_lines)
                else:
                    return []
            else:
                lines.extend(resolved_lines)
        elif has_any_overlap(line, bboxes) and resolution_type == 'group_by_distance':
            resolved_lines = resolve_overlaps(bboxes, line)
            # Update inlines as pass-by-reference
            update_inlines(inlines, line, resolved_lines)
            lines.extend(resolved_lines)
        else:
            lines.append(line)

        visited.update(line)

    return lines

def process_with_meta_info(
    vertices: BBoxVertices,
    boundaries: List[Tuple[Number, Number]],
    overlap_resolution_type: OverlapResolutionType,
) -> Tuple[Lines, InLines, PassThroughs, PointOfIntersections]:

    bboxes = [
        to_bbox_object(vertex, idx)
        for idx, vertex in enumerate(vertices)
    ]

    _boundaries = [Point(*point) for point in boundaries]

    pois = get_point_of_intersections(bboxes, _boundaries)
    passthroughs = passthroughs = get_passthroughs(bboxes, 1)

    inlines = get_inlines(bboxes, pois, passthroughs)

    # inlines will get updated by pass-by-reference
    # in this step when resolving overalps in a line
    lines = get_lines(inlines, bboxes, pois, overlap_resolution_type)

    return lines, inlines, passthroughs, pois

def process(
    vertices: BBoxVertices,
    boundaries: List[Tuple[Number, Number]],
    overlap_resolution_type: OverlapResolutionType,
) -> Lines:

    line, _, _, _ = process_with_meta_info(
        vertices, boundaries, overlap_resolution_type
    )

    return line