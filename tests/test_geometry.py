import pytest
from bbox_align.geometry import Point, Line


def test_point_constructor():
    p = Point(3, 4)
    assert p.x == 3
    assert p.y == 4
    assert p.co_ordinates == (3, 4)

def test_point_equality():
    p1 = Point(3, 4)
    p2 = Point(3, 4)
    p3 = Point(5, 6)
    assert p1 == p2
    assert p1 != p3

def test_point_addition():
    p1 = Point(3, 4)
    p2 = Point(1, 2)
    result = p1 + p2
    assert result == Point(4, 6)

def test_point_subtraction():
    p1 = Point(3, 4)
    p2 = Point(1, 2)
    result = p1 - p2
    assert result == Point(2, 2)

def test_point_floordiv():
    p = Point(6, 8)
    result = p // 2
    assert result == Point(3, 4)

def test_point_truediv():
    p = Point(6, 8)
    result = p / 2
    assert result == Point(3.0, 4.0)

def test_point_is_above():
    p1 = Point(3, 4)
    p2 = Point(3, 2)
    assert p1.is_above(p2)
    assert not p2.is_above(p1)

def test_point_is_below():
    p1 = Point(3, 4)
    p2 = Point(3, 2)
    assert p2.is_below(p1)
    assert not p1.is_below(p2)

def test_point_is_left_of():
    p1 = Point(3, 4)
    p2 = Point(5, 4)
    assert p1.is_left_of(p2)
    assert not p2.is_left_of(p1)

def test_point_is_right_of():
    p1 = Point(3, 4)
    p2 = Point(5, 4)
    assert p2.is_right_of(p1)
    assert not p1.is_right_of(p2)

def test_point_slope_wrt():
    p1 = Point(3, 4)
    p2 = Point(6, 8)
    assert p2.slope_wrt(p1) == pytest.approx(4 / 3)
    p3 = Point(3, 8)
    assert p3.slope_wrt(p1) == pytest.approx(float('inf'))

def test_point_distance_to_point():
    p1 = Point(3, 4)
    p2 = Point(6, 8)
    assert p1.distance_to_point(p2) == pytest.approx(5.0)

def test_point_distance_to_line():
    p = Point(3, 4)
    l = Line(Point(0, 0), 1)  # y = x
    assert p.distance_to_line(l) == pytest.approx(0.7071, rel=1e-3)

def test_point_reflect_on_line():
    p = Point(3, 4)
    l = Line(Point(0, 0), 1)  # y = x
    reflected = p.reflect_on_line(l)
    assert reflected == Point(4, 3)

def test_line_constructor():
    p = Point(0, 0)
    l = Line(p, 1)  # y = x
    assert l.standard_form_coeffs == (1, -1, 0)

def test_line_find_x():
    l = Line(Point(0, 0), 1)  # y = x
    assert l.find_x(5) == pytest.approx(5)

def test_line_find_y():
    l = Line(Point(0, 0), 1)  # y = x
    assert l.find_y(5) == pytest.approx(5)

def test_line_point_position():
    l = Line(Point(0, 0), 1)  # y = x
    p = Point(3, 4)
    assert l.point_position(p) == pytest.approx(-1)

def test_line_point_of_intersection():
    l1 = Line(Point(0, 0), 1)  # y = x
    l2 = Line(Point(0, 1), -1)  # y = -x + 1
    intersection = l1.point_of_intersection(l2)
    assert intersection == Point(0.5, 0.5)

def test_line_reflect_point():
    l = Line(Point(0, 0), 1)  # y = x
    p = Point(3, 4)
    reflected = l.reflect_point(p)
    assert reflected == Point(4, 3)
