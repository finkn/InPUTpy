"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import xml.etree.ElementTree as et
import inputpy.param as param
import inputpy.util as util
from inputpy.designspace import DesignSpace
from inputpy.mapping import Mapping, CodeMapping, NULL_CODE_MAPPING
from inputpy.q import *

class XMLFactory:
    @staticmethod
    def __getParamArgs(element, parentId=None):
        args = element.attrib
        if element.tag.endswith(SPARAM):
            args[TAG] = SPARAM
            paramId = args[ID_ATTR]
            nextParent = util.absolute(parentId, paramId)
            args[NESTED] = [
                XMLFactory.__getParamArgs(e, nextParent) for e in element
            ]

        args[PARENT_ID] = parentId
        return args

    @staticmethod
    def getParameter(element, codeMapping=None):
        cm = codeMapping or NULL_CODE_MAPPING
        return param.paramFactory(XMLFactory.__getParamArgs(element), cm)

    @staticmethod
    def getMapping(element):
        return Mapping(**element.attrib)

    @staticmethod
    def getCodeMapping(fileName, mappingFactory=None):
        factory = mappingFactory or XMLFactory.getMapping
        root = et.parse(fileName).getroot()
        mappings = []
        mappingTypes = []
        for e in root:
            if e.tag.endswith(MAPPING):
                mappings.append(factory(e))
            elif e.tag.endswith(MAPPING_TYPE):
                mappingTypes.append(factory(e))
        return CodeMapping(mappings, mappingTypes)

    @staticmethod
    def getParamStore(root, codeMapping=None, paramFactory=None):
        factory = paramFactory or XMLFactory.getParameter
        cm = codeMapping
        return param.ParamStore([factory(e, codeMapping=cm) for e in root])

    @staticmethod
    def getDesignSpace(fileName, codeMappingFactory=None, psFactory=None):
        factory = psFactory or XMLFactory.getParamStore
        cmFactory = codeMappingFactory or XMLFactory.getCodeMapping
        root = et.parse(fileName).getroot()
        codeMapping = root.attrib.get(MAPPING_ATTR)
        if codeMapping is not None:
            codeMapping = cmFactory(codeMapping)
        ps = factory(root, codeMapping=codeMapping)
        spaceId = root.get(ID_ATTR)
        return DesignSpace(ps, spaceId, fileName)
