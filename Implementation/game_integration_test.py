import unittest
from mock import Mock

import game
import prng

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
 
        #Create the proxy game objects with game views
        self.view = Mock(spec=game.GameView)
        self.proxy = game.ProxyGame(None)
        self.proxy_dispatcher = game.ProxyDispatcher(None, self.proxy)
        self.proxy.add_view(self.view)

        #Create the utility objects
        self.random = prng.get_random()
        self.dice_roller = game.DiceRoller(self.random)
        self.win_checker = game.WinChecker()
        self.bid_checker = game.BidChecker()
        self.win_handler = game.WinHandler()
        
        #Create the game states from last to first
        self.game_end_state = game.FinishedState(self.proxy_dispatcher, None)
        self.bid_state = game.BidState(self.proxy_dispatcher, self.game_end_state, None)
        self.first_bid_state = game.FirstBidState(self.proxy_dispatcher, self.bid_state, None)
        self.game_start_state = game.GameStartState(self.proxy_dispatcher, self.first_bid_state, self.dice_roller)
        self.game_end_state.restart = self.game_start_state
        self.first_bid_state.restart = self.game_start_state
        self.bid_state = self.game_start_state

        #Create the game object
        self.game = game.Game(self.data_store, self.game_start_state, self.bid_checker, self.win_checker, self.win_handler)
        self.proxy.game = self.game
        self.proxy_dispatcher.game = self.game

def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(GameIntegrationTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
