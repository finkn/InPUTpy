"""
test.factories

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
DPOINT = 'test.types.geo.DoublePoint'
NAPOINT = 'test.types.geo.PointWithoutAccessors'
NCPOINT = 'test.types.geo.PointWithoutConstructor'
SHAPE = 'test.types.geo.Shape'
RECT = 'test.types.geo.Rectangle'
SQUARE = 'test.types.geo.Square'
TRIANGLE = 'test.types.geo.Triangle'
TRIANGLE_CUSTOM = 'test.types.geo.TriangleWithCustomAccessors'
TRIANGLE_DEFAULT = 'test.types.geo.TriangleWithoutConstructor'
EMPTY = 'test.types.simple.EmptyClass'
EMPTY1 = 'test.types.simple.Empty1'
EMPTY2 = 'test.types.simple.Empty2'
EMPTY3 = 'test.types.simple.Empty3'
NONEMPTY = 'test.types.simple.NonEmptyClass'
NONEMPTY1 = 'test.types.simple.NonEmpty1'
NONEMPTY2 = 'test.types.simple.NonEmpty2'

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

    CHOICE_POINT_PMAP = (
        M('Point', POINT, constructor='X Y'), M('Point.Regular', POINT),
        M('Point.Double', DPOINT), M('Point.NoAccessors', NAPOINT),
    )
    CHOICE_SHAPE_PMAP = (
        M('Point', POINT, constructor='X Y'), M('Point.Regular', POINT),
        M('Point.Double', DPOINT), M('Point.NoAccessors', NAPOINT),
        M('PlainShape', SHAPE, constructor='Point1 Point2'),
        M('PlainShape.Point1', POINT, constructor='X Y'),
        M('PlainShape.Point2', POINT, constructor='X Y'),
    )
    CHOICE_PMAP = (
        M('Empty', EMPTY), M('Empty.E1', EMPTY1), M('Empty.E2', EMPTY2),
        M('Empty.E3', EMPTY3),
        M('NonEmpty', NONEMPTY, constructor='Obj'),
        M('NonEmpty.NE1', NONEMPTY1), M('NonEmpty.NE2', NONEMPTY2),
        M('Point', POINT, constructor='X Y'), M('Point.Regular', POINT),
        M('Point.Double', DPOINT), M('Point.NoAccessors', NAPOINT),
        M('Point.NoConstructor', NCPOINT, constructor=''),
        M('Shape', SHAPE), M('Shape.Point', POINT, constructor='X Y'),
        M('Shape.Rectangle', RECT, constructor='Point Width Height'),
        M('Shape.Square', SQUARE, constructor='Point Side'),
    )
    ARRAY_MAPT = (
        M('Empty', EMPTY), M(P, POINT, constructor='X Y'),
    )
    ARRAY_PMAP = (
        M('EmptyClassArray1', 'Empty'), M('EmptyClassArray2', 'Empty'),
        M('PointArray1', P), M('PointArray2', P), M('EmptyChoiceArray', 'Empty'),
        M('EmptyChoiceArray.Empty1', EMPTY1),
        M('EmptyChoiceArray.Empty2', EMPTY2),
        M('EmptyChoiceArray.Empty3', EMPTY3),
        M('PointChoiceArray', P),
        M('PointChoiceArray.Regular', P),
        M('PointChoiceArray.Double', DPOINT),
        M('PointChoiceArray.NoConstructor', NCPOINT, constructor=''),
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
        'choicePointMapping.xml': (
            CHOICE_POINT_PMAP, [],
        ),
        'choiceShapeMapping.xml': (
            CHOICE_SHAPE_PMAP, [],
        ),
        'choiceMapping.xml': (
            CHOICE_PMAP, [],
        ),
        'arrayMapping.xml': (
            ARRAY_PMAP, ARRAY_MAPT,
        )
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

    CHOICE_POINT_SPACE = (
        {ID: 'Point', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
            {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Regular', TAG: SCHOICE},
            {ID: 'Double', TAG: SCHOICE},
            {ID: 'NoAccessors', TAG: SCHOICE},
        ), },
    )
    CHOICE_SPACE = (
        {ID: 'Empty', TAG: SP, NESTED: (
            {ID: 'E1', TAG: SCHOICE}, {ID: 'E2', TAG: SCHOICE},
            {ID: 'E3', TAG: SCHOICE},
        ), },
        {ID: 'Point', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
            {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Regular', TAG: SCHOICE},
            {ID: 'Double', TAG: SCHOICE},
            {ID: 'NoAccessors', TAG: SCHOICE},
            {ID: 'NoConstructor', TAG: SCHOICE},
        ), },
        {ID: 'NonEmpty', TAG: SP, NESTED: (
            {ID: 'NE1', TAG: SCHOICE, NESTED: ({ID: 'Obj', TYPE: INT},)},
            {ID: 'NE2', TAG: SCHOICE, NESTED: ({ID: 'Obj', TYPE: FLOAT},)},
        ), },
        {ID: 'Shape', TAG: SP, NESTED: (
            {ID: 'Point', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'Square', TAG: SP, NESTED: (
                {ID: 'Side', TYPE: INT, IMIN: '3', IMAX: '3'},
            ), },
            {ID: 'Rectangle', TAG: SP, NESTED: (
                {ID: 'Width', TYPE: INT, IMIN: '4', IMAX: '4'},
                {ID: 'Height', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
        ), },
    )
    #"""
    CHOICE_SHAPE_SPACE = (
        {ID: 'Point', TAG: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
            {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Regular', TAG: SCHOICE},
            {ID: 'Double', TAG: SCHOICE},
            {ID: 'NoAccessors', TAG: SCHOICE},
        ), },
        {ID: 'PlainShape', TAG: SP, NESTED: (
            {ID: 'Point1', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'Point2', TAG: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '4', IMAX: '4'},
                {ID: 'Y', TYPE: INT, IMIN: '3', IMAX: '3'},
            ), },
        ), },
    )

    ARRAY_SPACE = (
        {ID: 'IntArray1', TYPE: 'integer[3]', IMIN: '1', IMAX: '1'},
        {ID: 'IntArray2', TYPE: 'integer[3][][2]', IMIN: '2', IMAX: '2'},
        {ID: 'FloatArray1', TYPE: 'float[3]', IMIN: '3.5', IMAX: '3.5'},
        {ID: 'FloatArray2', TYPE: 'float[3][][2]', IMIN: '4.5', IMAX: '4.5'},
        {ID: 'BoolArray1', TYPE: 'boolean[3]'},
        {ID: 'BoolArray2', TYPE: 'boolean[3][][2]'},
        {ID: 'FixedIntArray', TYPE: 'integer[3][][2]', FIXED_ATTR: '5'},
        {ID: 'FixedBoolArray', TYPE: 'boolean[3][][2]', FIXED_ATTR: 'false'},
        {ID: 'StringArray1', TAG: SP, TYPE: 'String[3]'},
        {ID: 'StringArray2', TAG: SP, TYPE: 'String[3][][2]'},
        {ID: 'EmptyClassArray1', TAG: SP, TYPE: '[3]'},
        {ID: 'EmptyClassArray2', TAG: SP, TYPE: '[3][][2]'},
        {ID: 'PointArray1', TAG: SP, TYPE: '[3]', NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
            {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
        ), },
        {ID: 'PointArray2', TAG: SP, TYPE: '[3][][2]', NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
            {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
        ), },
        {ID: 'EmptyChoiceArray', TAG: SP, TYPE: '[10]', NESTED: (
            {ID: 'Empty1', TAG: SCHOICE},
            {ID: 'Empty2', TAG: SCHOICE},
            {ID: 'Empty3', TAG: SCHOICE},
        ), },
        {ID: 'PointChoiceArray', TAG: SP, TYPE: '[10]', NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
            {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Regular', TAG: SCHOICE},
            {ID: 'Double', TAG: SCHOICE},
            {ID: 'NoConstructor', TAG: SCHOICE},
        ), },
    )

    STORES = {
        'simpleIntegerParameterSpace.xml': SIMPLE_INTEGER_SPACE,
        'advancedIntegerParameterSpace.xml': ADVANCED_INTEGER_SPACE,
        'simpleTriangleSpace.xml': SIMPLE_TRIANGLE_SPACE,
        'advancedTriangleSpace.xml': ADVANCED_TRIANGLE_SPACE,
        'choicePointSpace.xml': CHOICE_POINT_SPACE,
        'choiceShapeSpace.xml': CHOICE_SHAPE_SPACE,
        'choiceSpace.xml': CHOICE_SPACE,
        'arraySpace.xml': ARRAY_SPACE,
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
        'choicePointSpace.xml': 'choicePoint',
        'choiceShapeSpace.xml': 'choiceShape',
        'choiceSpace.xml': 'choice',
        'arraySpace.xml': 'array',
    }

    MAPPING = {
        'simpleTriangleSpace.xml': 'triangleMapping.xml',
        'advancedTriangleSpace.xml': 'triangleMapping.xml',
        'choicePointSpace.xml': 'choicePointMapping.xml',
        'choiceShapeSpace.xml': 'choiceShapeMapping.xml',
        'choiceSpace.xml': 'choiceMapping.xml',
        'arraySpace.xml': 'arrayMapping.xml',
    }

    @staticmethod
    def getDesignSpace(fileName,
            codeMappingFactory=PresetCodeMappingFactory.getCodeMapping,
            psFactory=PresetParamStoreFactory.getParamStore):

        mappingFile = PresetDesignSpaceFactory.MAPPING.get(fileName)
        mapping = codeMappingFactory(mappingFile)
        ps = psFactory(fileName, mapping)

        return DesignSpace(ps, PresetDesignSpaceFactory.IDS[fileName], fileName)
