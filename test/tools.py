"""
test.tools

Tools that are useful for writing unit tests for InPUT.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""

import warnings

# TODO:
# Remove all the check* functions once all of them have assert* replacements
# and they are not longer used elsewhere.

def checkVariability(f, iterations=10):
    warnings.warn('use the assert version instead', DeprecationWarning)
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
    warnings.warn('use the assert version instead', DeprecationWarning)
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            return False    # Found a new value.
        else:
            values.append(value)
    return True             # No variation after N iterations.


def assertVariability(f, iterations=10):
    """ Assert that f will generate at least one unique value. """
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            return True     # Found a new value.
        else:
            values.append(value)
    msg = 'Only generated %s for %i iterations' % (value, iterations)
    raise AssertionError(msg)

def assertConstancy(f, iterations=10):
    """ Assert that f will only generate a constant value. """
    assert iterations > 1, '1 iteration makes no sense!'
    values = []
    for i in range(iterations):
        value = f()
        if value not in values and len(values) > 0:
            msg = 'Generated a unique value after %i iterations' % (iterations)
            raise AssertionError(msg)
        else:
            values.append(value)
    return True             # No variation after N iterations.


def checkArrayDimensions(sizes, array):
    warnings.warn('use the assert version instead', DeprecationWarning)
    size = sizes[0]
    if size != len(array):
        return False        # Current dimension does not match.
    if len(sizes) == 1:
        return True         # No more dimensions. Done.
    for element in array:
        if not checkArrayDimensions(sizes[1:], element):
            return False    # Check sub-arrays recursively.
    return True

def assertMatchingArrayDimensions(sizes, array):
    """
    Assert that the array dimensions match the given sizes.
    The sizes are listed in order of nesting, which implies that the
    sub-arrays on each level must be uniformly sized.
    """
    size = sizes[0]
    if size != len(array):
        msg = '%i does not match length of %s' % (size, len(array))
        raise AssertionError(msg)
    if len(sizes) == 1:
        return True         # No more dimensions. Done.
    for element in array:
        # Check sub-arrays recursively.
        assertMatchingArrayDimensions(sizes[1:], element)
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
    warnings.warn('use the assert version instead', DeprecationWarning)
    return any([v in expected for v in values])

def checkAllValuesMatch(values, expected):
    """
    Return whether all of the values match an expected value.
    The return value is True if and only if there does not exist some
    value v such that v is not one of the expected values.
    """
    warnings.warn('use the assert version instead', DeprecationWarning)
    return all([v in expected for v in values])


def checkGeneratesAnyExpected(f, expected, iterations=10):
    """
    Return True if the function f generates one of the expected values.
    """
    warnings.warn('use the assert version instead', DeprecationWarning)
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
    warnings.warn('use the assert version instead', DeprecationWarning)
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
    warnings.warn('use the assert version instead', DeprecationWarning)
    for i in range(iterations):
        if f() not in expected:
            return False
    return True


def assertGeneratesAny(f, expected, iterations=10):
    """ Assert that f generates at least one expected value. """
    for i in range(iterations):
        if f() in expected:
            return True
    msg = 'Generated none of %s after %i iterations' % (expected, iterations)
    raise AssertionError(msg)

def assertGeneratesAll(f, expected, iterations=None):
    """
    Assert that f generates all expected values.
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
    msg = '%s still missing after %i iterations' % (expected, iterations)
    raise AssertionError(msg)

def assertGeneratesOnly(f, expected, iterations=10):
    """ Assert only expected values are generated by f. """
    for i in range(iterations):
        v = f()
        if v not in expected:
            raise AssertionError('%s not in %s' % (v, expected))
    return True
