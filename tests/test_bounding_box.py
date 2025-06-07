import pytest
from bbox_align.bounding_box import BoundingBox
from bbox_align.geometry import Point


def test_bounding_box_constructor():
    bbox = BoundingBox((0, 0), (4, 0), (4, 3), (0, 3), idx=1)
    assert bbox.p1 == Point(0, 0)
    assert bbox.p2 == Point(4, 0)
    assert bbox.p3 == Point(4, 3)
    assert bbox.p4 == Point(0, 3)
    assert bbox.idx == 1
    assert bbox.midpoint == Point(2, 1.5)
    assert bbox.approx_orientation == pytest.approx(0.0)
    assert bbox.average_height == pytest.approx(3.0)
    assert bbox.average_width == pytest.approx(4.0)


def test_bounding_box_lt():
    bbox1 = BoundingBox((0, 0), (4, 0), (4, 3), (0, 3), idx=1)
    bbox2 = BoundingBox((5, 0), (9, 0), (9, 3), (5, 3), idx=2)
    assert bbox1 < bbox2
    assert not bbox2 < bbox1


def test_bounding_box_str():
    bbox = BoundingBox((0, 0), (4, 0), (4, 3), (0, 3), idx=1)
    expected_str = "(0, 0), (4, 0)\n(0, 3), (4, 3)"
    assert str(bbox) == expected_str


def test_bounding_box_properties():
    bbox = BoundingBox((0, 0), (4, 0), (4, 3), (0, 3), idx=1)
    assert bbox.p1 == Point(0, 0)
    assert bbox.p2 == Point(4, 0)
    assert bbox.p3 == Point(4, 3)
    assert bbox.p4 == Point(0, 3)
    assert bbox.midpoint == Point(2, 1.5)
    assert bbox.approx_orientation == pytest.approx(0.0)
    assert bbox.average_height == pytest.approx(3.0)
    assert bbox.average_width == pytest.approx(4.0)


def test_bounding_box_is_overlapping():
    bbox1 = BoundingBox((0, 0), (4, 0), (4, 3), (0, 3), idx=1)
    bbox2 = BoundingBox((3, 0), (7, 0), (7, 3), (3, 3), idx=2)
    bbox3 = BoundingBox((5, 0), (9, 0), (9, 3), (5, 3), idx=3)

    overlap1, percentage1 = bbox1.is_overlapping(bbox2)
    assert overlap1 is True
    assert percentage1 == pytest.approx(25.0)

    overlap2, percentage2 = bbox1.is_overlapping(bbox3)
    assert overlap2 is False
    assert percentage2 == pytest.approx(0.0)