class SomeStructural:
    pass

class SomeCommonStructural(SomeStructural):
    def __init__(self):
        self.wrapper = None

    def setPrimitive(self, wrapper):
        self.wrapper = wrapper

    def getPrimitive(self):
        return self.wrapper

class SomeFirstChoice(SomeCommonStructural):
    pass

class SomeSecondChoice(SomeCommonStructural):
    pass

class SomeSharedStructuralSub:
    pass

class SomeSubChoice(SomeSharedStructuralSub):
    pass

class AnotherSubChoice(SomeSharedStructuralSub):
    pass

class AnotherStructuralParent:
    def __init__(self, sub):
        self.sub = sub

    def getSomeSharedStructuralSub(self):
        return self.sub

class SomeAbstractComplexStructural:
    pass

class SomeComplexStructural(SomeAbstractComplexStructural):
    def __init__(self):
        self.items = []

    def addEntry(self, item):
        self.items.append(item)

    def getEntry(self, index):
        return self.items[index]

    def size(self):
        return len(self.items)

class SingleComplexChoice(SomeAbstractComplexStructural):
    def __init__(self, a=0.0):
        self.a = a

    def getA(self):
        return self.a

class SecondSingleComplexChoice(SingleComplexChoice):
    pass

class Wrapper:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Wrapper):
            return self.value == other.value
        else:
            return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        else:
            return result

    def toValue(self):
        return self.value
