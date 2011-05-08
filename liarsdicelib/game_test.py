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
import game_views
import game_data
import game_common

class GameObjectTest(unittest.TestCase) :
    
    def setUp(self) :
        self.data = Mock(spec=game_data.GameData)
        self.state = Mock()
        self.dice_check = Mock(spec=game.check_bids)
        self.win_check = Mock(spec=game.get_winner)
        self.win_hand = Mock(spec=game.on_win)
        self.bid_reset = Mock(spec=game.bid_reset)
        self.reshuffle_dice = Mock(spec=game.reshuffle_dice)
        self.subject = game.Game(self.data, self.win_hand, self.dice_check, 
        self.win_check, self.bid_reset, self.reshuffle_dice)

    def testDeactivatePlayer(self) :
        player1 = "player"
        self.subject.deactivate_player(player1)
        self.data.mark_inactive.assert_called_with(player1)

    def testSettingAPlayer(self) :
        player1 = "player"
        self.subject.set_current_player(player1)
        self.data.set_current_player.assert_called_with(player1)

    def testCheckingForFinished(self) :
        player1 = "player"
        dice_map = dict()
        self.win_check.return_value = player1
        self.data.get_dice_map.return_value = dice_map
        ret = self.subject.finished()
        self.assertTrue(ret is not None)
        self.assertTrue(ret)
        self.data.get_dice_map.assert_called_with()
        self.win_check.assert_called_with(dice_map)
    
    def testCheckingForActive(self) :
        player1 = "player"
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
        player = "player"
        self.data.get_current_player.return_value = player
        self.data.get_current_state.return_value = self.state
        bid = (1, 2)
        self.subject.make_bid(bid)

        self.data.get_current_state.assert_called_with()
        self.data.get_current_player.assert_called_with()
        self.state.on_bid.assert_called_with(player, bid)
        self.assertTrue(not self.data.set_bid.called)
        self.assertEquals(self.state, self.subject.get_state())

    def testResettingBid(self) :
        self.subject.reset_bid() 
        self.bid_reset.assert_called_with(self.subject)
            
    def testGettingNumberOfDiceAPlayerHas(self) :
        player1 = "player"
        expected = 4
        self.data.get_number_of_dice.return_value = expected

        ret = self.subject.num_of_dice(player1)

        self.data.get_number_of_dice.assert_called_with(player1)
        self.assertEquals(expected, ret)


    def testMakingAChallengeWithNoneAndNoneGrabsFromGame(self) :
        player1 = "player"
        player2 = "player"
        self.data.get_players.return_value = [player1, player2]
        self.data.get_current_player.return_value = player2
        self.data.get_current_state.return_value = self.state

        self.subject.make_challenge()
        self.data.get_current_state.assert_called_with()
        self.data.get_players.assert_called_with()
        self.state.on_challenge.assert_called_with(player2, player1)
        self.assertEquals(self.state, self.subject.get_state())
 
    def testMakingAChallengeWithChallengedParametersDoesNotCall(self) :
        player1 = "player"
        player2 = "player"
        self.data.get_current_player.return_value = player2
        self.data.get_current_state.return_value = self.state

        self.subject.make_challenge(challenged=player1)
        self.data.get_current_state.assert_called_with()
        self.data.get_current_player.assert_called_with()
        self.assertTrue(not self.data.get_players.called)
        self.state.on_challenge.assert_called_with(player2, player1)
        self.assertEquals(self.state, self.subject.get_state())
    
    def testGettingNextPlayer(self) :
        players = ["player" for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_next_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[1], ret)
        self.data.get_players.assert_called_with()
        self.data.get_current_player.assert_called_with()

    def testGettingNextPlayerOnLastPlayer(self) :
        players = ["player" for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[4]

        ret = self.subject.get_next_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)
    
    def testGettingPreviousPlayer(self) :
        players = ["player" for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[4]

        ret = self.subject.get_previous_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[3], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousPlayerOnFirstPlayer(self) :
        players = ["player" for x in xrange(0, 5)]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_previous_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[4], ret)
        self.assertTrue(self.data.get_players.called)
    
    def testGettingNextPlayerWithOnePlayer(self) :
        players = ["player"]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_next_player()
        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousPlayerWithOnePlayer(self) :
        players = ["player"]
        self.data.get_players.return_value = players
        self.data.get_current_player.return_value = players[0]

        ret = self.subject.get_previous_player()

        self.assertTrue(ret is not None)
        self.assertEquals(players[0], ret)
        self.assertTrue(self.data.get_players.called)

    def testGettingPreviousBid(self) :
        players = ["player" for x in xrange(0, 2)]
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
        player = "player"
        self.data.get_dice.return_value = ret_list
        self.subject.remove_dice(player)
        self.data.get_dice.assert_called_with(player)
        self.assertTrue(self.data.set_dice.called)
        self.assertEquals(length - 1, len(self.data.set_dice.call_args[0][1]))

    def testWinHandling(self) :
        player1 = "player"
        player2 = "player"
        cur_bid = (1, 2)
        self.subject.on_win(player1, player2, cur_bid)
        self.win_hand.assert_called_with(player1, player2, cur_bid)

    def testGettingWinningPlayer(self) :
        player1 = "player"
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
        player1 = "player"
        ret_map = {player1:[1]}
        self.data.get_dice_map.return_value = ret_map
        ret = self.subject.get_dice_map()
        self.assertEquals(ret_map, ret)

    def testGettingFaceValues(self) :
        lowest = 1
        highest = 6
        self.data.get_lowest_dice.return_value = lowest
        self.data.get_highest_dice.return_value = highest

        result = self.subject.get_face_values()

        self.assertEquals(2, len(result))
        self.assertEquals(lowest, result[0])
        self.assertEquals(highest, result[1])

    def testShufflingDice(self) :
        players = ["player" for x in xrange(0, 3)]
        self.data.get_players.return_value = players
        lowest = 1
        highest = 6
        self.data.get_lowest_dice.return_value = lowest
        self.data.get_highest_dice.return_value = highest
        face_vals = (lowest, highest)

        self.subject.shuffle_dice()

        self.reshuffle_dice.assert_called_with(players, face_vals)


class BidCheckerTest(unittest.TestCase) :
    
    def testCheckingBidSimple(self) :
        player = "player"
        bid = (2, 4)
        dice_map = {player:[2, 4, 4]}
        ret = game.check_bids(bid, dice_map)
        self.assertTrue(ret is not None)
        self.assertTrue(ret)
    
    def testCheckingBidNegative(self) :
        player = "player"
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
        self.game_obj = Mock(spec=game.Game)
        self.subject = game.on_win
   
    def testHandlingWinWithoutMakingPlayerInactive(self) :
        player1 = "player"
        player2 = "player"
        bid = (1, 2)
        self.game_obj.get_dice.return_value = [1, 2]
        self.subject(player1, player2, bid, self.game_obj)
        self.game_obj.reset_bid.assert_called_with()
        self.game_obj.remove_dice.assert_called_with(player2)
        self.game_obj.shuffle_dice.assert_called_with()
        self.game_obj.get_dice.assert_called_with(player2)
        self.game_obj.set_current_player.assert_called_with(player2)

    def testHandlingWinWithMakingPlayerInactive(self) :
        player1 = "player"
        player2 = "player"
        bid = (1, 2)
        self.game_obj.get_dice.return_value = []
        self.subject(player1, player2, bid, self.game_obj)
        self.game_obj.remove_dice.assert_called_with(player2)
        self.game_obj.reset_bid.assert_called_with()
        self.game_obj.shuffle_dice.assert_called_with()
        self.game_obj.get_dice.assert_called_with(player2)
        self.game_obj.deactivate_player.assert_called_with(player2)
        self.game_obj.set_current_player.assert_called_with(player1)

class BidResetTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game_obj = Mock(spec=game.Game)
        self.subject = game.bid_reset

    def testResettingABid(self) :
        player1 = "player1"
        self.game_obj.get_previous_player.return_value = player1
        
        self.subject(self.game_obj)

        self.game_obj.get_previous_player.assert_called_with()
        self.game_obj.set_bid(player1, None)

class ReshuffleDiceTest(unittest.TestCase) :

    def setUp(self) :
        self.game_obj = Mock(spec=game.Game)
        self.dice_roller = Mock(spec=game_common.roll_set_of_dice)
        self.subject = game.reshuffle_dice

    def testShufflingDice(self) :
        player1 = "player1"
        players = [player1]
        face_vals = (1, 6)
        num = 3
        return_dice = [3] * num
        total_players = len(players)
        self.game_obj.num_of_dice.return_value = num
        self.dice_roller.return_value = return_dice

        self.subject(players, face_vals, self.game_obj,
             self.dice_roller)

        self.dice_roller.assert_called_with(num, face_vals)
        self.game_obj.set_dice.assert_called_with(player1, 
             return_dice)

def suite() :
    """Return a test suite of all tests defined in this module"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(GameObjectTest))
    test_suite.addTests(loader.loadTestsFromTestCase(BidCheckerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(WinCheckerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(WinHandlerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(BidResetTest))
    test_suite.addTests(loader.loadTestsFromTestCase(ReshuffleDiceTest))
    return test_suite


if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
