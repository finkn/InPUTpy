import inputpy.Q as Q
import unittest

class TestQ(unittest.TestCase):
    def testDesignRoot(self):
        self.assertEquals("Design", Q.DESIGN_ROOT)

if __name__ == '__main__':
    unittest.main()
