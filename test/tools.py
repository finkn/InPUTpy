"""
test.tools

Tools that are useful for writing unit tests for InPUT.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""

def checkVariability(f, iterations=10):
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            return True     # Found a new value.
        else:
            values.append(value)
    return False            # No variation after N iterations.


def checkConstancy(f, iterations=10):
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            return False    # Found a new value.
        else:
            values.append(value)
    return True             # No variation after N iterations.


def checkArrayDimensions(sizes, array):
    size = sizes[0]
    if size != len(array):
        return False        # Current dimension does not match.
    if len(sizes) == 1:
        return True         # No more dimensions. Done.
    for element in array:
        if not checkArrayDimensions(sizes[1:], element):
            return False    # Check sub-arrays recursively.
    return True
