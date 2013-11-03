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


# Note that these two functions can be used in two different ways, simply
# by flipping the order of their arguments. The values can either be
# matched against expected values, or the other way around. Both are useful.

def checkAnyValueMatches(values, expected):
    """
    Return whether any of the values match an expected value.
    The return value is True if and only if there exists some value v
    such that v is one of the expected values.
    """
    return any([v in expected for v in values])

def checkAllValuesMatch(values, expected):
    """
    Return whether all of the values match an expected value.
    The return value is True if and only if there does not exist some
    value v such that v is not one of the expected values.
    """
    return all([v in expected for v in values])


def checkGeneratesAnyExpected(f, expected, iterations=10):
    """
    Return True if the function f generates one of the expected values.
    """
    for i in range(iterations):
        if f() in expected:
            return True
    return False

def checkGeneratesAllExpected(f, expected, iterations=None):
    """
    Return True if the function f generates all of the expected values.
    The number of iterations is proportional to the number of values.
    If given, iterations must be >= the number of expected values.
    """
    if iterations is None:
        iterations = len(expected) * 10
    else:
        msg = 'Must generate at least as many values as are expected'
        assert iterations > len(expected), msg

    expected = list(expected)
    for i in range(iterations):
        v = f()
        if v in expected:
            expected.remove(v)
        if len(expected) == 0:
            return True
    return False

def checkGeneratesOnlyExpected(f, expected, iterations=10):
    """
    Return False as soon as f generates a value that does not match any of
    the expected values.
    """
    for i in range(iterations):
        if f() not in expected:
            return False
    return True
