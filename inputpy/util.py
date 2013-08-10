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
        for (k, v) in cls.getSafeNamespace(mode).items():
            ns[k] = v
        return eval(exp, ns)

    @classmethod
    def __checkMode(cls, mode):
        if not mode in cls.MODES:
            raise ValueError('%s is not a valid mode' % (mode))

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
        raise ValueError('Detected circular dependency')
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
