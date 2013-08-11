import unittest
import inputpy.generators as generator
from inputpy.param import Param

class TestGenerators(unittest.TestCase):

    def testGeneratorRandomness(self):
        params = (
            Param('A', 'integer', inclMin=1, inclMax=10),
            Param('A', 'float', inclMin=1, inclMax=10),
            Param('A', 'boolean'),
        )
        for p in params:
            self.checkGeneratorRandomness(p)

    def testGeneratorReturnType(self):
        params = (
            (Param('A', 'short', inclMin=1, inclMax=10), int),
            (Param('A', 'integer', inclMin=1, inclMax=10), int),
            (Param('A', 'long', inclMin=1, inclMax=10), int),
            (Param('A', 'float', inclMin=1, inclMax=10), float),
            (Param('A', 'double', inclMin=1, inclMax=10), float),
            (Param('A', 'numeric', inclMin=1, inclMax=10), float),
            (Param('A', 'boolean', inclMin=1, inclMax=10), bool),
        )
        # Go through parameter-type pairs.
        for pair in params:
            self.assertIsInstance(generator.nextValue(pair[0]), pair[1])

    # Note that this test does not include a float parameter with an
    # exclusive limit.
    def testGeneratorRange(self):
        tests = (
            {
                'param': Param('A', 'short', inclMin=-2, inclMax=0),
                'inclMin': (-2,), 'inclMax': (0,),
            },
            {
                'param': Param('A', 'long', exclMin=1, exclMax=4),
                'inclMin': (2,), 'inclMax': (3,),
            },
            {
                'param': Param('A', 'integer', inclMin=(1,2,), exclMax=(2,4,)),
                'inclMin': (1,2,), 'inclMax': (1,3,),
            },
            {
                'param': Param('A', 'float', inclMin=0.5, inclMax=0.6),
                'inclMin': (0.5,), 'inclMax': (0.6,),
            },
            {
                'param': Param('A', 'boolean'),
                'inclMin': (0,), 'inclMax': (1,),
            },
            {
                'param': Param('A', 'double',
                            inclMin=('Math.cos(Math.pi)','.5/2 + B'),
                            inclMax=(.9,'Math.sqrt(16) + B')),
                'dep': {'B': 3},
                'inclMin': (-1.0,3.25,), 'inclMax': (.9,7,),
            },
        )
        for kwarg in tests:
            self.checkRange(**kwarg)

    def checkGeneratorRandomness(self, param, dep={}, iterations=10):
        self.assertTrue(iterations > 1, msg='1 iteration makes no sense!')
        values = []
        for i in range(iterations):
            value = generator.nextValue(param, dep)
            if len(values) > 0 and value not in values:
                return
            else:
                values.append(value)
        msg = 'No unique value after %d iterations.' % (iterations)
        self.fail(msg)

    # This test always assumes that the range is inclusive.
    def checkRange(self, inclMin, inclMax, param, dep={}, iterations=10):
        self.assertTrue(iterations > 1, msg='1 iteration makes no sense!')
        for i in range(iterations):
            value = generator.nextValue(param, dep)
            result = [
                minLimit <= value <= maxLimit
                for (minLimit, maxLimit) in list(zip(inclMin, inclMax))
            ]
            msg='%s did not match any of the ranges' % (value,)
            self.assertTrue(any(result), msg=msg)


if __name__ == '__main__':
    unittest.main()
