import inputpy.q as Q
import unittest

class TestQ(unittest.TestCase):
    def testDesignRoot(self):
        self.assertEqual("Design", Q.DESIGN_ROOT)

    # This is a very minimal test.
    def testGetSchemaLocationShouldNotReturnNone(self):
        self.assertIsNotNone(Q.getSchemaLocation())

if __name__ == '__main__':
    unittest.main()
