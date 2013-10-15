"""
test.tools

Exports fake factories for "importing" known configurations.
"""
from inputpy.designspace import DesignSpace
from inputpy.param import ParamStore
from inputpy.param import getParameter
from inputpy.param import paramFactory
from inputpy.mapping import Mapping
from inputpy.mapping import CodeMapping
from inputpy.q import *

class PresetCodeMappingFactory:

    SIMPLE_TRIANGLE_PMAP = [
        Mapping('P1', 'Point'),
        Mapping('P4', 'Point'),
        Mapping('T1', 'Triangle'),
        Mapping('T2', 'Triangle'),
        Mapping('T1.P1', 'Point'),
        Mapping('T1.P2', 'Point'),
        Mapping('T1.P3', 'Point'),
        Mapping('T2.P1', 'Point'),
        Mapping('T2.P2', 'Point'),
        Mapping('T2.P3', 'Point'),
    ]

    SIMPLE_TRIANGLE_MAPT = [
        Mapping('Point', 'test.types.geo.Point', constructor='X Y'),
        Mapping('Triangle', 'test.types.geo.Triangle', constructor='P1 P2 P3'),
    ]

    MAPPINGS = {
        'triangleMapping.xml': (SIMPLE_TRIANGLE_PMAP, SIMPLE_TRIANGLE_MAPT),
    }

    @staticmethod
    def getCodeMapping(fileName):
        return CodeMapping(*(PresetCodeMappingFactory.MAPPINGS[fileName]))

class PresetParamStoreFactory:
    # Trying to compress the arguments.
    ID = ID_ATTR
    TYPE = TYPE_ATTR
    INT = 'integer'
    IMIN = INCL_MIN
    IMAX = INCL_MAX
    NESTED = 'nested'
    SP = SPARAM

    SIMPLE_INTEGER_SPACE = [
        getParameter('A', 'integer'),
        getParameter('B', 'integer', inclMin='1'),
        getParameter('C', 'integer', inclMax='1'),
        getParameter('D', 'integer', exclMin='1'),
        getParameter('E', 'integer', exclMax='1'),
        getParameter('F', 'integer', inclMin='1', inclMax='3'),
        getParameter('G', 'integer', exclMin='1', exclMax='3'),
        getParameter('H', 'integer', inclMin='1', exclMax='3'),
        getParameter('I', 'integer', exclMin='1', inclMax='3'),
        getParameter('J', 'integer', exclMin='0', inclMax='3'),
        getParameter('K', 'integer', exclMin='-1', inclMax='0'),
        getParameter('L', 'integer', inclMin='0', inclMax='0'),
        getParameter('M', 'integer', fixed='43'),
        getParameter('N', 'integer', inclMin='1', fixed='43'),
        getParameter('O', 'integer', inclMin='1', inclMax='3', fixed='43'),
        getParameter('P', 'integer', fixed='2.9'),
        getParameter('Q', 'integer', inclMin='0.1', inclMax='1.9'),
    ]

    ADVANCED_INTEGER_SPACE = [
        getParameter('A', 'integer', inclMin='1 + 2'),
        getParameter('B', 'integer', inclMin='(1 + 2) + 3'),
        getParameter('C', 'integer', inclMin='4 * 3 / 2 + 1 - (2 + 3)'),
        getParameter('D', 'integer', inclMin='4 * (3 / (2 + 1)) - 2 + 3'),
        getParameter('E', 'integer', inclMin='(4 * 3) / (2 + (-1 - (1 - 3)))'),
        getParameter('F', 'integer', inclMin='(4*3)/(2+(-1-(1-3)))'),
        getParameter('G', 'integer', inclMin='Math.cos(Math.pi)'),
        getParameter('H', 'integer', inclMin='Math.exp(Math.cos(Math.pi*2)) / (Math.e * 2)'),
        getParameter('I', 'integer', inclMin='Y'),
        getParameter('J', 'integer', inclMin='Z'),
        getParameter('K', 'integer', inclMin='Z + Y'),
        getParameter('L', 'integer', inclMin='(Z + Y) * Z / ((4 + Y) - Z)'),
        getParameter('M', 'integer', inclMin='Math.exp(Math.cos(Z*2)) / (Math.e * Y)'),
        getParameter('N', 'integer', fixed='1 + 2'),
        getParameter('O', 'integer', inclMin='(4 * 3) / (2 + (-1 - (1 - 3)))'),
        getParameter('P', 'integer', inclMin='Math.exp(Math.cos(Math.pi*2)) / (Math.e * 2)'),
        getParameter('Y', 'integer', inclMin='2', inclMax='2'),
        getParameter('Z', 'integer', fixed='2'),
    ]

    SIMPLE_TRIANGLE_SPACE = (
        {ID: 'X', TYPE: INT, IMIN: '0', IMAX: '0'},
        {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
        {ID: 'P1', TYPE: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Y', TYPE: INT, IMIN: '3', IMAX: '3'},
        ), },
        {ID: 'P4', TYPE: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '4', IMAX: '4'},
            {ID: 'Y', TYPE: INT, IMIN: '8', IMAX: '8'},
        ), },
        {ID: 'T1', TYPE: SP, NESTED: (
            {ID: 'P1', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
            {ID: 'P2', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '5', IMAX: '5'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
        ), },
        {ID: 'T2', TYPE: SP, NESTED: (
            {ID: 'P1', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
            {ID: 'P2', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TYPE: SP, NESTED: (
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
        {ID: 'P1', TYPE: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '4', IMAX: '4'},
            {ID: 'Y', TYPE: INT, IMIN: 'X + 1', IMAX: 'X + 1'},
        ), },
        {ID: 'P4', TYPE: SP, NESTED: (
            {ID: 'X', TYPE: INT, IMIN: '2', IMAX: '2'},
            {ID: 'Y', TYPE: INT, IMIN: 'X + 1', IMAX: 'X + 1'},
        ), },
        {ID: 'T1', TYPE: SP, NESTED: (
            {ID: 'P1', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: 'T2.P2.X + 1', IMAX: 'T2.P2.X + 1'},
            ), },
            {ID: 'P2', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '5', IMAX: '5'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
        ), },
        {ID: 'T2', TYPE: SP, NESTED: (
            {ID: 'P1', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '1', IMAX: '1'},
                {ID: 'Y', TYPE: INT, IMIN: '1', IMAX: '1'},
            ), },
            {ID: 'P2', TYPE: SP, NESTED: (
                {ID: 'X', TYPE: INT, IMIN: '3', IMAX: '3'},
                {ID: 'Y', TYPE: INT, IMIN: '2', IMAX: '2'},
            ), },
            {ID: 'P3', TYPE: SP, NESTED: (
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
        newStyleStores = (
            'simpleTriangleSpace.xml', 'advancedTriangleSpace.xml'
        )
        if fileName not in newStyleStores:
            return ParamStore(PresetParamStoreFactory.STORES[fileName])

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
        'simpleTriangleMapping.xml': 'triangleMapping.xml',
        'advancedTriangleMapping.xml': 'triangleMapping.xml',
    }

    @staticmethod
    def getDesignSpace(fileName, codeMappingFactory=PresetCodeMappingFactory,
             psFactory=PresetParamStoreFactory):
        mappingFile = PresetDesignSpaceFactory.MAPPING.get(fileName)
        mapping = None
        if mapping is not None:
            mapping = codeMappingFactory(mappingFile)
        ps = psFactory.getParamStore(fileName, mapping)

        return DesignSpace(ps, PresetDesignSpaceFactory.IDS[fileName], fileName)
