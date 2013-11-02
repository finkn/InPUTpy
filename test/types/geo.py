"""
geo.py

This module (test.types.geo) exports classes that represent various
types of geometrical objects, such as points and rectangles. They are
intended as tools for testing code mappings.

While the testing classes in the model package of the testing project
from InPUT4j have been ported to allow the ported API tests to run, these
objects were created in addition to those. Having objects that represent
actual concepts, with meaningful names and meaningful parameters, seemed
to make them easier to understand and thus more useful.
"""

__all__ = (
    'Point', 'DoublePoint',
    'PointWithoutConstructor', 'PointWithoutAccessors',
    'PointWithCustomAccessors', 'PointWithCustomAccessorsNoConstructor',
    'Triangle', 'TriangleWithoutConstructor', 'TriangleWithCustomAccessors',
)

class Point:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def getX(self): return self.__x
    def getY(self): return self.__y
    def setX(self, x): self.__x = x; return self
    def setY(self, y): self.__y = y; return self

    def __str__(self):
        return '(%s,%s)' % (self.__x, self.__y)
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__x == other.__x and self.__y == other.__y

class PointWithoutConstructor(Point):
    def __init__(self):
        Point.__init__(self, None, None)

class PointWithoutAccessors(Point):
    # Redefine get and set methods to make sure the default accessors
    # are not called.
    def getX(*args): raise NotImplementedError('No default accessors.')
    def getY(*args): raise NotImplementedError('No default accessors.')
    def setX(*args): raise NotImplementedError('No default accessors.')
    def setY(*args): raise NotImplementedError('No default accessors.')

class PointWithCustomAccessors(PointWithoutAccessors):
    def customXGetter(self): return Point.getX(self)
    def customYGetter(self): return Point.getY(self)
    def customXSetter(self, n): return Point.setX(self, n)
    def customYSetter(self, n): return Point.setY(self, n)

class PointWithCustomAccessorsNoConstructor(PointWithCustomAccessors):
    def __init__(self):
        Point.__init__(self, None, None)

class DoublePoint(Point):
    def __init__(self, x, y):
        Point.__init__(self, x*2, y*2)

class Shape:
    def __init__(self, *args):
        self.points = [p for p in args]

    def getPoint(self, index):
        return self.points[index]

    def setPoint(self, index, point):
        self.points[index] = point
        return self

    def __str__(self):
        return str(self.points)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Shape):
            return False
        if self.points != other.points:
            return False
        return True


class Triangle(Shape):
    def __init__(self, p1, p2, p3):
        Shape.__init__(self, p1, p2, p3)

    def getP1(self): return Shape.getPoint(self, 0)
    def getP2(self): return Shape.getPoint(self, 1)
    def getP3(self): return Shape.getPoint(self, 2)
    def setP1(self, p): return Shape.setPoint(self, 0, p)
    def setP2(self, p): return Shape.setPoint(self, 1, p)
    def setP3(self, p): return Shape.setPoint(self, 2, p)

    def __str__(self):
        return '(%s,%s,%s)' % (self.getP1(), self.getP2(), self.getP3())
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.points[0] == other.points[0] and
            self.points[1] == other.points[1] and
            self.points[2] == other.points[2])

class TriangleWithoutConstructor(Triangle):
    def __init__(self):
        Triangle.__init__(self, None, None, None)

class TriangleWithCustomAccessors(Triangle):
    def __init__(self):
        Triangle.__init__(self, None, None, None)

    # Redefine get and set methods to make sure the default accessors
    # are not called.
    def customP1Getter(self): return Shape.getPoint(self, 0)
    def customP2Getter(self): return Shape.getPoint(self, 1)
    def customP3Getter(self): return Shape.getPoint(self, 2)
    def customP1Setter(self, p): return Shape.setPoint(self, 0, p)
    def customP2Setter(self, p): return Shape.setPoint(self, 1, p)
    def customP3Setter(self, p): return Shape.setPoint(self, 2, p)

    def getP1(*args): raise NotImplementedError('No default accessors.')
    def getP2(*args): raise NotImplementedError('No default accessors.')
    def getP3(*args): raise NotImplementedError('No default accessors.')
    def setP1(*args): raise NotImplementedError('No default accessors.')
    def setP2(*args): raise NotImplementedError('No default accessors.')
    def setP3(*args): raise NotImplementedError('No default accessors.')


class Rectangle(Shape):
    def __init__(self, topLeft, width, height):
        topRight = Point(topLeft.getX() + width, topLeft.getY())
        botRight = Point(topLeft.getX() + width, topLeft.getY() - height)
        botLeft = Point(topLeft.getX(), topLeft.getY() - height)
        Shape.__init__(self, topLeft, topRight, botRight, botLeft)

class Square(Rectangle):
    def __init__(self, topLeft, side):
        Rectangle.__init__(self, topLeft, side, side)
