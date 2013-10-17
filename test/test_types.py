"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import unittest
from test.types.geo import *

class TestTypes(unittest.TestCase):
    def testPoint(self):
        p = Point(-1, 2)
        self.assertEqual(-1, p.getX())
        self.assertEqual(2, p.getY())

    def testPointEquality(self):
        p1 = Point(1, 2)
        p2 = Point(1, 1)
        p3 = Point(2, 1)
        p4 = Point(1, 1)
        self.assertEqual(p2, p4)
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)

    # Checking that the inherited equality check works as expected.
    def testSubPointEquality(self):
        # Well, obviously it has a constructor, but no arguments.
        p1 = PointWithoutConstructor().setX(1).setY(1)
        p2 = PointWithoutConstructor().setX(1).setY(1)
        self.assertEqual(p1, p2)
        p1.setX(2)
        self.assertNotEqual(p1, p2)
        self.assertEqual(Point(1, 1), p2) # Compare with regular Point.

    def testTriangle(self):
        p1 = Point(-1, 1)
        p2 = Point(1, 1)
        p3 = Point(0, -1)
        t = Triangle(p1, p2, p3)
        self.assertEqual(p1, t.getP1())
        self.assertEqual(p2, t.getP2())
        self.assertEqual(p3, t.getP3())
        t.setP1(p2)
        self.assertEqual(p2, t.getP1())

    def testTriangleEquality(self):
        t1 = Triangle(Point(1,1), Point(2,2), Point(3,3))
        t2 = Triangle(Point(1,1), Point(2,2), Point(3,3))
        t3 = Triangle(Point(1,2), Point(2,2), Point(3,3))
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)
        self.assertNotEqual(t2, t3)
