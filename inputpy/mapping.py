"""
mapping.py

A module for handling code mappings.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import importlib

mappings = {}

def getType(typeString):
    """
    Return the type referred to by a string naming the type, including any
    package and module names.
    While the use of plain built-in type names ('int') is discouraged
    ('builtins.int' should be used instead), both cases are supported.
    """
    typeName = typeString
    moduleName = 'builtins'
    modEnd = typeString.rfind('.')

    if modEnd != -1:
        moduleName = typeString[:modEnd]
        typeName = typeString[modEnd+1:]

    module = importlib.import_module(moduleName)
    return module.__dict__[typeName]
