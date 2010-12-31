import unittest

from mock import Mock

import game
from player import Player

class GameDataTest(unittest.TestCase) :
    pass

class GameObjectTest(unittest.TestCase) :
    pass

def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(GameDataTest))
    suite.addTests(loader.loadTestsFromTestCase(GameObjectTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
