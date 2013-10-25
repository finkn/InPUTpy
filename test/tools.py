"""
test.tools

Exports fake factories for "importing" known configurations.

:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
from inputpy.designspace import DesignSpace
from inputpy.param import ParamStore, getParameter, paramFactory
from inputpy.mapping import Mapping, CodeMapping, NULL_CODE_MAPPING
from inputpy.q import *

__all__ = (
    'PresetCodeMappingFactory', 'PresetParamStoreFactory',
    'PresetDesignSpaceFactory',
)

# Trying to compress the arguments.
ID = ID_ATTR
TYPE = TYPE_ATTR
INT = INTEGER
IMIN = INCL_MIN
IMAX = INCL_MAX
NESTED = 'nested'
SP = SPARAM
POINT = 'test.types.geo.Point'
TRIANGLE = 'test.types.geo.Triangle'
TRIANGLE_CUSTOM = 'test.types.geo.TriangleWithCustomAccessors'
TRIANGLE_DEFAULT = 'test.types.geo.TriangleWithoutConstructor'

def makeIntParam(d):
    d[TAG] = NPARAM
    d[TYPE] = INTEGER
    return d

class PresetCodeMappingFactory:

    M = Mapping
    P = 'Point'
    T = 'Triangle'
    TRIANGLE_PMAP = (
        M('P1', P), M('T1', T), M('T1.P1', P), M('T1.P2', P), M('T1.P3', P),
        M('P4', P), M('T2', T), M('T2.P1', P), M('T2.P2', P), M('T2.P3', P),
    )
    TRIANGLE_MAPT = (
        M(P, POINT, constructor='X Y'), M(T, TRIANGLE, constructor='P1 P2 P3'),
    )

    P1 = 'Point1'
    P2 = 'Point2'
    P3 = 'Point3'
    CUSTOM_ACCESSOR_TRIANGLE_PMAP = (
        M('P1', P), M('P4', P), M('T1', T), M('T2', T),
        M('T1.P1', P1), M('T1.P2', P2), M('T1.P3', P3),
        M('T2.P1', P1), M('T2.P2', P2), M('T2.P3', P3),
    )
    CUSTOM_ACCESSOR_TRIANGLE_MAPT = (
        M(P, POINT, constructor='X Y'), M(T, TRIANGLE_CUSTOM),
        M(P1, POINT, constructor='X Y', set='customP1Setter'),
        M(P2, POINT, constructor='X Y', set='customP2Setter'),
        M(P3, POINT, constructor='X Y', set='customP3Setter'),
    )

    DEFAULT_ACCESSOR_TRIANGLE_PMAP = TRIANGLE_PMAP
    DEFAULT_ACCESSOR_TRIANGLE_MAPT = (
        M(P, POINT, constructor='X Y'), M(T, TRIANGLE_DEFAULT),
    )

    MAPPINGS = {
        'triangleMapping.xml': (
            TRIANGLE_PMAP, TRIANGLE_MAPT,
        ),
        'triangleCustomAccessorMapping.xml': (
            CUSTOM_ACCESSOR_TRIANGLE_PMAP, CUSTOM_ACCESSOR_TRIANGLE_MAPT
        ),
        'triangleDefaultAccessorMapping.xml': (
            DEFAULT_ACCESSOR_TRIANGLE_PMAP, DEFAULT_ACCESSOR_TRIANGLE_MAPT
        ),
    }

    @staticmethod
    def getCodeMapping(fileName):
        # Getting code mapping for a design space without a mapping.
        if fileName is None:
            return NULL_CODE_MAPPING
        return CodeMapping(*(PresetCodeMappingFactory.MAPPINGS[fileName]))


class PresetParamStoreFactory:

    SIMPLE_INTEGER_SPACE = (
        {ID: 'A', },
        {ID: 'B', INCL_MIN: '1'},
        {ID: 'C', INCL_MAX: '1'},
        {ID: 'D', EXCL_MIN: '1'},
        {ID: 'E', EXCL_MAX: '1'},
        {ID: 'F', INCL_MIN: '1', INCL_MAX: '3'},
        {ID: 'G', EXCL_MIN: '1', EXCL_MAX: '3'},
        {ID: 'H', INCL_MIN: '1', EXCL_MAX: '3'},
        {ID: 'I', EXCL_MIN: '1', INCL_MAX: '3'},
        {ID: 'J', EXCL_MIN: '0', INCL_MAX: '3'},
        {ID: 'K', EXCL_MIN: '-1', INCL_MAX: '0'},
        {ID: 'L', INCL_MIN: '0', INCL_MAX: '0'},
        {ID: 'M', FIXED_ATTR: '43'},
        {ID: 'N', INCL_MIN: '1', FIXED_ATTR: '43'},
        {ID: 'O', INCL_MIN: '1', INCL_MAX: '3', FIXED_ATTR: '43'},
        {ID: 'P', FIXED_ATTR: '2.9'},
        {ID: 'Q', INCL_MIN: '0.1', INCL_MAX: '1.9'},
    )
    SIMPLE_INTEGER_SPACE = tuple(map(makeIntParam, SIMPLE_INTEGER_SPACE))


    ADVANCED_INTEGER_SPACE = (
        {ID: 'A', INCL_MIN: '1 + 2'},
        {ID: 'B', INCL_MIN: '(1 + 2) + 3'},
        {ID: 'C', INCL_MIN: '4 * 3 / 2 + 1 - (2 + 3)'},
        {ID: 'D', INCL_MIN: '4 * (3 / (2 + 1)) - 2 + 3'},
        {ID: 'E', INCL_MIN: '(4 * 3) / (2 + (-1 - (1 - 3)))'},
        {ID: 'F', INCL_MIN: '(4*3)/(2+(-1-(1-3)))'},
        {ID: 'G', INCL_MIN: 'Math.cos(Math.pi)'},
        {ID: 'H', INCL_MIN: 'Math.exp(Math.cos(Math.pi*2)) / (Math.e * 2)'},
        {ID: 'I', INCL_MIN: 'Y'},
        {ID: 'J', INCL_MIN: 'Z'},
        {ID: 'K', INCL_MIN: 'Z + Y'},
        {ID: 'L', INCL_MIN: '(Z + Y) * Z / ((4 + Y) - Z)'},
        {ID: 'M', INCL_MIN: 'Math.exp(Math.cos(Z*2)) / (Math.e * Y)'},
        {ID: 'N', FIXED_ATTR: '1 + 2'},
        {ID: 'O', INCL_MIN: '(4 * 3) / (2 + (-1 - (1 - 3)))'},
        {ID: 'P', INCL_MIN: 'Math.exp(Math.cos(Math.pi*2)) / (Math.e * 2)'},
        {ID: 'Y', INCL_MIN: '2', INCL_MAX: '2'},
        {ID: 'Z', FIXED_ATTR: '2'},
    )
    ADVANCED_INTEGER_SPACE = tuple(map(makeIntParam, ADVANCED_INTEGER_SPACE))

    SIMPLE_TRIANGLE_SPACE = (
        {ID: 'X', TYPE: INT, IMIN: '0', IMAX: '0'},
        {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
        {ID: 'P1', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Y', TYPE: INT, IMIN: '3', IMAX: '3'},
        ), },
        {ID: 'P4', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '4', IMAX: '4'},
            {ID: 'Y', TYPE: INT, IMIN: '8', IMAX: '8'},
        ), },
        {ID: 'T1', TAG: SP, NESTED: (
            {ID: 'P1', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
            {ID: 'P2', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '5', IMAX: '5'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
        ), },
        {ID: 'T2', TAG: SP, NESTED: (
            {ID: 'P1', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
            {ID: 'P2', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '5', IMAX: '5'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
        ), },
    )

    # This config is subject to change. It's supposed to include a wide
    # variety of different dependencies, which isn't the case now.
    ADVANCED_TRIANGLE_SPACE = (
        {ID: 'X', TYPE: INT, IMIN: '0', IMAX: '0'},
        {ID: 'Y', TYPE: INT, IMIN: 'X + 1', IMAX: 'X + 1'},
        {ID: 'P1', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '4', IMAX: '4'},
            {ID: 'Y', TYPE: INT, IMIN: 'X + 1', IMAX: 'X + 1'},
        ), },
        {ID: 'P4', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Y', TYPE: INT, IMIN: 'X + 1', IMAX: 'X + 1'},
        ), },
        {ID: 'T1', TAG: SP, NESTED: (
            {ID: 'P1', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: 'T2.P2.X + 1', IMAX: 'T2.P2.X + 1'},
            ), },
            {ID: 'P2', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '5', IMAX: '5'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
        ), },
        {ID: 'T2', TAG: SP, NESTED: (
            {ID: 'P1', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
            {ID: 'P2', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '5', IMAX: '5'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
        ), },
    )

    STORES = {
        'simpleIntegerParameterSpace.xml': SIMPLE_INTEGER_SPACE,
        'advancedIntegerParameterSpace.xml': ADVANCED_INTEGER_SPACE,
        'simpleTriangleSpace.xml': SIMPLE_TRIANGLE_SPACE,
        'advancedTriangleSpace.xml': ADVANCED_TRIANGLE_SPACE,
    }

    @staticmethod
    def getParamStore(fileName, mapping=None):
        paramArgs = PresetParamStoreFactory.STORES[fileName]
        params = [paramFactory(args, mapping) for args in paramArgs]
        return ParamStore(params)


class PresetDesignSpaceFactory:
    IDS = {
        'simpleIntegerParameterSpace.xml': 'simpleInteger',
        'advancedIntegerParameterSpace.xml': 'advancedInteger',
        'simpleTriangleSpace.xml': 'triangle',
        'advancedTriangleSpace.xml': 'triangle',
    }

    MAPPING = {
        'simpleTriangleSpace.xml': 'triangleMapping.xml',
        'advancedTriangleSpace.xml': 'triangleMapping.xml',
    }

    @staticmethod
    def getDesignSpace(fileName,
            codeMappingFactory=PresetCodeMappingFactory.getCodeMapping,
            psFactory=PresetParamStoreFactory.getParamStore):

        mappingFile = PresetDesignSpaceFactory.MAPPING.get(fileName)
        mapping = codeMappingFactory(mappingFile)
        ps = psFactory(fileName, mapping)

        return DesignSpace(ps, PresetDesignSpaceFactory.IDS[fileName], fileName)
