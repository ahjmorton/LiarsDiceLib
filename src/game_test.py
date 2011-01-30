"""
***** BEGIN LICENSE BLOCK *****
Version: MPL 1.1

The contents of this file are subject to the Mozilla Public License Version 
1.1 (the "License"); you may not use this file except in compliance with 
the License. You may obtain a copy of the License at 
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
for the specific language governing rights and limitations under the
License.

The Original Code is LiarsDiceLib.

The Initial Developer of the Original Code is
Andrew Morton <ahjmorton@gmail.com> .
Portions created by the Initial Developer are Copyright (C) 2011
the Initial Developer. All Rights Reserved.

Contributor(s):
     
***** END LICENSE BLOCK *****
Game test tests the objects in the game module using unit tests.
This module relies on the mock library for mocking of dependencies."""

import unittest
import random

from mock import Mock

import game
import game_data

class GameObjectTest(unittest.TestCase) :
    
    def setUp(self) :
        self.data = Mock(spec=game_data.GameData)
        self.state = Mock()
        self.dice_check = Mock(spec=game.check_bids)
        self.win_check = Mock(spec=game.get_winner)
        self.win_hand = Mock(spec=game.on_win)
        self.subject = game.Game(self.data, self.win_hand, self.dice_check, 
        self.win_check)

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
        self.win_check.return_value = player1
        self.data.get_dice_map.return_value = dice_map
        ret = self.subject.finished()
        self.assertTrue(ret is not None)
        self.assertTrue(ret)
        self.data.get_dice_map.assert_called_with()
        self.win_check.assert_called_with(dice_map)
    
    def testCheckingForActive(self) :
        player1 = Mock(spec=game.Player)
        self.data.is_active.return_value = True

        self.assertTrue(self.subject.is_player_active(player1))
        
        self.data.is_active.assert_Called_with(player1)
        self.data.is_active.return_value = False

        self.assertTrue(not self.subject.is_player_active(player1))
           
    def testCheckingForFinishedNegative(self) :
        self.win_check.return_value = None
        dice_map = dict()
        self.data.get_dice_map.return_value = dice_map
        ret = self.subject.finished()
        self.assertTrue(ret is not None)
        self.assertTrue(not ret)
        self.data.get_dice_map.assert_called_with()
        self.win_check.assert_called_with(dice_map)

    def testStartupStateOfGameObject(self) :
        self.data.get_current_player.return_value = None
        self.assertTrue(self.subject.get_current_player() is None)
        self.data.get_current_state.return_value = self.state
        self.assertTrue(self.subject.get_state() == self.state)
        self.data.get_current_state.assert_called_with()
        self.assertTrue(not self.state.on_game_start.called)
        self.assertTrue(not self.data.add_player.called)

    def testStartingAGame(self) :
        self.data.get_current_state.return_value = self.state
        self.subject.start_game()
        self.data.get_current_player.return_value = None
        self.assertTrue(self.subject.get_current_player() is None)
        self.state.on_game_start.assert_called_with()
        self.assertEquals(self.state, self.subject.get_state())

    def testSettingAState(self) :
        state1 = Mock()
        self.subject.set_state(state1)
        self.data.set_current_state.assert_called_with(state1)

    def testMakingABid(self) :
        player = Mock(spec=game.Player)
        self.data.get_current_player.return_value = player
        self.data.get_current_state.return_value = self.state
        bid = (1, 2)
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
        bid = (1, 2)
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
        self.dice_check.return_value = exp
        bid = (1, 2)
        ret = self.subject.true_bid(bid)
        self.assertTrue(ret is not None)
        self.assertTrue(exp == ret)
        self.assertTrue(self.data.get_dice_map.called)
        self.dice_check.assert_called_with(bid, dice_dict)

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
        cur_bid = (1, 2)
        self.subject.on_win(player1, player2, cur_bid)
        self.win_hand.assert_called_with(player1, player2, cur_bid)

    def testGettingWinningPlayer(self) :
        player1 = Mock(spec=game.Player)
        ret_map = {player1:[1]}
        self.data.get_dice_map.return_value = ret_map
        self.win_check.return_value = player1
        ret = self.subject.get_winning_player()
        self.assertTrue(ret is not None)
        self.assertTrue(ret == player1)
        self.win_check.assert_called_with(ret_map)
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
    
    def testCheckingBidSimple(self) :
        player = Mock(spec=game.Player)
        bid = (2, 4)
        dice_map = {player:[2, 4, 4]}
        ret = game.check_bids(bid, dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(ret)
    
    def testCheckingBidNegative(self) :
        player = Mock(spec=game.Player)
        bid = (2, 4)
        dice_map = {player:[2, 4]}
        ret = game.check_bids(bid, dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(not ret) 

class WinCheckerTest(unittest.TestCase) :
    
    def testCheckingBidAllNone(self) :
        dice_map = {"a":[1, 2, 3], "b":[1], "c":[1, 4, 2]}
        self.assertTrue(game.get_winner(dice_map) is None)


    def testCheckingBidOneWin(self) :
        winner = "a"
        dice_map = {winner:[1, 2, 3], "b":[], "c":[]}
        ret = game.get_winner(dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(winner == ret)


class WinHandlerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game_obj = Mock(game.Game)
        self.subject = game.on_win
   
    def testHandlingWinWithoutMakingPlayerInactive(self) :
        player1 = Mock(game.Player)
        player2 = Mock(game.Player)
        bid = (1, 2)
        self.game_obj.get_dice.return_value = [1, 2]
        self.subject(player1, player2, bid, self.game_obj)
        self.game_obj.remove_dice.assert_called_with(player2)
        self.game_obj.get_dice.assert_called_with(player2)
        self.game_obj.set_current_player.assert_called_with(player2)

    def testHandlingWinWithMakingPlayerInactive(self) :
        player1 = Mock(game.Player)
        player2 = Mock(game.Player)
        bid = (1, 2)
        self.game_obj.get_dice.return_value = []
        self.subject(player1, player2, bid, self.game_obj)
        self.game_obj.remove_dice.assert_called_with(player2)
        self.game_obj.get_dice.assert_called_with(player2)
        self.game_obj.deactivate_player.assert_called_with(player2)
        self.game_obj.set_current_player.assert_called_with(player1)


class DiceRollerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.random = Mock(spec=random.Random)
        self.subject = game.roll_set_of_dice

    def testRollingSetOfDice(self) :
        ret = 3
        amount = 6
        face = (1, 6)
        self.random.randint.return_value = ret
        val = self.subject(amount, face, self.random)
        self.assertTrue(val is not None)
        self.assertTrue(len(val) == amount)
        self.assertTrue(reduce(lambda x, y: x and (y == ret), val, True))
        self.assertTrue(self.random.randint.called)
        self.assertTrue(self.random.randint.call_count == amount)


class GameStartStateTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.dice_roll = Mock(spec=game.roll_set_of_dice)
        self.next_state = Mock()
        self.subject = game.GameStartState(self.game, self.next_state, 
               self.dice_roll)

    def testOnGameStart(self) :
        player = Mock(spec=game.Player)
        face = (1, 6)
        self.game.get_players.return_value = [player]
        self.game.get_face_values.return_value = face
        res = self.subject.on_game_start()
        self.assertTrue(res is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.game.activate_players.assert_called_with()
        self.game.set_current_player.assert_called_with(player)
    
    def testOnGameStartShufflesDice(self) :
        players = [Mock(spec=game.Player) for i in xrange(1, 4)]
        self.game.get_players.return_value = players
        ret_dice = [1, 2, 3, 4, 5, 6]
        face = (1, 6)
        max_dice = 6
        self.game.number_of_starting_dice.return_value = max_dice
        self.game.get_face_values.return_value = face
        self.dice_roll.return_value = ret_dice
        res = self.subject.on_game_start()
        self.assertTrue(res is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.assertTrue(self.game.number_of_starting_dice.called)
        self.assertTrue(self.dice_roll.called)
        self.assertEquals(len(players), 
            self.dice_roll.call_count)
        self.dice_roll.assert_called_with(max_dice, face)
        self.assertTrue(self.game.set_dice.called)
        self.assertEquals(len(players), self.game.set_dice.call_count)
        full_call_args = self.game.set_dice.call_args_list
        for x in players :
            self.assertTrue(((x, ret_dice), {}) in full_call_args)
     
    def testOnChallenge(self) :
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        def call() :
            self.subject.on_challenge(player, player2)
        self.assertRaises(game.IllegalStateChangeError, call)
    
    def testOnBid(self) :
        bid = (1, 2)
        player = Mock(spec=game.Player)
        def call() :
            self.subject.on_bid(player, bid)
        self.assertRaises(game.IllegalStateChangeError, call)


class FirstBidGameStateTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.next_state = Mock()
        self.subject = game.FirstBidState(self.game, self.next_state)

    def testOnBid(self) :
        bid = (1, 2)
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        self.game.get_next_player.return_value = player2
        ret = self.subject.on_bid(player, bid)
        self.assertTrue(ret is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.game.set_bid.assert_called_with(player, bid)
        self.game.set_current_player.assert_called_with(player2)

    def testOnGameStart(self) :
        def call() :
            self.subject.on_game_start()
        self.assertRaises(game.IllegalStateChangeError, call)

    def testOnChallenge(self) :
        player = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        def call() :
            self.subject.on_challenge(player, player2)
        self.assertRaises(game.IllegalStateChangeError, call)


class BidGameStateTest(unittest.TestCase) :

    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.next_state = Mock()
        self.subject = game.BidState(self.game, self.next_state)
 
    def testOnGameStart(self) :
        def call() :
            self.subject.on_game_start()
        self.assertRaises(game.IllegalStateChangeError, call)

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
        def call1() :
            self.subject.on_bid(player, test_bid1)
        self.assertRaises(game.IllegalBidError, call1)
        def call2() :
            self.subject.on_bid(player, test_bid2)
        self.assertRaises(game.IllegalBidError, call2)   
        def call3() :
            self.subject.on_bid(player, test_bid3)
        self.assertRaises(game.IllegalBidError, call3)
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


def suite() :
    """Return a test suite of all tests defined in this module"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(GameObjectTest))
    test_suite.addTests(loader.loadTestsFromTestCase(GameStartStateTest))
    test_suite.addTests(loader.loadTestsFromTestCase(FirstBidGameStateTest))
    test_suite.addTests(loader.loadTestsFromTestCase(BidCheckerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(BidGameStateTest))
    test_suite.addTests(loader.loadTestsFromTestCase(DiceRollerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(WinCheckerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(WinHandlerTest))
    return test_suite


if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
