"""
mapping.py

A module for handling code mappings.
Note that this module has state.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import importlib

__all__ = ('getType', 'Mapping', 'CodeMapping', )

mappings = {}
types = {}

def __load(typeString):
    """
    Return the type referred to by a string naming the type, including any
    package and module names.
    While the use of plain built-in type names ('int') is discouraged
    ('builtins.int' should be used instead), both cases are supported.

    This is a low level helper function. It does not do any caching, so it
    will always import modules.
    This function is as pure as a function that interacts with the file
    system can be.
    """
    typeName = typeString
    moduleName = 'builtins'
    modEnd = typeString.rfind('.')

    if modEnd != -1:
        moduleName = typeString[:modEnd]
        typeName = typeString[modEnd+1:]

    module = importlib.import_module(moduleName)
    return module.__dict__[typeName]

def getType(typeString):
    """
    Return a type referred to by a string. Modules will be imported as
    necessary. Redundant imports are avoided by caching the results.
    """
    if typeString not in types:
        types[typeString] = __load(typeString)
    return types[typeString]

# If we're serious about supporting parameter names with spaces, then
# they should be removed or replaced here. Otherwise the accessor will be
# absolutely illegal and useless.
def getAccessor(paramId, prefix):
    """
    Returns the parameter ID with a prefix attached. This function is
    almost silly, but it does strip the parameter ID to the relative
    part, which means that this function can handle absolute IDs.
    """
    # TODO:
    # Pull this out and make a general utility function out of it.
    index = paramId.rfind('.')
    if index != -1:
        paramId = paramId[index + 1:]
    return prefix + paramId

def getDefaultSetter(paramId, prefix='set'):
    """
    Uses getAccessor with a default prefix of 'set'.
    """
    return getAccessor(paramId, prefix)

def getDefaultGetter(paramId, prefix='get'):
    """
    Uses getAccessor with a default prefix of 'get'.
    """
    return getAccessor(paramId, prefix)

class Mapping:
    def __init__(self, id, type, constructor=None, set=None, get=None):
        self.id = id
        self.type = type
        self.constructor = constructor
        self.setter = set or getDefaultSetter(id)
        self.getter = get or getDefaultGetter(id)

        if constructor is not None:
            self.dep = tuple(constructor.split())
        else:
            self.dep = ()

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def getTypeName(self):
        return self.type

    def getDependencies(self):
        return self.dep

    def getConstructor(self):
        return self.constructor

    def getSetter(self):
        return self.setter

    def getGetter(self):
        return self.getter

    def getParameters(self):
        return {
            'id': self.id, 'type': self.type, 'constructor': self.constructor,
            'set': self.setter, 'get': self.getter,
        }

    @staticmethod
    def makeDirect(paramId, mapping):
        params = mapping.getParameters()
        params['id'] = paramId
        return Mapping(**params)

class CodeMapping:
    """
    Objects of this class act as databases of code mappings.
    The class uses a bit of internal magic to simplify handling of the
    different mappings, but the original information should still be
    reproducible.
    """
    def __init__(self, paramMappings, mappingTypes):
        """
        Regular mappings (corresponding to a "Mapping" element) and
        mapping types (corresponding to a "MappingType" element) are
        handled separately to make it possible to accurately export the
        object to XML if needed.
        """
        self.__paramMappings = paramMappings
        self.__mappingTypes = mappingTypes

        types = {m.getId(): m for m in mappingTypes}

        # Update the mapping so that every parameter is associated to a mapping.
        # If the type matches one of the mapping types, then a new mapping is
        # created. The same type and initialization information is used, but
        # now it is directly mapped from a parameter ID.
        self.__mappings = {m.getId(): m for m in paramMappings}
        self.__mappings.update({
            m.getId(): Mapping.makeDirect(m.getId(), types[m.getTypeName()])
            for m in paramMappings if m.getTypeName() in types
        })

    # Always returns a full/direct mapping.
    def getMapping(self, id):
        return self.__mappings[id]