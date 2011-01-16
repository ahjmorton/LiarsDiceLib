import unittest
from mock import Mock

import game

class GameIntegrationTest(unittest.TestCase) :
    
    def setUp(self) :
        
        #Initialise players
        self.player1 = Mock(spec=game.Player)
        self.player2 = Mock(spec=game.Player)
        self.player1name = "Player1"
        self.player2name = "Player2"
        self.player1.get_name.return_value = player1name
        self.player2.get_name.return_value = player2name

        #Initialise game data store and add players
        self.starting_dice = 3
        self.lowest_face = 1
        self.highest_face = 6
        self.data_store = game.GameData(self.starting_dice, self.lowest_face, self.highest_face)
        self.data_store.add_player(self.player1)
        self.data_store.add_player(self.player2)




def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(GameIntegrationTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
