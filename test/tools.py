"""
test.tools

Exports fake factories for "importing" known configurations.
"""
from inputpy.designspace import DesignSpace
from inputpy.param import ParamStore
from inputpy.param import getParameter

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

    STORES = {
        'simpleIntegerParameterSpace.xml': SIMPLE_INTEGER_PARAM_SPACE,
        'advancedIntegerParameterSpace.xml': ADVANCED_INTEGER_PARAM_SPACE,
    }

    @staticmethod
    def getParamStore(fileName):
        return ParamStore(PresetParamStoreFactory.STORES[fileName])

class PresetDesignSpaceFactory:
    IDS = {
        'simpleIntegerParameterSpace.xml': 'simpleInteger',
        'advancedIntegerParameterSpace.xml': 'advancedInteger',
    }

    @staticmethod
    def getDesignSpace(fileName, psFactory=PresetParamStoreFactory):
        ps = psFactory.getParamStore(fileName)
        return DesignSpace(ps, PresetDesignSpaceFactory.IDS[fileName], fileName)
