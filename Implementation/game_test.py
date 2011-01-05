import unittest
import random

from mock import Mock

import game

class GameDataTest(unittest.TestCase) :

    def setUp(self) :
        self.starting = 3
        self.subject = game.GameData(self.starting)

    def testStartingState(self) : 
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(0, len(players))
        self.assertEquals(self.subject.get_num_of_starting_dice(), self.starting)

    def testAddingPlayer(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
        dice = self.subject.get_dice(player)
        self.assertTrue(dice is None)
        bid = self.subject.get_bid(player)
        self.assertTrue(bid is None)
        players = self.subject.get_all_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
    
    def testRemovingPlayer(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
        players = self.subject.get_all_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
        self.subject.remove_player(player)        
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(0, len(players))
        players = self.subject.get_all_players()
        self.assertTrue(players is not None)
        self.assertEquals(0, len(players))

    def testAddingDice(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        dice = [1,2,3,4]
        self.subject.set_dice(player, dice)
        self.assertTrue(dice == self.subject.get_dice(player))

    def testMakingPlayerInactive(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        self.subject.mark_inactive(player)
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(0, len(players))
        self.assertTrue(players is not None)
        players = self.subject.get_all_players()
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)

    def testMakingPlayerInactiveThenReactivating(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        self.subject.mark_inactive(player)
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(0, len(players))
        players = self.subject.get_all_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
        self.subject.make_all_active()        
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)
        players = self.subject.get_all_players()
        self.assertTrue(players is not None)
        self.assertEquals(1, len(players))
        self.assertTrue(player in players)

    def testAddingDiceWithNoPlayerThorwsException(self) :
        player = Mock(spec=game.Player)
        dice = [1,2,3,4]
        def caller() :
            self.subject.set_dice(player, dice)
        self.assertRaises(ValueError, caller)
    
    def testAddingBids(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        bid = (2, 4)
        self.subject.set_bid(player, bid)
        self.assertTrue(bid == self.subject.get_bid(player))

    def testAddingDiceWithNoPlayerThorwsException(self) :
        player = Mock(spec=game.Player)
        bid = (1,2)
        def caller() :
            self.subject.set_bid(player, bid)
        self.assertRaises(ValueError, caller)

class GameObjectTest(unittest.TestCase) :
    
    def setUp(self) :
        self.data = Mock(spec=game.GameData)
        self.state = Mock(spec=game.GameState)
        self.dice_check = Mock(spec=game.BidChecker)
        self.subject = game.Game(self.data, self.state, self.dice_check)

    def testStartupStateOfGameObject(self) :
        self.assertTrue(self.subject.get_current_player() is None)
        self.assertTrue(not self.state.on_game_start.called)
        self.assertTrue(not self.data.add_player.called)

    def testStartingAGame(self) :
        player = Mock(spec=game.Player)
        self.subject.start_game(player)
        self.assertTrue(self.subject.get_current_player() is None)
        self.state.on_game_start.assert_called_with(player)

    def testMakingABid(self) :
        player = Mock(spec=game.Player)
        self.subject.set_current_player(player)
        bid = (1,2)
        self.subject.make_bid(bid)
        self.state.on_bid.assert_called_with(player, bid)
        self.assertTrue(not self.data.set_bid.called)

    def testMakingAChallenge(self) :
        player = Mock(spec=game.Player)
        challenge = Mock(spec=game.Player)
        self.subject.set_current_player(player)
        self.subject.make_challenge(challenge)
        self.state.on_challenge.assert_called_with(challenge, player)

    def testGettingNextPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.subject.set_current_player(players[0])
        ret = self.subject.get_next_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[1], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingNextPlayerOnLastPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.subject.set_current_player(players[4])
        ret = self.subject.get_next_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)
    
    def testGettingPreviousPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.subject.set_current_player(players[4])
        ret = self.subject.get_previous_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[3], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousPlayerOnFirstPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.subject.set_current_player(players[0])
        ret = self.subject.get_previous_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[4], ret)
        self.assertTrue(self.data.get_players.called)
    
    def testGettingNextPlayerWithOnePlayer(self) :
        players = [Mock(spec=game.Player)]
        self.data.get_players.return_value = players
        self.subject.set_current_player(players[0])
        ret = self.subject.get_next_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousPlayerWithOnePlayer(self) :
        players = [Mock(spec=game.Player)]
        self.data.get_players.return_value = players
        self.subject.set_current_player(players[0])
        ret = self.subject.get_previous_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousBid(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 2)]
        bid = (1,2)
        self.data.get_players.return_value = players
        self.data.get_bid.return_value = bid
        self.subject.set_current_player(players[1])
        ret = self.subject.get_previous_bid()
        self.assertTrue(ret is not None)
        self.assertEquals(bid, ret)
        self.data.get_bid.assert_called_with(players[0])

    def testBidChecking(self) :
        dice_dict = dict()
        exp = True
        self.data.get_dice_map.return_value = dice_dict
        self.dice_check.check_bids.return_value = exp
        bid = (1, 2)
        ret = self.subject.true_bid(bid)
        self.assertTrue(ret is not None)
        self.assertTrue(exp == ret)
        self.assertTrue(self.data.get_dice_map.called)
        self.dice_check.check_bids.assert_called_with(bid, dice_dict)

    def testRemovingDice(self) :
        length = 4
        ret_list = [1 for x in xrange(0, length)]
        player = Mock(spec=game.Player)
        self.data.get_dice.return_value = ret_list
        self.subject.remove_dice(player)
        self.data.get_dice.assert_called_with(player)
        self.assertTrue(self.data.set_dice.called)
        self.assertEquals(length - 1, len(self.data.set_dice.call_args[0][1]))

class BidCheckerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.subject = game.BidChecker()

    def testCheckingBidSimple(self) :
        player = Mock(spec=game.Player)
        bid = (2,4)
        dice_map = {player:[2,4,4]}
        ret = self.subject.check_bids(bid, dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(ret)
    
    def testCheckingBidNegative(self) :
        player = Mock(spec=game.Player)
        bid = (2,4)
        dice_map = {player:[2,4]}
        ret = self.subject.check_bids(bid, dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(not ret) 

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
    
    def testRollingSetOfDice(self) :
        ret = 3
        amount = 6
        self.random.randint.return_value = ret
        val = self.subject.roll_set_of_dice(amount)
        self.assertTrue(val is not None)
        self.assertTrue(len(val) == amount)
        self.assertTrue(reduce(lambda x, y: x and (y == ret), val, True))

class GameStateTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.subject = self.get_subject(self.game)
        
    def get_subject(self, g) :
        return game.GameState(g)

    def testOnGameStart(self) :
        player = Mock(spec=game.Player)
        def call() :
            self.subject.on_game_start(player)
        self.assertRaises(game.IllegalStateChangeError, call)

    def testOnBid(self) :
        player = Mock(spec=game.Player)
        bid = (1,2)
        def call() :
            self.subject.on_bid(player, bid)
        self.assertRaises(game.IllegalStateChangeError, call)

    def testOnChallenge(self) :
        player = Mock(spec=game.Player)
        challenge = Mock(spec=game.Player)
        bid = (1,2)
        def call() :
            self.subject.on_challenge(challenge, player)
        self.assertRaises(game.IllegalStateChangeError, call)

class FirstBidGameStateTest(GameStateTest) :
    
    def get_subject(self, g) :
        self.first = Mock(spec=game.GameState)
        self.next_state = Mock(spec=game.GameState)
        return game.FirstBidState(g, self.next_state, self.first)

    def testOnGameStart(self) :
        mock_state = Mock(spec=game.GameState)
        player = Mock(spec=game.Player)
        self.first.on_game_start.return_value = mock_state
        ret = self.subject.on_game_start(player)
        self.assertTrue(ret is not None)
        self.first.on_game_start.assert_called_with(player)
        self.assertTrue(ret == mock_state)

    def testOnBid(self) :
        bid = (1,2)
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.game.get_next_player.return_value = player2
        ret = self.subject.on_bid(player, bid)
        self.assertTrue(ret is not None)
        self.game.set_bid.assert_called_with(player, bid)
        self.game.set_current_player.assert_called_with(player2)

class BidGameStateTest(GameStateTest) :
    def get_subject(self, g) :
        self.first = Mock(spec=game.GameState)
        self.next_state = Mock(spec=game.GameState)
        return game.BidState(g, self.next_state, self.first)

    def testOnGameStart(self) :
        mock_state = Mock(spec=game.GameState)
        player = Mock(spec=game.Player)
        self.first.on_game_start.return_value = mock_state
        ret = self.subject.on_game_start(player)
        self.assertTrue(ret is not None)
        self.first.on_game_start.assert_called_with(player)
        self.assertTrue(ret == mock_state)

    def testOnBid(self) :
        cur_bid = (3, 4)
        prev_bid = (1, 2)
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.game.get_previous_bid.return_value = prev_bid
        self.game.get_next_player.return_value = player2
        ret = self.subject.on_bid(player, cur_bid)
        self.assertTrue(ret is not None)
        self.assertTrue(ret == self.next_state)
        self.game.set_bid.assert_called_with(player, cur_bid)
        self.game.set_current_player.assert_called_with(player2)

    def testOnBidThrowsIllegalBidException(self) :
        test_bid1 = (4, 3)
        test_bid2 = (3, 6)
        prev_bid = (4, 4)
        player = Mock(spec=game.Player)
        self.game.get_previous_bid.return_value = prev_bid
        def call() :
            self.subject.on_bid(player, test_bid1)
        self.assertRaises(game.IllegalBidError, call)
        def call() :
            self.subject.on_bid(player, test_bid2)
        self.assertRaises(game.IllegalBidError, call)
    
    def testOnChallenge(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = True
        self.game.get_previous_bid.return_value = cur_bid
        self.game.finished.return_value = False
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is not None)
        self.assertTrue(ret == self.subject)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player2, player1, cur_bid)

    def testOnChallengeNegativeRepeats(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = False
        self.game.get_previous_bid.return_value = cur_bid
        self.game.finished.return_value = False
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is not None)
        self.assertTrue(ret == self.subject)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player1, player2, cur_bid)

    def testOnChallengeToFinalState(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = True
        self.game.get_previous_bid.return_value = cur_bid
        self.game.finished.return_value = True
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is not None)
        self.assertTrue(ret == self.next_state)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player2, player1, cur_bid)

    def testOnChallengeNegativeToFinalState(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = False
        self.game.get_previous_bid.return_value = cur_bid
        self.game.finished.return_value = True
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is not None)
        self.assertTrue(ret == self.next_state)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player1, player2, cur_bid)
        
class GameStartStateTest(GameStateTest) :
    
    def get_subject(self, g) :
        self.dice_roll = Mock(spec=game.DiceRoller)
        self.next_state = Mock(spec=game.GameState)
        self.max_face = 6
        return game.GameStartState(g, self.next_state, self.dice_roll)

    def testOnGameStart(self) :
        player = Mock(spec=game.Player)
        self.game.has_player.return_value = True
        self.game.get_players.return_value = []
        res = self.subject.on_game_start(player)
        self.assertTrue(res is not None)
        self.assertTrue(res is self.next_state)
        self.assertTrue(self.game.has_player.called)
        self.game.set_current_player.assert_called_with(player)
    
    def testOnGameStartShufflesDice(self) :
        player = Mock(spec=game.Player)
        players = [player] + [Mock(spec=game.Player) for i in xrange(1, 4)]
        self.game.get_players.return_value = players
        ret_dice = [1,2,3,4,5,6]
        self.game.has_player.return_value = True
        self.game.number_of_starting_dice.return_value = 6
        self.dice_roll.roll_set_of_dice.return_value = ret_dice
        res = self.subject.on_game_start(player)
        self.assertTrue(res is not None)
        self.assertTrue(res is self.next_state)
        self.assertTrue(self.game.has_player.called) 
        self.assertTrue(self.game.number_of_starting_dice.called)
        self.assertTrue(self.dice_roll.roll_set_of_dice.called)
        self.assertEquals(len(players), self.dice_roll.roll_set_of_dice.call_count)
        self.assertTrue(self.game.set_dice.called)
        self.assertEquals(len(players), self.game.set_dice.call_count)
        full_call_args = self.game.set_dice.call_args_list
        for x in players :
            self.assertTrue(((x, ret_dice), {}) in full_call_args)

class FinalGameStateTest(GameStateTest) :
    def get_subject(self, g) :
        self.first = Mock(spec=game.GameState)
        return game.FinishedState(g, self.first)

    def testOnGameStart(self) :
        mock_state = Mock(spec=game.GameState)
        player = Mock(spec=game.Player)
        self.first.on_game_start.return_value = mock_state
        ret = self.subject.on_game_start(player)
        self.assertTrue(ret is not None)
        self.first.on_game_start.assert_called_with(player)
        self.assertTrue(ret == mock_state)

def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(GameDataTest))
    suite.addTests(loader.loadTestsFromTestCase(GameObjectTest))
    suite.addTests(loader.loadTestsFromTestCase(GameStateTest))
    suite.addTests(loader.loadTestsFromTestCase(GameStartStateTest))
    suite.addTests(loader.loadTestsFromTestCase(FirstBidGameStateTest))
    suite.addTests(loader.loadTestsFromTestCase(BidCheckerTest))
    suite.addTests(loader.loadTestsFromTestCase(BidGameStateTest))
    suite.addTests(loader.loadTestsFromTestCase(FinalGameStateTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
