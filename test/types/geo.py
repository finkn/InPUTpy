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

class Point:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def getX(self): return self.__x
    def getY(self): return self.__y

class Triangle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
