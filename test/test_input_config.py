import inputpy.config as config
import inputpy.q as Q
import unittest

DESIGN_FILE = "testDesign.xml"

class TestInPUTConfig(unittest.TestCase):

    @unittest.skip("Not implemented yet.")
    def testGetValue(self):
        from random import Random
        rand = Random()
        value = config.getValue(Q.RANDOM)
        # Change assertTrue to assertIsInstance.
        self.assertTrue(isinstance(value, type(rand)))
        self.fail("Not implemented yet.")

    @unittest.skip("Not implemented yet.")
    def testIsLoggingActive(self):
        logging = config.isLoggingActive()
        loggingValue = config.getValue(Q.LOGGING)
        self.assertEquals(loggingValue, logging)

    @unittest.skip("Not implemented yet.")
    def testIsThreadSafe(self):
        threadSafe = config.isThreadSafe()
        threadSafeValue = config.getValue(Q.THREAD_SAFE)
        self.assertEquals(threadSafeValue, threadSafe)

    @unittest.skip("Not implemented yet.")
    def testIsInjectionActive(self):
        injection = config.isInjectionActive()
        injectionValue = config.getValue(Q.INJECTION)
        self.assertEquals(injectionValue, injection)

if __name__ == '__main__':
    unittest.main()
