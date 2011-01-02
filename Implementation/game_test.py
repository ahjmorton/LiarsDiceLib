import unittest
import random

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

    def testAddingDice(self) :
        player = Mock(spec=Player)
        self.subject.add_player(player)
        dice = [1,2,3,4]
        self.subject.set_dice(player, dice)
        self.assertTrue(dice == self.subject.get_dice(player))

    def testAddingDiceWithNoPlayerThrowsException(self) :
        player = Mock(spec=Player)
        dice = [1,2,3,4]
        def caller() :
            self.subject.set_dice(player, dice)
        self.assertRaises(ValueError, caller)
    
    def testAddingBids(self) :
        player = Mock(spec=Player)
        self.subject.add_player(player)
        bid = (2, 4)
        self.subject.set_bid(player, bid)
        self.assertTrue(bid == self.subject.get_bid(player))

    def testAddingDiceWithNoPlayerThrowsException(self) :
        player = Mock(spec=Player)
        bid = (1,2)
        def caller() :
            self.subject.set_bid(player, bid)
        self.assertRaises(ValueError, caller)

class GameObjectTest(unittest.TestCase) :
    
    def setUp(self) :
        self.data = Mock(spec=game.GameData)
        self.state = Mock(spec=game.GameState)
        self.subject = game.Game(self.data, self.state)

    def testStartupStateOfGameObject(self) :
        self.assertTrue(self.subject.get_current_player() is None)
        self.assertTrue(not self.state.on_game_start.called)
        self.assertTrue(not self.data.add_player.called)

    def testStartingAGame(self) :
        player = Mock(spec=Player)
        self.subject.start_game(player)
        self.assertTrue(self.subject.get_current_player() is None)
        self.state.on_game_start.assert_called_with(player)

    def testMakingABid(self) :
        player = Mock(spec=Player)
        self.subject.set_current_player(player)
        bid = (1,2)
        self.subject.make_bid(bid)
        self.state.on_bid.assert_called_with(player, bid)
        self.assertTrue(not self.data.set_bid.called)

    def testMakingAChallenge(self) :
        player = Mock(spec=Player)
        challenge = Mock(spec=Player)
        self.subject.set_current_player(player)
        self.subject.make_challenge(challenge)
        self.state.on_challenge.assert_called_with(challenge, player)

class DiceRollerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.u = 6
        self.l = 1
        self.random = Mock(spec=random.Random)
        self.subject = game.DiceRoller(self.u, self.l, self.random)

    def testRollingDice(self) :
        ret = 3
        self.random.randint.return_value = ret
        val = self.subject.roll_dice()
        self.assertTrue(val is not None)
        self.assertTrue(ret == val)
        self.assertTrue(self.random.randint.called)
        self.assertTrue(self.random.randint.callcount == 1)

class GameStateTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.subject = self.get_subject(self.game)
        
    def get_subject(self, g) :
        return game.GameState(g)

    def testOnGameStart(self) :
        player = Mock(spec=Player)
        def call() :
            self.subject.on_game_start(player)
        self.assertRaises(game.IllegalStateChangeError, call)

    def testOnBid(self) :
        player = Mock(spec=Player)
        bid = (1,2)
        def call() :
            self.subject.on_bid(player, bid)
        self.assertRaises(game.IllegalStateChangeError, call)

    def testOnChallenge(self) :
        player = Mock(spec=Player)
        challenge = Mock(spec=Player)
        bid = (1,2)
        def call() :
            self.subject.on_challenge(challenge, player)
        self.assertRaises(game.IllegalStateChangeError, call)
        
class GameStartStateTest(GameStateTest) :
    
    def get_subject(self, g) :
        self.next_state = Mock(spec=game.GameState)
        self.data = Mock(spec=game.GameData)
        self.game.get_state.return_value = self.data
        self.max_face = 6
        return game.GameStartState(g, self.next_state)

    def testOnGameStart(self) :
        player = Mock(spec=Player)
        players = [player]
        self.data.get_players.return_value = players
        res = self.subject.on_game_start(player)
        self.assertTrue(res is not None)
        self.assertTrue(res is self.next_state)
        self.assertTrue(self.data.get_players.called)


def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(GameDataTest))
    suite.addTests(loader.loadTestsFromTestCase(GameObjectTest))
    suite.addTests(loader.loadTestsFromTestCase(GameStateTest))
    suite.addTests(loader.loadTestsFromTestCase(GameStartStateTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
