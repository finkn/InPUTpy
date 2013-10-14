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
    'Point', 'PointWithoutConstructor', 'Triangle',
    'TriangleWithoutConstructor',
)

class Point:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def getX(self): return self.__x
    def getY(self): return self.__y
    def setX(self, x): self.__x = x
    def setY(self, y): self.__y = y

    def __str__(self):
        return '(%i,%i)' % (self.__x, self.__y)
    def __repr__(self):
        return self.__str__()

class PointWithoutConstructor(Point):
    def __init__(self):
        Point.__init__(self, None, None)

class Triangle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def getP1(self): return self.p1
    def getP2(self): return self.p2
    def getP3(self): return self.p3
    def setP1(self, p): self.p1 = p
    def setP2(self, p): self.p2 = p
    def setP3(self, p): self.p3 = p

    def __str__(self):
        return '(%s,%s,%s)' % (self.p1, self.p2, self.p3)
    def __repr__(self):
        return self.__str__()

class TriangleWithoutConstructor(Triangle):
    def __init__(self):
        Triangle.__init__(self, None, None, None)

class TriangleWithCustomAccessors(Triangle):
    def __init__(self):
        Triangle.__init__(self, None, None, None)

    # Redefine get and set methods to make sure the default accessors
    # are not called.
    def customP1Getter(self): return self.p1
    def customP2Getter(self): return self.p2
    def customP3Getter(self): return self.p3
    def customP1Setter(self, p): self.p1 = p
    def customP2Setter(self, p): self.p2 = p
    def customP3Setter(self, p): self.p3 = p

    def getP1(*args): raise NotImplementedError('No default accessors.')
    def getP2(*args): raise NotImplementedError('No default accessors.')
    def getP3(*args): raise NotImplementedError('No default accessors.')
    def setP1(*args): raise NotImplementedError('No default accessors.')
    def setP2(*args): raise NotImplementedError('No default accessors.')
    def setP3(*args): raise NotImplementedError('No default accessors.')

