import unittest

import prng_test
import game_test
import game_integration_test

def suite() :
    return unittest.TestSuite([prng_test.suite(), game_test.suite(), game_integration_test.suite()])

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
