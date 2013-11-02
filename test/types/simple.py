class EmptyClass:
    def __eq__(self, other):
        return isinstance(other, type(self))

class Empty1(EmptyClass): pass
class Empty2(EmptyClass): pass
class Empty3(EmptyClass): pass

class NonEmptyClass:
    def __init__(self, obj): self.obj = obj
    def getObject(self): return self.obj

class NonEmpty1(NonEmptyClass):
    def __init__(self, obj):
        if not isinstance(obj, int):
            raise ValueError('NonEmpty1 expects integers')
        else:
            NonEmptyClass.__init__(self, obj)

class NonEmpty2(NonEmptyClass):
    def __init__(self, obj):
        if not isinstance(obj, float):
            raise ValueError('NonEmpty2 expects floats')
        else:
            NonEmptyClass.__init__(self, obj)
