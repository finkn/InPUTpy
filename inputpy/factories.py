import xml.etree.ElementTree as et
import inputpy.param as param
from inputpy.designspace import DesignSpace

class XMLFactory:
    @staticmethod
    def getParameter(element):
        return param.getParameter(**element.attrib)

    @staticmethod
    def getParamStore(root, paramFactory=None):
        factory = paramFactory or XMLFactory.getParameter
        return param.ParamStore([factory(e) for e in root])

    @staticmethod
    def getDesignSpace(fileName, psFactory=None):
        factory = psFactory or XMLFactory.getParamStore
        root = et.parse(fileName).getroot()
        ps = factory(root)
        spaceId = root.get('id')
        return DesignSpace(ps, spaceId, fileName)
