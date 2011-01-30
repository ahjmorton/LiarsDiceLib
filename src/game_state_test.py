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
import game_state
from game_common import IllegalBidError, IllegalStateChangeError

class DiceRollerTest(unittest.TestCase) :
    
    def setUp(self) :
        self.random = Mock(spec=random.Random)
        self.subject = game_state.roll_set_of_dice

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
        self.dice_roll = Mock(spec=game_state.roll_set_of_dice)
        self.next_state = Mock()
        self.subject = game_state.GameStartState(self.game, self.next_state, 
               self.dice_roll)

    def testOnGameStart(self) :
        player = Mock(spec=game_views.Player)
        face = (1, 6)
        self.game.get_players.return_value = [player]
        self.game.get_face_values.return_value = face
        res = self.subject.on_game_start()
        self.assertTrue(res is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.game.activate_players.assert_called_with()
        self.game.set_current_player.assert_called_with(player)
    
    def testOnGameStartShufflesDice(self) :
        players = [Mock(spec=game_views.Player) for i in xrange(1, 4)]
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
        player = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
        def call() :
            self.subject.on_challenge(player, player2)
        self.assertRaises(IllegalStateChangeError, call)
    
    def testOnBid(self) :
        bid = (1, 2)
        player = Mock(spec=game_views.Player)
        def call() :
            self.subject.on_bid(player, bid)
        self.assertRaises(IllegalStateChangeError, call)


class FirstBidGameStateTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.next_state = Mock()
        self.subject = game_state.FirstBidState(self.game, self.next_state)

    def testOnBid(self) :
        bid = (1, 2)
        player = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
        self.game.get_next_player.return_value = player2
        ret = self.subject.on_bid(player, bid)
        self.assertTrue(ret is None)
        self.game.set_state.assert_called_with(self.next_state)
        self.game.set_bid.assert_called_with(player, bid)
        self.game.set_current_player.assert_called_with(player2)

    def testOnGameStart(self) :
        def call() :
            self.subject.on_game_start()
        self.assertRaises(IllegalStateChangeError, call)

    def testOnChallenge(self) :
        player = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
        def call() :
            self.subject.on_challenge(player, player2)
        self.assertRaises(IllegalStateChangeError, call)


class BidGameStateTest(unittest.TestCase) :

    def setUp(self) :
        self.game = Mock(spec=game.Game)
        self.next_state = Mock()
        self.subject = game_state.BidState(self.game, self.next_state)
 
    def testOnGameStart(self) :
        def call() :
            self.subject.on_game_start()
        self.assertRaises(IllegalStateChangeError, call)

    def testOnBid(self) :
        cur_bid = (3, 4)
        prev_bid = (1, 2)
        player = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
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
        player = Mock(spec=game_views.Player)
        self.game.get_previous_bid.return_value = prev_bid
        def call1() :
            self.subject.on_bid(player, test_bid1)
        self.assertRaises(IllegalBidError, call1)
        def call2() :
            self.subject.on_bid(player, test_bid2)
        self.assertRaises(IllegalBidError, call2)   
        def call3() :
            self.subject.on_bid(player, test_bid3)
        self.assertRaises(IllegalBidError, call3)
        self.assertTrue(not self.game.set_state.called)
        self.assertTrue(not self.game.set_bid.called)
        self.assertTrue(not self.game.set_current_player.called)
    
    def testOnChallenge(self) :
        player1 = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
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
        player1 = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
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
        player1 = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
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
        player1 = Mock(spec=game_views.Player)
        player2 = Mock(spec=game_views.Player)
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
    test_suite.addTests(loader.loadTestsFromTestCase(DiceRollerTest))
    test_suite.addTests(loader.loadTestsFromTestCase(GameStartStateTest))
    test_suite.addTests(loader.loadTestsFromTestCase(FirstBidGameStateTest))
    test_suite.addTests(loader.loadTestsFromTestCase(BidGameStateTest))
    return test_suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
