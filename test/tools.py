"""
test.tools

Exports fake factories for "importing" known configurations.
"""
from inputpy.designspace import DesignSpace
from inputpy.param import ParamStore
from inputpy.param import getParameter
from inputpy.mapping import Mapping
from inputpy.mapping import CodeMapping

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
    SIMPLE_INTEGER_PARAM_SPACE = [
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

    ADVANCED_INTEGER_PARAM_SPACE = [
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

    mapping = PresetCodeMappingFactory.getCodeMapping('triangleMapping.xml')
    # With relative names, with parent.
    SIMPLE_TRIANGLE_PARAM_SPACE = [
        # Outer X and Y.
        getParameter('X', 'integer', inclMin='0', inclMax='0'),
        getParameter('Y', 'integer', inclMin='1', inclMax='1'),
        # Outer P1 and P4.
        getParameter('P1', 'SParam', nested=[
            getParameter(
                'X', 'integer', inclMin='2', inclMax='2', parentId='P1'
            ),
            getParameter(
                'Y', 'integer', inclMin='3', inclMax='3', parentId='P1'
            ),
        ], mapping=mapping.getMapping('P1')),
        getParameter('P4', 'SParam', nested=[
            getParameter(
                'X', 'integer', inclMin='4', inclMax='4', parentId='P4'
            ),
            getParameter(
                'Y', 'integer', inclMin='8', inclMax='8', parentId='P4'
            ),
        ], mapping=mapping.getMapping('P4')),
        # Outer T1.
        getParameter('T1', 'SParam', nested=[
            getParameter('P1', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='1', inclMax='1', parentId='T1.P1'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T1.P1'
                ),
            ], mapping=mapping.getMapping('T1.P1'), parentId='T1'),
            getParameter('P2', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='3', inclMax='3', parentId='T1.P2'
                ),
                getParameter(
                    'Y', 'integer', inclMin='2', inclMax='2', parentId='T1.P2'
                ),
            ], mapping=mapping.getMapping('T1.P2'), parentId='T1'),
            getParameter('P3', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='5', inclMax='5', parentId='T1.P3'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T1.P3'
                ),
            ], mapping=mapping.getMapping('T1.P3'), parentId='T1'),
        ], mapping=mapping.getMapping('T1')),
        # Outer T2.
        getParameter('T2', 'SParam', nested=[
            getParameter('P1', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='1', inclMax='1', parentId='T2.P1'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T2.P1'
                ),
            ], mapping=mapping.getMapping('T2.P1'), parentId='T2'),
            getParameter('P2', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='3', inclMax='3', parentId='T2.P2'
                ),
                getParameter(
                    'Y', 'integer', inclMin='2', inclMax='2', parentId='T2.P2'
                ),
            ], mapping=mapping.getMapping('T2.P2'), parentId='T2'),
            getParameter('P3', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='5', inclMax='5', parentId='T2.P3'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T2.P3'
                ),
            ], mapping=mapping.getMapping('T2.P3'), parentId='T2'),
        ], mapping=mapping.getMapping('T2')),
    ]

    # This config is subject to change. It's supposed to include a wide
    # variety of different dependencies, which isn't the case now.
    ADVANCED_TRIANGLE_PARAM_SPACE = [
        # Outer X and Y.
        getParameter('X', 'integer', inclMin='0', inclMax='0'),
        getParameter('Y', 'integer', inclMin='X + 1', inclMax='X + 1'),
        # Outer P1 and P4.
        getParameter('P1', 'SParam', nested=[
            getParameter(
                'X', 'integer', inclMin='4', inclMax='4', parentId='P1'
            ),
            getParameter(
                'Y', 'integer', inclMin='X + 1', inclMax='X + 1', parentId='P1'
            ),
        ], mapping=mapping.getMapping('P1')),
        getParameter('P4', 'SParam', nested=[
            getParameter(
                'X', 'integer', inclMin='2', inclMax='2', parentId='P4'
            ),
            getParameter(
                'Y', 'integer', inclMin='X + 1', inclMax='X + 1', parentId='P4'
            ),
        ], mapping=mapping.getMapping('P4')),
        # Outer T1.
        getParameter('T1', 'SParam', nested=[
            getParameter('P1', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='1', inclMax='1', parentId='T1.P1'
                ),
                getParameter(
                    'Y', 'integer', inclMin='T2.P2.X + 1', inclMax='T2.P2.X + 1', parentId='T1.P1'
                ),
            ], mapping=mapping.getMapping('T1.P1'), parentId='T1'),
            getParameter('P2', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='3', inclMax='3', parentId='T1.P2'
                ),
                getParameter(
                    'Y', 'integer', inclMin='2', inclMax='2', parentId='T1.P2'
                ),
            ], mapping=mapping.getMapping('T1.P2'), parentId='T1'),
            getParameter('P3', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='5', inclMax='5', parentId='T1.P3'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T1.P3'
                ),
            ], mapping=mapping.getMapping('T1.P3'), parentId='T1'),
        ], mapping=mapping.getMapping('T1')),
        # Outer T2.
        getParameter('T2', 'SParam', nested=[
            getParameter('P1', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='1', inclMax='1', parentId='T2.P1'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T2.P1'
                ),
            ], mapping=mapping.getMapping('T2.P1'), parentId='T2'),
            getParameter('P2', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='3', inclMax='3', parentId='T2.P2'
                ),
                getParameter(
                    'Y', 'integer', inclMin='2', inclMax='2', parentId='T2.P2'
                ),
            ], mapping=mapping.getMapping('T2.P2'), parentId='T2'),
            getParameter('P3', 'SParam', nested=[
                getParameter(
                    'X', 'integer', inclMin='5', inclMax='5', parentId='T2.P3'
                ),
                getParameter(
                    'Y', 'integer', inclMin='1', inclMax='1', parentId='T2.P3'
                ),
            ], mapping=mapping.getMapping('T2.P3'), parentId='T2'),
        ], mapping=mapping.getMapping('T2')),
    ]

    STORES = {
        'simpleIntegerParameterSpace.xml': SIMPLE_INTEGER_PARAM_SPACE,
        'advancedIntegerParameterSpace.xml': ADVANCED_INTEGER_PARAM_SPACE,
        'simpleTriangleSpace.xml': SIMPLE_TRIANGLE_PARAM_SPACE,
        'advancedTriangleSpace.xml': ADVANCED_TRIANGLE_PARAM_SPACE,
    }

    @staticmethod
    def getParamStore(fileName):
        return ParamStore(PresetParamStoreFactory.STORES[fileName])

class PresetDesignSpaceFactory:
    IDS = {
        'simpleIntegerParameterSpace.xml': 'simpleInteger',
        'advancedIntegerParameterSpace.xml': 'advancedInteger',
        'simpleTriangleSpace.xml': 'triangle',
        'advancedTriangleSpace.xml': 'triangle',
    }

    @staticmethod
    def getDesignSpace(fileName, psFactory=PresetParamStoreFactory):
        ps = psFactory.getParamStore(fileName)
        return DesignSpace(ps, PresetDesignSpaceFactory.IDS[fileName], fileName)
