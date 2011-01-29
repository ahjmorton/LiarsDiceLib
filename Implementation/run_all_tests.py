import unittest

import game_test
import game_integration_test

def suite() :
    return unittest.TestSuite([game_test.suite(), 
           game_integration_test.suite()])

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
