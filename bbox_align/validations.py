from .types import BBoxes, BBox
from .geometry import Point


def check_user_inputs(bounding_boxes: BBoxes, boundaries: BBox):

    if not isinstance(bounding_boxes, list) or not all(
        isinstance(bbox, list) and len(bbox) == 4 for bbox in bounding_boxes
    ):
        raise ValueError("bounding_boxes must be a list of 4-point lists.")

    if not isinstance(boundaries, list) or not len(boundaries) == 4:
        raise ValueError("boundaries must be a list of 4-points")

    # Validate the orientation of each bounding box
    for idx, bbox in enumerate(bounding_boxes):
        p1, p2, p3, p4 = bbox
        if not (
            Point(*p1).is_left_of(Point(*p2)) and
            Point(*p2).is_below(Point(*p3)) and
            Point(*p3).is_right_of(Point(*p4)) and
            Point(*p4).is_above(Point(*p1))
        ):
            raise ValueError(
                f"Bounding box at index {idx} has invalid orientation. "
                f"Points must be in clockwise order: "
                f"top-left (p1), top-right (p2), bottom-right (p3), bottom-left (p4). "
                f"Provided points: p1={p1}, p2={p2}, p3={p3}, p4={p4}"
            )

    p1, p2, p3, p4 = boundaries
    if not (
        Point(*p1).is_left_of(Point(*p2)) and
        Point(*p2).is_below(Point(*p3)) and
        Point(*p3).is_right_of(Point(*p4)) and
        Point(*p4).is_above(Point(*p1))
    ):
        raise ValueError(
            f"boundaries has invalid orientation. "
            f"Points must be in clockwise order: "
            f"top-left (p1), top-right (p2), bottom-right (p3), bottom-left (p4). "
            f"Provided points: p1={p1}, p2={p2}, p3={p3}, p4={p4}"
        )
