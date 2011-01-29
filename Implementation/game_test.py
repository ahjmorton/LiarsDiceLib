import unittest
import random

from mock import Mock

import game

class GameDataTest(unittest.TestCase) :

    def setUp(self) :
        self.starting = 3
        self.subject = game.GameData(self.starting)

    def testSettingPlayer(self) :
        player1 = Mock(spec=game.Player)
        self.subject.set_current_player(player1)
        self.assertEquals(player1, self.subject.get_current_player())
    
    def testSettingState(self) :
        state = Mock(spec=game.GameState)
        self.subject.set_current_state(state)
        self.assertEquals(state, self.subject.get_current_state())

    def testStartingState(self) : 
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(None, self.subject.get_current_player())
        self.assertEquals(None, self.subject.get_current_state())
        self.assertEquals(0, len(players))
        self.assertEquals(self.subject.get_num_of_starting_dice(), self.starting
)

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

    def testCheckingForActive(self) :
        player = Mock(spec=game.Player)
        self.subject.add_player(player)
        self.subject.make_all_active()

        ret = self.subject.is_active(player)

        self.assertTrue(ret)
        self.subject.mark_inactive(player)

        ret = self.subject.is_active(player)

        self.assertTrue(not ret)

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
        self.win_check = Mock(spec=game.WinChecker)
        self.win_hand = Mock(spec=game.WinHandler)
        self.subject = game.Game(self.data, self.dice_check, 
        self.win_check, self.win_hand)

    def testDeactivatePlayer(self) :
        player1 = Mock(spec=game.Player)
        self.subject.deactivate_player(player1)
        self.data.mark_inactive.assert_called_with(player1)

    def testSettingAPlayer(self) :
        player1 = Mock(spec=game.Player)
        self.subject.set_current_player(player1)
        self.data.set_current_player.assert_called_with(player1)

    def testCheckingForFinished(self) :
        player1 = Mock(spec=game.Player)
        dice_map = dict()
        self.win_check.get_winner.return_value = player1
        self.data.get_dice_map.return_value = dice_map
        ret = self.subject.finished()
        self.assertTrue(ret is not None)
        self.assertTrue(ret)
        self.data.get_dice_map.assert_called_with()
        self.win_check.get_winner.assert_called_with(dice_map)
    
    def testCheckingForActive(self) :
        player1 = Mock(spec=game.Player)
        self.data.is_active.return_value = True

        self.assertTrue(self.subject.is_player_active(player1))
        
        self.data.is_active.assert_Called_with(player1)
        self.data.is_active.return_value = False

        self.assertTrue(not self.subject.is_player_active(player1))
           
    def testCheckingForFinishedNegative(self) :
        self.win_check.get_winner.return_value = None
        dice_map = dict()
        self.data.get_dice_map.return_value = dice_map
        ret = self.subject.finished()
        self.assertTrue(ret is not None)
        self.assertTrue(not ret)
        self.data.get_dice_map.assert_called_with()
        self.win_check.get_winner.assert_called_with(dice_map)

    def testStartupStateOfGameObject(self) :
        self.data.get_current_player.return_value = None
        self.assertTrue(self.subject.get_current_player() is None)
        self.data.get_current_state.return_value = self.state
        self.assertTrue(self.subject.get_state() == self.state)
        self.data.get_current_state.assert_called_with()
        self.assertTrue(not self.state.on_game_start.called)
        self.assertTrue(not self.data.add_player.called)

    def testStartingAGame(self) :
        player = Mock(spec=game.Player)
        self.data.get_current_state.return_value = self.state
        self.subject.start_game(player)
        self.data.get_current_player.return_value = None
        self.assertTrue(self.subject.get_current_player() is None)
        self.state.on_game_start.assert_called_with(player)
        self.assertEquals(self.state, self.subject.get_state())

    def testSettingAState(self) :
        state1 = Mock(spec=game.GameState)
        self.subject.set_state(state1)
        self.data.set_current_state.assert_called_with(state1)

    def testMakingABid(self) :
        player = Mock(spec=game.Player)
        self.data.get_current_player.return_value = player
        self.data.get_current_state.return_value = self.state
        bid = (1,2)
        self.subject.make_bid(bid)

        self.data.get_current_state.assert_called_with()
        self.data.get_current_player.assert_called_with()
        self.state.on_bid.assert_called_with(player, bid)
        self.assertTrue(not self.data.set_bid.called)
        self.assertEquals(self.state, self.subject.get_state())

    def testMakingAChallengeWithNoneAndNoneGrabsFromGame(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.data.get_players.return_value = [player1, player2]
        self.data.get_current_player.return_value = player2
        self.data.get_current_state.return_value = self.state

        self.subject.make_challenge()
        self.data.get_current_state.assert_called_with()
        self.data.get_players.assert_called_with()
        self.state.on_challenge.assert_called_with(player2, player1)
        self.assertEquals(self.state, self.subject.get_state())
 
    def testMakingAChallengeWithChallengedParametersDoesNotCall(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.data.get_current_player.return_value = player2
        self.data.get_current_state.return_value = self.state

        self.subject.make_challenge(challenged=player1)
        self.data.get_current_state.assert_called_with()
        self.data.get_current_player.assert_called_with()
        self.assertTrue(not self.data.get_players.called)
        self.state.on_challenge.assert_called_with(player2, player1)
        self.assertEquals(self.state, self.subject.get_state())
    
    def testGettingNextPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_next_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[1], ret)
        self.data.get_players.assert_called_with()
        self.data.get_current_player.assert_called_with()

    def testGettingNextPlayerOnLastPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[4]

        ret = self.subject.get_next_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)
    
    def testGettingPreviousPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[4]

        ret = self.subject.get_previous_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[3], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousPlayerOnFirstPlayer(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_previous_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[4], ret)
        self.assertTrue(self.data.get_players.called)
    
    def testGettingNextPlayerWithOnePlayer(self) :
        players = [Mock(spec=game.Player)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_next_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousPlayerWithOnePlayer(self) :
        players = [Mock(spec=game.Player)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_previous_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousBid(self) :
        players = [Mock(spec=game.Player) for x in xrange(0, 2)]
        bid = (1,2)
        self.data.get_players.return_value = players
        self.data.get_bid.return_value = bid
        self.data.get_current_player.return_value = players[1]

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

    def testWinHandling(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (1,2)
        self.subject.on_win(player1, player2, cur_bid)
        self.win_hand.on_win.assert_called_with(player1, player2, cur_bid)

    def testGettingWinningPlayer(self) :
        player1 = Mock(spec=game.Player)
        ret_map = {player1:[1]}
        self.data.get_dice_map.return_value = ret_map
        self.win_check.get_winner.return_value = player1
        ret = self.subject.get_winning_player()
        self.assertTrue(ret is not None)
        self.assertTrue(ret == player1)
        self.win_check.get_winner.assert_called_with(ret_map)
        self.data.get_dice_map.assert_called_with()

    def testActivatingAllPlayers(self) :
        self.subject.activate_players()
        self.data.make_all_active.assert_called_with()

    def testGettingDiceMap(self) :
        player1 = Mock(spec=game.Player)
        ret_map = {player1:[1]}
        self.data.get_dice_map.return_value = ret_map
        ret = self.subject.get_dice_map()
        self.assertEquals(ret_map, ret)

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

class WinCheckerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.subject = game.WinChecker()

    def testCheckingBidAllNone(self) :
        dice_map = {"a":[1,2,3], "b":[1], "c":[1,4,2]}
        self.assertTrue(self.subject.get_winner(dice_map) is None)


    def testCheckingBidOneWin(self) :
        winner = "a"
        dice_map = {winner:[1,2,3], "b":[], "c":[]}
        ret = self.subject.get_winner(dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(winner == ret)

class WinHandlerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game_obj = Mock(game.Game)
        self.subject = game.WinHandler(self.game_obj)

    def testHandlingWinWithoutMakingPlayerInactive(self) :
        player1 = Mock(game.Player)
        player2 = Mock(game.Player)
        bid = (1,2)
        self.game_obj.get_dice.return_value = [1,2]
        self.subject.on_win(player1, player2, bid)
        self.game_obj.remove_dice.assert_called_with(player2)
        self.game_obj.get_dice.assert_called_with(player2)
        self.game_obj.set_current_player.assert_called_with(player2)

    def testHandlingWinWithMakingPlayerInactive(self) :
        player1 = Mock(game.Player)
        player2 = Mock(game.Player)
        bid = (1,2)
        self.game_obj.get_dice.return_value = []
        self.subject.on_win(player1, player2, bid)
        self.game_obj.remove_dice.assert_called_with(player2)
        self.game_obj.get_dice.assert_called_with(player2)
        self.game_obj.deactivate_player.assert_called_with(player2)
        self.game_obj.set_current_player.assert_called_with(player1)

class DiceRollerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.random = Mock(spec=random.Random)
        self.subject = game.DiceRoller(self.random)

    def testRollingDice(self) :
        ret = 3
        face = (1, 6)
        self.random.randint.return_value = ret
        val = self.subject.roll_dice(face)
        self.assertTrue(val is not None)
        self.assertTrue(ret == val)
        self.assertTrue(self.random.randint.called)
        self.assertTrue(self.random.randint.call_count == 1)
    
    def testRollingSetOfDice(self) :
        ret = 3
        amount = 6
        face = (1, 6)
        self.random.randint.return_value = ret
        val = self.subject.roll_set_of_dice(amount, face)
        self.assertTrue(val is not None)
        self.assertTrue(len(val) == amount)
        self.assertTrue(reduce(lambda x, y: x and (y == ret), val, True))
        self.assertTrue(self.random.randint.called)
        self.assertTrue(self.random.randint.call_count == amount)

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
        player = Mock(spec=game.Player)
        ret = self.subject.on_game_start(player)
        self.assertTrue(ret is None)
        self.first.on_game_start.assert_called_with(player)

    def testOnBid(self) :
        bid = (1,2)
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.game.get_next_player.return_value = player2
        ret = self.subject.on_bid(player, bid)
        self.assertTrue(ret is None)
        self.game.set_state.assert_called_with(self.next_state)
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
        self.assertTrue(ret is None)
        self.first.on_game_start.assert_called_with(player)

    def testOnBid(self) :
        cur_bid = (3, 4)
        prev_bid = (1, 2)
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.game.get_previous_bid.return_value = prev_bid
        self.game.get_next_player.return_value = player2
        ret = self.subject.on_bid(player, cur_bid)
        self.assertTrue(ret is None)
        self.assertTrue(not self.game.set_state.called)
        self.game.set_bid.assert_called_with(player, cur_bid)
        self.game.set_current_player.assert_called_with(player2)

    def testOnBidThrowsIllegalBidException(self) :
        test_bid1 = (4, 3)
        test_bid2 = (3, 6)
        prev_bid = (4, 4)
        test_bid3 = (4, 4)
        player = Mock(spec=game.Player)
        self.game.get_previous_bid.return_value = prev_bid
        def call() :
            self.subject.on_bid(player, test_bid1)
        self.assertRaises(game.IllegalBidError, call)
        def call() :
            self.subject.on_bid(player, test_bid2)
        self.assertRaises(game.IllegalBidError, call)        
        def call() :
            self.subject.on_bid(player, test_bid3)
        self.assertRaises(game.IllegalBidError, call)
        self.assertTrue(not self.game.set_state.called)
        self.assertTrue(not self.game.set_bid.called)
        self.assertTrue(not self.game.set_current_player.called)
    
    def testOnChallenge(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = True
        self.game.get_previous_bid.return_value = cur_bid
        self.game.finished.return_value = False
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is None)
        self.assertTrue(not self.game.set_state.called)
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
        self.assertTrue(ret is None)
        self.assertTrue(not self.game.set_state.called)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player1, player2, cur_bid)

    def testOnChallengeToFinalState(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = True
        self.game.get_previous_bid.return_value = cur_bid
        self.game.get_winning_player.return_value = player1
        self.game.finished.return_value = True
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player2, player1, cur_bid)
        self.game.get_winning_player.assert_called_with()
        self.game.end_game.assert_called_with(player1)

    def testOnChallengeNegativeToFinalState(self) :
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        cur_bid = (3, 4)
        self.game.true_bid.return_value = False
        self.game.get_previous_bid.return_value = cur_bid
        self.game.finished.return_value = True
        self.game.get_winning_player.return_value = player2
        ret = self.subject.on_challenge(player1, player2)
        self.assertTrue(ret is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.game.true_bid.assert_called_with(cur_bid)
        self.game.on_win.assert_called_with(player1, player2, cur_bid)
        self.game.get_winning_player.assert_called_with()
        self.game.end_game.assert_called_with(player2)

        
class GameStartStateTest(GameStateTest) :
    
    def get_subject(self, g) :
        self.dice_roll = Mock(spec=game.DiceRoller)
        self.next_state = Mock(spec=game.GameState)
        return game.GameStartState(g, self.next_state, self.dice_roll)

    def testOnGameStart(self) :
        player = Mock(spec=game.Player)
        face = (1,6)
        self.game.has_player.return_value = True
        self.game.get_players.return_value = []
        self.game.get_face_values.return_value = face
        res = self.subject.on_game_start(player)
        self.assertTrue(res is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.assertTrue(self.game.has_player.called)
        self.game.activate_players.assert_called_with()
        self.game.set_current_player.assert_called_with(player)
    
    def testOnGameStartShufflesDice(self) :
        player = Mock(spec=game.Player)
        players = [player] + [Mock(spec=game.Player) for i in xrange(1, 4)]
        self.game.get_players.return_value = players
        ret_dice = [1,2,3,4,5,6]
        face = (1,6)
        max_dice = 6
        self.game.has_player.return_value = True
        self.game.number_of_starting_dice.return_value = max_dice
        self.game.get_face_values.return_value = face
        self.dice_roll.roll_set_of_dice.return_value = ret_dice
        res = self.subject.on_game_start(player)
        self.assertTrue(res is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.assertTrue(self.game.has_player.called) 
        self.assertTrue(self.game.number_of_starting_dice.called)
        self.assertTrue(self.dice_roll.roll_set_of_dice.called)
        self.assertEquals(len(players), 
            self.dice_roll.roll_set_of_dice.call_count)
        self.dice_roll.roll_set_of_dice.assert_called_with(max_dice, face)
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
        self.assertTrue(ret is None)
        self.first.on_game_start.assert_called_with(player)

class ProxyDispatcherTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=[])
        self.prox = Mock(spec=[])
        self.subject = game.ProxyDispatcher(self.game, self.prox)

    def testDispatchingToProxy(self) :
        fake = Mock()
        self.prox.mock_method = fake
        ret = self.subject.mock_method
        self.assertTrue(ret == fake)

    def testDispatchingToGame(self) :
        fake = Mock()
        self.game.mock_method = fake
        ret = self.subject.mock_method
        self.assertTrue(ret == fake)

    def testDispatchingToProxyOverGame(self) :
        fake1 = Mock()
        fake2 = Mock()
        self.game.mock_method = fake1
        self.prox.mock_method = fake2
        ret = self.subject.mock_method
        self.assertTrue(ret == fake2)

class ProxyGameTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.subject = game.ProxyGame(self.game)

    def testAddingGameView(self) :
        view = Mock(spec=game.GameView)
        self.subject.add_game_view(view)
        self.assertTrue(view in self.subject.get_game_views())

    def testStartingGame(self) :
        view = Mock(spec=game.GameView)
        player = Mock(spec=game.Player)
        players = [player]
        playername = "player1"
        player.get_name.return_value = playername
        self.game.get_all_players.return_value = players
        self.subject.add_game_view(view)
        self.subject.start_game(player)
        self.assertTrue(player.get_name.called)
        self.game.start_game.assert_called_with(player)
        view.on_game_start.assert_Called_with([playername])
        player.on_game_start.assert_called_with()

    def testEndingGame(self) :
        view = Mock(spec=game.GameView)
        winner = Mock(spec=game.Player)
        player = Mock(spec=game.Player)
        players = [player]
        playername = "Player1"
        winner.get_name.return_value = playername
        self.game.get_all_players.return_value = players
        self.subject.add_game_view(view)
        self.subject.end_game(winner)
        self.assertTrue(winner.get_name.called)
        self.game.end_game.assert_called_with(winner)
        view.on_game_end.assert_called_with(playername)
        player.on_game_end.assert_called_with()

    def testSettingDiceAmount(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        players = [player1, player2]
        playername = "Player1"
        amount = 4
        dice = [1] * amount
        player1.get_name.return_value = playername
        self.game.get_all_players.return_value = players
        self.game.get_dice.return_value = dice
        self.subject.add_game_view(view)
        self.subject.set_dice(player1, dice)
        player1.get_name.assert_called_with()
        self.assertTrue(not player2.get_name.called)
        self.game.set_dice.assert_called_with(player1, dice)
        self.game.get_dice.assert_called_with(player1)
        view.on_new_dice_amount.assert_called_with(playername, amount)
        player1.on_new_dice_amount.assert_called_with(amount)
        player1.on_set_dice.assert_called_with(dice)
        self.assertTrue(not player2.on_new_dice_amount.called)
        self.assertTrue(not player2.on_set_dice.called)

    def testActivatingPlayers(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        players = [player1]
        playername = "Player1"
        player1.get_name.return_value = playername
        self.game.get_all_players.return_value = players
        self.subject.add_game_view(view)
        self.subject.activate_players()
        player1.get_name.assert_called_with()
        self.game.activate_players.assert_called_with()
        view.on_multi_activation.assert_called_with([playername])
        player1.on_made_active.assert_called_with()
    
    def testAddingPlayer(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        players = [player1]
        playername = "Player1"
        player1.get_name.return_value = playername
        self.subject.add_game_view(view)
        self.subject.add_player(player1)
        player1.get_name.assert_called_with()
        self.game.add_player.assert_called_with(player1)
        view.on_player_addition.assert_called_with(playername)

    def testRemovingPlayer(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        players = [player1]
        playername = "Player1"
        player1.get_name.return_value = playername
        self.subject.add_game_view(view)
        self.subject.remove_player(player1)
        player1.get_name.assert_called_with()
        self.game.remove_player.assert_called_with(player1)
        view.on_player_remove.assert_called_with(playername)    
 
    def testRemovingDice(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        players = [player1, player2]
        playername = "Player1"
        amount = 4
        dice = [1] * amount
        player1.get_name.return_value = playername
        self.game.get_all_players.return_value = players
        self.game.get_dice.return_value = dice
        self.subject.add_game_view(view)
        self.subject.remove_dice(player1)
        self.assertTrue(player1.get_name.called)
        self.assertTrue(not player2.get_name.called)
        self.game.remove_dice.assert_called_with(player1)
        self.game.get_dice.assert_called_with(player1)
        view.on_new_dice_amount.assert_called_with(playername, amount)
        player1.on_new_dice_amount.assert_called_with(amount)
        self.assertTrue(not player2.on_new_dice_amount.called)
    
    def testDeactivatePlayer(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        players = [player1]
        playername = "Player1"
        player1.get_name.return_value = playername
        self.subject.add_game_view(view)
        self.subject.deactivate_player(player1)
        player1.get_name.assert_called_with()
        player1.on_made_inactive.called_with()
        self.game.deactivate_player.assert_called_with(player1)
        view.on_deactivate.assert_called_with(playername)    

    def testSettingBid(self) :
        view = Mock(spec=game.GameView)
        player1 = Mock(spec=game.Player)
        playername = "Player1"
        player1.get_name.return_value = playername
        cur_bid = (1,2)
        self.subject.add_game_view(view)
        self.subject.set_bid(player1, cur_bid)
        player1.get_name.assert_called_with()
        self.game.set_bid.assert_called_with(player1, cur_bid)
        view.on_bid.assert_called_with(playername, cur_bid)

    def testSettingCurrentPlayer(self) :
        view = Mock(spec=game.GameView)
        self.subject.add_game_view(view)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        player1name = "Player1"
        player2name = "Player2"
        player1.get_name.return_value = player1name
        player2.get_name.return_value = player2name
        self.game.get_current_player.return_value = player1
        self.subject.set_current_player(player2)
        self.game.get_current_player.assert_called_with()
        self.game.set_current_player.assert_called_with(player2)
        player1.get_name.assert_called_with()
        player2.get_name.assert_called_with()
        player1.on_end_turn.assert_called_with()
        player2.on_start_turn.assert_called_with()
        view.on_player_end_turn.assert_called_with(player1name)
        view.on_player_start_turn.assert_called_with(player2name)
    
    def testSettingCurrentWhenCurrentPlayerIsNone(self) :
        view = Mock(spec=game.GameView)
        self.subject.add_game_view(view)
        player = Mock(spec=game.Player)
        playername = "Player1"
        player.get_name.return_value = playername
        self.game.get_current_player.return_value = None
        self.subject.set_current_player(player)
        self.game.set_current_player.assert_called_with(player)
        self.game.get_current_player.assert_called_with()
        player.get_name.assert_called_with()
        player.on_start_turn.assert_called_with()
        view.on_player_start_turn.assert_called_with(playername)
    
    def testOnWinning(self) :
        view = Mock(spec=game.GameView)
        self.subject.add_game_view(view)
        bid = (6, 5)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        player1name = "Player1"
        player2name = "Player2"
        player1.get_name.return_value = player1name
        player2.get_name.return_value = player2name
        dice_map = {player1:[1,5,4,2], player2:[3,5,4,5]}
        self.game.get_dice_map.return_value = dice_map
        ret_map = {player1name:[1,5,4,2], player2name:[3,5,4,5]}
        
        self.subject.on_win(player1, player2, bid)

        self.game.on_win.assert_called_with(player1, player2, bid)
        player1.get_name.assert_called_with()
        player2.get_name.assert_called_with()
        self.game.get_dice_map.assert_called_with()
        view.on_challenge.assert_called_with(player1name, player2name, ret_map, 
bid)
    
    def testOnWinningCallsGetDiceMapBeforeOnWin(self) :
        view = Mock(spec=game.GameView)
        self.subject.add_game_view(view)
        bid = (6, 5)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        player1name = "Player1"
        player2name = "Player2"
        player1.get_name.return_value = player1name
        player2.get_name.return_value = player2name
        dice_map = {player1:[1,5,4,2], player2:[3,5,4,5]}
        self.game.get_dice_map.return_value = dice_map
        ret_map = {player1name:[1,5,4,2], player2name:[3,5,4,5]}
        
        self.subject.on_win(player1, player2, bid)

        self.game.on_win.assert_called_with(player1, player2, bid)
        player1.get_name.assert_called_with()
        player2.get_name.assert_called_with()
        self.game.get_dice_map.assert_called_with()
        onWinIndex = map(lambda args : args[0] , 
            filter(lambda meth_call : meth_call[1][0] == "on_win", 
               enumerate(self.game.method_calls)))[0]
        getDiceMapIndex = map(lambda args : args[0] , 
            filter(lambda meth_call : meth_call[1][0] == "get_dice_map", 
               enumerate(self.game.method_calls)))[0]
        self.assertTrue(getDiceMapIndex < onWinIndex)
        view.on_challenge.assert_called_with(player1name, player2name, 
            ret_map, bid)

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
    suite.addTests(loader.loadTestsFromTestCase(DiceRollerTest))
    suite.addTests(loader.loadTestsFromTestCase(WinCheckerTest))
    suite.addTests(loader.loadTestsFromTestCase(WinHandlerTest))
    suite.addTests(loader.loadTestsFromTestCase(ProxyDispatcherTest))
    suite.addTests(loader.loadTestsFromTestCase(ProxyGameTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
