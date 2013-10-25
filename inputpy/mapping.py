"""
mapping.py

A module for handling code mappings.
Note that this module has state.

The NULL_CODE_MAPPING object is a predefined code mapping that always
returns None. This can be used when no real mapping exists.
It's a Null Object.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import importlib
from inputpy.q import SETTER_PREFIX, GETTER_PREFIX
import inputpy.util as util

__all__ = ('getType', 'Mapping', 'CodeMapping', 'NULL_CODE_MAPPING',)

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
    moduleName = util.parent(typeString) or 'builtins'
    typeName = util.relative(typeString) or typeString

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
def getDefaultSetter(paramId, prefix=SETTER_PREFIX):
    """
    Return the name of the default setter for this parameter ID.
    A prefix can optionally be specified.
    """
    return prefix + util.relative(paramId)

def getDefaultGetter(paramId, prefix=GETTER_PREFIX):
    """
    Return the name of the default getter for this parameter ID.
    A prefix can optionally be specified.
    """
    return prefix + util.relative(paramId)

class Mapping:
    def __init__(self, id, type, constructor=None, set=None, get=None):
        self.id = id
        self.typeName = type
        self.constructor = constructor
        self.setter = set
        self.getter = get

        if constructor is not None:
            self.dep = tuple(constructor.split())
        else:
            self.dep = ()

    def getId(self):
        return self.id

    def getType(self):
        return getType(self.typeName)

    def getTypeName(self):
        return self.typeName

    def getDependencies(self):
        return self.dep

    def getConstructor(self):
        return self.constructor

    def getSetter(self):
        return self.setter or getDefaultSetter(self.id)

    def getGetter(self):
        return self.getter or getDefaultGetter(self.id)

    def getParameters(self):
        return {
            'id': self.id, 'type': self.typeName, 'get': self.getter,
            'constructor': self.constructor, 'set': self.setter,
        }

    @staticmethod
    def makeDirect(paramId, mapping):
        params = mapping.getParameters()
        params['id'] = paramId
        return Mapping(**params)

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return False
        if self.id != other.id: return False
        if self.typeName != other.typeName: return False
        if self.dep != other.dep: return False
        if self.constructor != other.constructor: return False
        if self.setter != other.setter: return False
        if self.getter != other.getter: return False
        return True

    def __str__(self):
        return '%s -> %s' % (self.id, self.typeName)

    def __repr__(self):
        return self.__str__()


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
        return self.__mappings.get(id)

    def __eq__(self, other):
        smt = self.__mappingTypes
        spm = self.__paramMappings
        omt = other.__mappingTypes
        opm = other.__paramMappings

        if len(smt) != len(omt): return False
        if len(spm) != len(opm): return False

        for m in smt:
            if smt.count(m) != omt.count(m): return False
        for m in omt:
            if smt.count(m) != omt.count(m): return False
        for m in spm:
            if spm.count(m) != opm.count(m): return False
        for m in opm:
            if spm.count(m) != opm.count(m): return False

        return True

NULL_CODE_MAPPING = CodeMapping([], [])
