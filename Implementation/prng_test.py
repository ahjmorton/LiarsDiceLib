import unittest
import prng

class RandomModuleTest(unittest.TestCase) :

    def test_getting_random_is_same_object(self) :
        rand1 = prng.get_random()
        rand2 = prng.get_random()
        self.assertTrue(rand1 is rand2)

def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(RandomModuleTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
