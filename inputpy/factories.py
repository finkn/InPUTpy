"""
:copyright: (c) 2013 by Christoffer Fink.
:license: MIT. See LICENSE for details.
"""
import xml.etree.ElementTree as et
import inputpy.param as param
import inputpy.util as util
import inputpy.generators as gen
from inputpy.design import Design
from inputpy.designspace import DesignSpace
from inputpy.mapping import Mapping, CodeMapping, NULL_CODE_MAPPING
from inputpy.paramstore import ParamStore
from inputpy.q import *
from inputpy.exceptions import InPUTException

def getTag(tag):
    index = tag.index('}')
    return tag[index+1:]

class XMLFactory:
    @staticmethod
    def __getParamArgs(element, parentId=None):
        args = element.attrib
        tag = getTag(element.tag)
        if tag == SPARAM or tag == SCHOICE:
            args[TAG] = tag
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
            try:
                mapping = factory(e)
            except:
                continue
            if e.tag.endswith(MAPPING):
                mappings.append(mapping)
            elif e.tag.endswith(MAPPING_TYPE):
                mappingTypes.append(mapping)
        return CodeMapping(mappings, mappingTypes)

    @staticmethod
    def getParamStore(root, codeMapping=None, paramFactory=None):
        factory = paramFactory or XMLFactory.getParameter
        cm = codeMapping
        return ParamStore([factory(e, codeMapping=cm) for e in root])

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

    @staticmethod
    def getDesign(fileName, dsFactory=None):
        dsFactory = dsFactory or XMLFactory.getDesignSpace
        try:
            root = et.parse(fileName).getroot()
        except (FileNotFoundError, TypeError) as e:
            raise InPUTException('Could not import Design: %s' % (e))
        designId = root.attrib.get(ID_ATTR)
        spaceFile = root.attrib.get(REF_ATTR)
        space = dsFactory(spaceFile)
        params = XMLFactory.getParamValues(root, space)
        return Design(params, space, designId)

    @staticmethod
    def getParamValues(root, space):
        result = XMLFactory.getNValues({}, root, space)
        result = XMLFactory.getSValues(result, root, space)
        result = XMLFactory.convertArrays(result, space)
        return result

    @staticmethod
    def convertArrays(values, space):
        elements = XMLFactory.getArrayElements(values, space)
        for key in elements.keys():
            del values[key]
        result = XMLFactory.condense(elements)
        for (k,v) in result.items():
            values[k] = v
        return values

    @staticmethod
    def condense(elements):
        prefixes = {
            id[:id.rfind('.')] for id in elements.keys() if id.rfind('.') != -1
        }
        if len(prefixes) == 0:
            return elements
        results = {prefix: [
                v for (k,v) in elements.items() if k.startswith(prefix + '.')
            ] for prefix in prefixes
        }
        results.update({
            k: v for (k,v) in elements.items() if k.find('.') == -1
        })
        return XMLFactory.condense(results)

    @staticmethod
    def getArrayElements(values, space):
        arrays = XMLFactory.getArrays(space)
        elements = {}
        for a in arrays:
            rootId = a.getId() + '.'
            for k in values.keys():
                if k.startswith(rootId):
                    elements[k] = values[k]
        return elements

    @staticmethod
    def getArrays(space):
        arrays = []
        for k in space.params.getSupportedParamIds():
            p = space.params.getParam(k)
            if p.getTag() == ARRAY:
                arrays.append(p)
        return arrays


    @staticmethod
    def getNValues(values, element, space, parentId=None):
        if element.tag.endswith(DESIGN_ROOT):
            paramId = None
        else:
            paramId = util.absolute(parentId, element.attrib.get(ID_ATTR))

        for e in element:
            values = XMLFactory.getNValues(values, e, space, paramId)

        if element.tag.endswith(NVALUE):
            param = space.params.getParam(paramId)
            value = element.attrib.get(VALUE_ATTR)

            # This happens with arrays, since they do not have a value.
            if value is None:
                return values

            # This should not really happen in production, but some parameters
            # are currently not supported, so we have to skip their values.
            if param is None:
                try:
                    values[paramId] = int(value)
                except:
                    values[paramId] = float(value)
                return values
            values[paramId] = XMLFactory.castValue(param, space, value)
        else:
            for e in element:
                values = XMLFactory.getNValues(values, e, space, paramId)
        return values

    @staticmethod
    def castValue(param, space, value):
        types = {
            SHORT: int, INTEGER: int, LONG: int,
            FLOAT: float, DOUBLE: float, DECIMAL: float,
        }
        type = param.getType()

        if type == BOOLEAN:
            return value.lower() == 'true'

        return types[type](value)

    @staticmethod
    def getSValues(values, element, space, parentId=None):
        if element.tag.endswith(DESIGN_ROOT):
            paramId = None
        else:
            paramId = util.absolute(parentId, element.attrib.get(ID_ATTR))

        for e in element:
            values = XMLFactory.getSValues(values, e, space, paramId)
        if element.tag.endswith(SVALUE):
            param = space.params.getParam(paramId)

            workingId = paramId
            # Could be an array. Try again using the root parameter ID.
            if param is None:
                root = paramId[:paramId.find('.')]
                param = space.params.getParam(root)
                # Hack
                if param is None:
                    return values
                workingId = param.getId()

            if param.getType() == STRING:
                value = element.attrib.get(VALUE_ATTR)
                if value is not None:
                    values[paramId] = value
            else:
                ids = values.keys()
                dep = {}

                # Dear God this is ugly!
                if param.getTag() == CHOICE:
                    choiceName = element.attrib.get(VALUE_ATTR)
                    sparam = param.getOriginal()
                    param = param.getChoice(choiceName)
                    # find schoice
                    schoice = None
                    for d in sparam.getNestedParameters():
                        if d.getRelativeId() == choiceName:
                            schoice = d
                    for d in schoice.getDependees():
                        absolute = util.findAbsoluteParameter(workingId, d, ids)
                        dep[d] = values.get(absolute)

                for d in param.getDependees():
                    absolute = util.findAbsoluteParameter(workingId, d, ids)
                    value = values.get(absolute)
                    if value is not None:
                        dep[d] = value
                    else:
                        absolute = workingId + '.' + d
                        dependee = space.params.getParam(absolute)
                        dep[d] = gen.nextValue(dependee, dep)
                values[paramId] = gen.nextValue(param, dep)
        return values
