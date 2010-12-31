import unittest

from mock import Mock

import game
from player import Player

class GameDataTest(unittest.TestCase) :

    def setUp(self) :
        self.subject = game.GameData()

    def testStartingState(self) : 
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(0, len(players))

    def testAddingPlayer(self) :
        player = Mock(spec=Player)
        self.subject.add_player(player)
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
        dice = self.subject.get_dice(player)
        self.assertTrue(dice is None)
        bid = self.subject.get_bid(player)
        self.assertTrue(bid is None)


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
