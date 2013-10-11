import unittest
from test.types.geo import Point
from test.types.geo import Triangle

class TestTypes(unittest.TestCase):
    def testPoint(self):
        p = Point(-1, 2)
        self.assertEqual(-1, p.getX())
        self.assertEqual(2, p.getY())

    def testTriangle(self):
        p1 = Point(-1, 1)
        p2 = Point(1, 1)
        p3 = Point(0, -1)
        r = Triangle(p1, p2, p3)
