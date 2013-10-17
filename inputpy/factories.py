import xml.etree.ElementTree as et
import inputpy.param as param
from inputpy.designspace import DesignSpace
from inputpy.mapping import Mapping, CodeMapping

class XMLFactory:
    @staticmethod
    def getParameter(element, parentId=None, codeMapping=None):
        # Does not yet handle nested parameters.
        args = element.attrib

        if element.tag.endswith('SParam'):
            args['type'] = 'SParam'
            paramId = args['id']
            if parentId is None:
                nextParent = paramId
            else:
                nextParent = parentId + '.' + paramId
            args['nested'] = [
                XMLFactory.getParameter(e, nextParent) for e in element
            ]

        args['parentId'] = parentId
        return param.getParameter(**args)

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
            if e.tag.endswith('Mapping'):
                mappings.append(factory(e))
            elif e.tag.endswith('MappingType'):
                mappingTypes.append(factory(e))
        return CodeMapping(mappings, mappingTypes)

    @staticmethod
    def getParamStore(root, codeMapping=None, paramFactory=None):
        # Does not yet handle nested parameters.
        factory = paramFactory or XMLFactory.getParameter
        return param.ParamStore([factory(e) for e in root])

    @staticmethod
    def getDesignSpace(fileName, codeMappingFactory=None, psFactory=None):
        factory = psFactory or XMLFactory.getParamStore
        cmFactory = codeMappingFactory or XMLFactory.getCodeMapping
        root = et.parse(fileName).getroot()
        codeMapping = root.attrib.get('mapping')
        if codeMapping is not None:
            codeMapping = cmFactory(codeMapping)
        ps = factory(root, codeMapping=codeMapping)
        spaceId = root.get('id')
        return DesignSpace(ps, spaceId, fileName)
