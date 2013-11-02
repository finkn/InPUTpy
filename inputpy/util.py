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
    def findUniqueSuffix(cls, paramId, paramIds, n=0):
        """
        Return the parameter ID with a unique number suffix (the ID does
        not occur in the given list of IDs.
        The function name may be slightly misleading since not the suffix
        but the whole parameter is returned.

        Keyword arguments:
        n       -- can be used to start looking for suffixes at n.
        """
        suggestion = '%s%i' % (paramId, n)
        if suggestion not in paramIds:
            return suggestion
        else:
            return cls.findUniqueSuffix(paramId, paramIds, n+1)

    @classmethod
    def convertToNonDot(cls, paramId, paramIds, prefix='__', n=0):
        """
        Return the parameter ID with dots replaced by underscores.
        The resulting ID is guaranteed to be unique relative to the
        given list of IDs.
        The resulting ID will be of the form: prefixIDsuffix, where
        suffix is of the form prefixN.

        Keyword arguments:
        prefix  -- the prefix to place before the ID and the number.
        n       -- can be used to start looking for suffixes at n.
        """
        paramId = paramId.replace('.', '_')
        paramId = '%s%s%s' % (prefix, paramId, prefix)
        return cls.findUniqueSuffix(paramId, paramIds, n)

    @classmethod
    def getRemapping(cls, dependencies, paramIds):
        """
        Returns a dictionary, mapping any parameter IDs containing dots
        to suitable dot-free alternatives.
        When resolving dependencies during evaluation, dots are fatal.
        This function allows for the simple dependency dictionary to be
        used by re-mapping those dependencies to new names.

        Dots are replaced by underscores. In order to prevent name
        collisions caused by this translation, the IDs are further mangled
        and guaranteed to be unique.
        """
        n = 0
        prefix = '__' # <-- He he, look how eager he is!
        # Slight performance optimization. We only have to avoid collisions
        # with any parameters that at least begin with the prefix.
        paramIds = [p for p in paramIds if p.startswith(prefix)]
        # And no need to remap IDs without dots.
        dependencies = [d for d in dependencies if d.find('.') != -1]
        result = {}
        for d in dependencies:
            converted = cls.convertToNonDot(d, paramIds, prefix, n)
            paramIds.append(converted)
            result[d] = converted
            n = n + 1

        return result

    @classmethod
    def remapExpression(cls, exp, remapping):
        """
        Returns the expression with the parameter references remapped to
        the dot-free parameter IDs.
        """
        # Necessary to perform greedy replacement.
        keys = sorted(remapping.keys(), key=len, reverse=True)
        for k in keys:
            exp = exp.replace(k, remapping[k])
        return exp

    @classmethod
    def evaluate(cls, exp, params={}, mode=JS):
        """
        Evaluate the expression inside a safe namespace, optionally including
        extra parameters.

        Keyword arguments:
        params  -- any parameters referenced in the expression (default {})
        mode    -- the evaluation mode (default 'js')
        """
        # This function should probably not do the remapping internally.
        # The expression and the parameters should probably already have been
        # remapped before this function is called.
        ns = dict(params)
        ns.update(cls.getSafeNamespace(mode))
        parameters = cls.parseDependencies(exp, mode)
        paramIds = params.keys()
        remapping = cls.getRemapping(parameters, paramIds)
        for (k,v) in remapping.items():
            ns[v] = ns[k]
            del ns[k]
        exp = cls.remapExpression(exp, remapping)
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

# TODO:
# These two functions are extremely ugly (and possibly even unreliable)
# heuristics. They must be replaced!
def isArrayElement(paramId, params):
    paramId = paramId[paramId.find('.') + 1:]
    parts = paramId.split('.')
    for component in parts:
        if not component.isdigit():
            return False
    return True

# Might not even work? What if this is a nested param of an SParam that is
# an array element?
def isSParam(paramId, params):
    paramId = paramId[paramId.find('.') + 1:]
    parts = paramId.split('.')
    for component in parts:
        if component.isdigit():
            return False
    return True

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
    of an array parameter, then the array element takes precedence.
    """
    # Handle regular parameter ID without any dots.
    if paramId.find('.') == -1:
        return params.get(paramId)

    parts = paramId.split('.')
    result = params.get(parts[0])
    if result is None:
        return params.get(paramId)
    if isArrayElement(paramId, params):
        indexes = [int(i)-1 for i in parts[1:]]
        for i in indexes:
            result = result[i]
        return result
    elif isSParam(paramId, params):
        return params.get(paramId)

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

def stripFirstArrayDimension(typeString):
    """
    Return a tuple of first array dimension and the rest of the type
    string. Example:
    'integer[2][3]' => (2, 'integer[3]')
    'integer[3]'    => (3, 'integer')
    Missing dimensions (empty brackets) default to 0:
    'integer[][3]' => (0, 'integer[3]')
    """
    startIndex = typeString.index('[')
    endIndex = typeString.index(']')
    size = int(typeString[startIndex+1:endIndex] or 0)
    typeString = typeString[:startIndex] + typeString[endIndex+1:]
    return (size, typeString)

def getBaseType(typeString):
    """
    Return the base type. Returns the type without any array dimensions.
    For regular parameters, the type string is simply returned as is.
    """
    if typeString is None:
        return typeString
    startIndex = typeString.find('[')
    if startIndex == -1:
        return typeString
    return typeString[:startIndex]

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

def absolute(parentId, paramId):
    """
    Return the absolute parameter ID of the parameter relative to the
    parent. If the parent is None or empty (''), then the parameter ID
    is already absolute and is simply returned.
    """
    if parentId is None or parentId == '':
        return paramId
    else:
        return parentId + '.' + paramId

def parent(paramId):
    """
    Return the parent ID, or None if the parameter is already at the root.
    This function basically does a '$ cd ..'.
    """
    index = paramId.rfind('.')
    if index == -1:
        return None
    else:
        return paramId[:index]

def relative(paramId):
    """
    Return the relative parameter ID. In other words, it strips away the
    parent ID from an absolute ID.
    """
    index = paramId.rfind('.')
    if index == -1:
        return paramId
    else:
        return paramId[index + 1:]

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
    param = absolute(contextId, paramId)

    if param in ids:
        return param
    elif contextId is None:
        return None
    else:
        contextId = parent(contextId)
        return findAbsoluteParameter(contextId, paramId, ids)

def getAbsoluteDependenciesForParam(param, supportedIds):
    results = []
    paramId = param.getId()
    for depId in param.getDependees():
        absolute = findAbsoluteParameter(paramId, depId, supportedIds)
        if absolute is None:
            msg = '%s referencing nonexistent parameter %s' % (paramId, depId)
            raise ValueError(msg)
        else:
            results.append(absolute)
    return results

def getAbsoluteDependencies(params):#, dependencies):
    return {k: getAbsoluteDependenciesForParam(params[k], params.keys())
            for k in params.keys()}
