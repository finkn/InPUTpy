"""
inputpy.util

This module exports utility classes/functions:
- Evaluator
    - Can evaluate expressions, optionally including parameter values.
    - Can parse expressions and return referenced parameters.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import math

class Evaluator:
    """
    By default, the Evaluator is expected to process JavaScript
    compatible expressions. Python expressions can optionally be used.
    Any function that takes an optional mode argument can operate in
    JavaScript or Python mode. The default is always JavaScript. Valid
    modes are 'js' or 'py' (Evaluator.JS, Evaluator.PY).
    """
    # Eventually, some more sophisticated wrapper will be needed in order to
    # map references to JavaScript Math functions and constants to the
    # corresponding Python objects.
    # Only most of the functions match.

    JS = 'js'
    PY = 'py'
    MODES = (JS, PY,)
    MATH_NAME = {JS: 'Math', PY: 'math', }

    @classmethod
    def parseDependencies(cls, exp, mode=JS):
        """
        Return a list that is the set of parameters referenced in the
        expression, if any.

        Keyword arguments:
        mode    -- the evaluation mode (default 'js')
        """
        cls.__checkMode(mode)
        skip = '+-*/()'
        m = cls.MATH_NAME[mode] + '.'
        for c in skip:
            exp = exp.replace(c, ' ')
        return [
            s for s in set(exp.split())
                if not (s.startswith(m) or s[0].isdigit() or s[0] == '.')
        ]

    @classmethod
    def getSafeNamespace(cls, mode=JS):
        """
        Return a namespace that is safe for evaluating arbitrary mathematical
        expressions. The namespace includes a math library but is otherwise
        completely empty.

        Keyword arguments:
        mode    -- the evaluation mode (default 'js')
        """
        cls.__checkMode(mode)
        return {cls.MATH_NAME[mode]: math, '__builtins__': {}}

    @classmethod
    def evaluate(cls, exp, params={}, mode=JS):
        """
        Evaluate the expression inside a safe namespace, optionally including
        extra parameters.

        Keyword arguments:
        params  -- any parameters referenced in the expression (default {})
        mode    -- the evaluation mode (default 'js')
        """
        ns = dict(params)
        ns.update(cls.getSafeNamespace(mode))
        return eval(exp, ns)

    @classmethod
    def __checkMode(cls, mode):
        if not mode in cls.MODES:
            raise ValueError('%s is not a valid mode' % (mode))

    # This is a naive implementation.
    # It should work for all simple, literal ranges, but it does not
    # enforce this limitation. It almost works for arbitrary expressions.
    # The problem is that function calls can contain commas, which would
    # be a problem. Arbitrary expressions need regexp matching.
    @staticmethod
    def parseRange(exp):
        return [s.strip() for s in exp.split(',')]

def depLen(params, paramId, dependents=None):
    """
    Return the longest chain of dependencies for the parameter ID using
    the dependency information in params.
    An independent parameter will have a dependency length of 0.

    This function assumes that there are no missing dependencies.

    Raises ValueError if a circular dependency is found.
    """
    # These are the parameters that directly or indirectly depend on the
    # current parameter. If this parameter is one of them, then it depends
    # on itself, which means that we've found a circular dependency.
    dependents = list(dependents or [])
    if paramId in dependents:
        raise ValueError('Detected circular dependency for ' + paramId)
    dependents.append(paramId)

    dep = params[paramId]
    if len(dep) == 0:
        return 0
    return max([depLen(params, d, dependents) + 1 for d in dep])

def initOrder(params):
    """
    Return dependency chain length mapped to a collection of parameter IDs
    where each parameter has a matching dependency length. In other words, the
    resulting dictionary gives the initialization order of the parameters.
    The dependency information in the dep argument is expected to be a
    dictionary that maps IDs to collections of IDs, where the key is a
    parameter that depends on the parameters in the value.
    """
    result = {}
    for k in params.keys():
        l = depLen(params, k)
        p = result.get(l, [])
        p.append(k)
        result[l] = p
    return result

def getValue(paramId, params):
    """
    Return the value of the parameter with the given ID.
    Can handle four cases:
    - An ID that does not contain dots, which may be:
        - A regular parameter.
        - An array parameter.
    - An ID that contains one or more dots, which may be:
        - A regular parameter.
        - An array parameter element.

    If there should exist a parameter that has the same ID as the element
    of an array parameter, then the array element takes precedent.
    """
    # Handle regular parameter ID without any dots.
    if paramId.find('.') == -1:
        return params.get(paramId)
    # Handle parameter ID with one or more dots.
    # This may be a regular parameter after all, or it may be an array element.
    parts = paramId.split('.')
    result = params.get(parts[0])
    if result is None:
        return params.get(paramId)
    # Assumes an array.
    indexes = [int(i)-1 for i in parts[1:]]
    for i in indexes:
        result = result[i]
    return result

# This function needs cleaning up!
def setValue(paramId, params, value):
    # Handle regular parameter ID without any dots.
    if paramId.find('.') == -1:
        if paramId in params:
            params[paramId] = value
            return
        else:
            raise KeyError('No parameter with ID %s exists.' % (paramId))
    # Handle parameter ID with one or more dots.
    # This may be a regular parameter after all, or it may be an array element.
    parts = paramId.split('.')
    result = params.get(parts[0])
    if result is None:
        if paramId in params:
            params[paramId] = value
            return
        else:
            raise KeyError('No parameter with ID %s exists.' % (paramId))

    indexes = [int(i)-1 for i in parts[1:]]

    target = result
    for i in range(len(indexes) - 1):
        index = indexes[0]
        indexes = indexes[1:]
        target = target[index]

    try:
        target[indexes[0]] = value
    except TypeError:
        raise KeyError('No parameter with ID %s exists.' % (paramId))

def parseDimensions(typeString):
    """
    Return the array dimensions this type string encodes.
    Expects a string of the form 'type[n1][n2]...[nm]' where type can be
    anything and any n can be absent.
    The result is a list containing all dimensions in order. For any missing
    size ('[]'), the resulting list will contain 0.
    """
    parts = typeString.split('[')[1:]   # Strip the regular type away.
    result = []
    for p in parts:
        p = p.replace(']', ' ').strip()
        if p == '':
            p = '0'
        result.append(int(p))
    return result

def expandParameterScope(contextId):
    """
    Return a parameter ID that represents an outer scope, or None if the
    scope cannot be expanded further (the context is already at the root).
    See info on findAbsoluteParameter for more details.
    This function basically does a '$ cd ..'.
    """
    index = contextId.rfind('.')
    if index == -1:
        return None
    else:
        return contextId[:index]

def findAbsoluteParameter(contextId, paramId, ids):
    """
    Return the absolute name of a parameter, relative to a context.
    The contextId parameter specifies a scope by naming a parameter
    relative to which some other parameter might be located.
    The scope is expanded more and more until the absolute path matches
    one of the given valid IDs.

    The contextId is always absolute. IDs in the ids collection are
    always absolute. The paramId may be absolute or relative.
    """
    if contextId is None:
        param = paramId
    else:
        param = contextId + '.' + paramId

    if param in ids:
        return param
    elif contextId is None:
        return None
    else:
        contextId = expandParameterScope(contextId)
        return findAbsoluteParameter(contextId, paramId, ids)
