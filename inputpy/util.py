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
        m = Evaluator.MATH_NAME[mode] + '.'
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
        return {Evaluator.MATH_NAME[mode]: math, '__builtins__': {}}

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
        if not mode in Evaluator.MODES:
            raise ValueError('%s is not a valid mode' % (mode))
