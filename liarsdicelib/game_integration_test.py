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

This module tests the game module functionally, so all dependencies are
created from actual production objects and tests run on them.

This module uses the mock library to mock out player and game views to
see the output given from the game"""

import unittest
from functools import partial

from mock import Mock

import game
import game_state
import game_views
import game_data
import game_proxy
from game_common import IllegalBidError, IllegalStateChangeError

class GameIntegrationTest(unittest.TestCase) :

    def setUp(self) :
        
        #Initialise players
        self.player1 = "Player1"
        self.player2 = "Player2"

        #Initialise game data store and add players
        self.starting_dice = 3
        self.lowest_face = 1
        self.highest_face = 6
        self.data_store = game_data.GameData(
            self.starting_dice, 
            self.lowest_face, 
            self.highest_face)
        self.data_store.add_player(self.player1)
        self.data_store.add_player(self.player2)
 
        #Create the proxy game objects with game views
        self.view = Mock(spec=game_views.GameView)
        self.proxy = game_proxy.ProxyGame(None, self.data_store)
        self.proxy_dispatcher = game_proxy.ProxyDispatcher(None, self.proxy)
        self.data_store.add_game_view(self.view)

        #Create the utility objects
        self.dice_roller = game_state.roll_set_of_dice
        self.win_checker = game.get_winner
        self.bid_checker = game.check_bids
        self.win_handler = game.on_win
        self.win_handler = partial(self.win_handler, game=self.proxy_dispatcher)
        
        #Create the game states from last to first
        self.bid_state = game_state.BidState(self.proxy_dispatcher, 
            None)
        self.first_bid_state = game_state.FirstBidState(self.proxy_dispatcher, 
            self.bid_state)
        self.game_start_state = game_state.GameStartState(self.proxy_dispatcher, 
            self.first_bid_state, self.dice_roller)
        self.bid_state.next = self.game_start_state

        #Create the game object
        self.game = game.Game(self.data_store, self.win_handler, self.bid_checker, 
            self.win_checker)
        self.game.set_state(self.game_start_state)
        self.proxy.game = self.game
        self.proxy_dispatcher.game = self.game

    def testStartingAGame(self) :
        self.proxy_dispatcher.start_game()

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player1, 
               self.game.get_current_player())
        self.assertEquals(2, self.view.on_activation.call_count)
        self.assertEquals(self.player1,
               self.view.on_activation.call_args_list[0][0][0])        
        self.assertEquals(self.player2,
               self.view.on_activation.call_args_list[1][0][0])
        self.view.on_game_start.assert_called_with(
            [self.player1, self.player2])
        self.assertEquals(2, self.view.on_new_dice_amount.call_count) 
        self.assertEquals((self.player1, self.starting_dice),
               self.view.on_new_dice_amount.call_args_list[0][0]) 
        self.assertEquals((self.player2, self.starting_dice),
               self.view.on_new_dice_amount.call_args_list[1][0]) 
        self.view.on_player_start_turn.assert_called_with(self.player1)
        dice_map = self.data_store.get_dice_map()
        self.assertEquals(2, len(dice_map))
        self.assertTrue(self.player1 in dice_map)
        self.assertTrue(self.player2 in dice_map)
        for player in dice_map :
            dice = dice_map[player]
            self.assertEquals(self.starting_dice, len(dice))
            self.assertTrue(all(
                [self.lowest_face <= die <= self.highest_face for die in dice]
                ))
            self.assertTrue(((player,dice),{}) in 
                 self.view.on_set_dice.call_args_list)
        player_names = [self.player1, self.player2]
        self.view.on_game_start.assert_called_with(player_names)
            
        self.assertEquals(2, self.view.on_new_dice_amount.call_count)
        players = set(player_names)
        for args in self.view.on_new_dice_amount.call_args_list :
            self.assertEquals(self.starting_dice, args[0][1])
            player = args[0][0]
            self.assertTrue(player in players)
            players.remove(player)
        self.assertEquals(0, len(players))
        self.assertEquals(self.first_bid_state, self.game.get_state())

    def testBiddingWithoutStartingGameThrowsException(self) :
        cur_bid = (1, 2)
        def call() :
            self.proxy_dispatcher.make_bid(cur_bid)
        self.assertRaises(IllegalStateChangeError, call)
        self.assertTrue(self.game.get_current_player() is None)
        self.assertTrue(self.game.get_state() is not None)
        self.assertEquals(self.game_start_state, self.game.get_state())

    def testFirstBid(self) :
        self.proxy_dispatcher.start_game()
        
        cur_bid = (2, 5)

        self.proxy_dispatcher.make_bid(cur_bid)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player2, self.game.get_current_player())
        self.view.on_player_end_turn.assert_called_with(self.player1)
        self.view.on_player_start_turn.assert_called_with(self.player2)
        self.view.on_bid.assert_called_with(self.player1, cur_bid)
        self.view.on_player_end_turn.assert_called_with(self.player1)
        self.view.on_player_start_turn.assert_called_with(self.player2)
        self.assertEquals(self.bid_state, self.game.get_state())

    def testTwoBidsWithBidAfterwards(self) :
        self.proxy_dispatcher.start_game()
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        
        cur_bid = (3, 6)

        self.proxy_dispatcher.make_bid(cur_bid)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player1, self.game.get_current_player())
        self.view.on_player_start_turn.assert_called_with(self.player1)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_bid.assert_called_with(self.player2, cur_bid)
        self.view.on_player_start_turn.assert_called_with(self.player1)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.assertEquals(self.bid_state, self.game.get_state())

    def testTwoBidsWithBadBid(self) :
        self.proxy_dispatcher.start_game()
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        self.view.reset_mock()
        cur_bid = (2, 3)

        def call() :
            self.proxy_dispatcher.make_bid(cur_bid)
        self.assertRaises(IllegalBidError, call)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player2, self.game.get_current_player())
        self.assertEquals(self.bid_state, self.game.get_state())
        self.assertTrue(not self.view.on_bid.called)
        self.assertTrue(not self.view.on_player_start_turn.called)
        self.assertTrue(not self.view.on_player_end_turn.called)

    def testChallengeWithFirstPlayerWin(self) :
        self.proxy_dispatcher.start_game()
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2, 5]
        player2dice = [6, 5]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player2, self.game.get_current_player())
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_player_start_turn.assert_called_with(self.player2)
        self.assertEquals(1, len(self.data_store.get_dice(self.player2)))
        self.view.on_new_dice_amount.assert_called_with(self.player2, 1)
        self.view.on_player_start_turn.assert_called_with(self.player2)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_challenge.assert_called_with(
              self.player1, 
              self.player2,
              {self.player1:player1dice, self.player2:player2dice}, 
              first_bid)

    def testChallengeWithFirstPlayerLoss(self) :
        self.proxy_dispatcher.start_game()
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2, 5]
        player2dice = [6, 4]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player1, self.game.get_current_player())
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_player_start_turn.assert_called_with(self.player1)
        self.assertEquals(1, len(self.data_store.get_dice(self.player1)))
        self.view.on_new_dice_amount.assert_called_with(self.player1, 1)
        self.view.on_player_start_turn.assert_called_with(self.player1)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_challenge.assert_called_with(
            self.player2, 
            self.player1,
            {self.player1:player1dice, self.player2:player2dice}, 
            first_bid)     

    def testChallengeResultingInFirstPlayerGettingDeactivated(self) :
        # Add a new player, don't want deactivation to end in a win
        player3 = "player 3"
        self.data_store.add_player(player3)

        self.proxy_dispatcher.start_game()

        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [5]
        player2dice = [6, 4]
        player3dice = [2, 2]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        self.data_store.set_dice(player3, player3dice)
        
        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player2, self.game.get_current_player())
        
        self.assertEquals(0, len(self.data_store.get_dice(self.player1)))
        self.assertTrue(not self.data_store.is_active(self.player1))
        self.view.on_new_dice_amount.assert_called_with(self.player1, 0)
        self.view.on_player_start_turn.assert_called_with(self.player2)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_challenge.assert_called_with(
            self.player2, 
            self.player1,
            {self.player1:player1dice, 
                self.player2:player2dice, 
             player3:player3dice},
            first_bid)     
        self.view.on_deactivate.assert_called_with(self.player1)

    def testChallengeResultingInLoserGettingDeactivated(self) :        
        player3 = "player 3"
        self.data_store.add_player(player3)

        self.proxy_dispatcher.start_game()

        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2, 5]
        player2dice = [5]
        player3dice = [2, 2]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        self.data_store.set_dice(player3, player3dice)
        

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player1, self.game.get_current_player())
        
        self.assertEquals(0, len(self.data_store.get_dice(self.player2)))
        self.assertTrue(not self.data_store.is_active(self.player2))
        self.view.on_player_start_turn.assert_called_with(self.player1)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_challenge.assert_called_with(
            self.player1, 
            self.player2,
            {self.player1:player1dice, 
                self.player2:player2dice, 
            player3:player3dice}, 
            first_bid)     
        self.view.on_deactivate.assert_called_with(self.player2)

    def testChallengeResultingInFirstPlayerWinning(self) :
        self.proxy_dispatcher.start_game()

        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2, 5]
        player2dice = [5]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player1, self.game.get_current_player())
        
        self.assertEquals(0, len(self.data_store.get_dice(self.player2)))
        self.assertTrue(not self.data_store.is_active(self.player2))
        self.view.on_player_start_turn.assert_called_with(self.player1)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_deactivate.assert_called_with(self.player2)
        self.view.on_game_end(self.player1)
        self.assertEquals(self.game_start_state, self.game.get_state())
        self.view.on_challenge.assert_called_with(
            self.player1, 
            self.player2,
            {self.player1:player1dice, self.player2:player2dice},
            first_bid)     

    def testChallengeResultingInFirstPlayerLoosing(self) :
        self.proxy_dispatcher.start_game()

        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [5]
        player2dice = [2, 3]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player2, self.game.get_current_player())
        self.assertEquals(0, len(self.data_store.get_dice(self.player1)))
        self.assertTrue(not self.data_store.is_active(self.player1))
        self.view.on_player_start_turn.assert_called_with(self.player2)
        self.view.on_player_end_turn.assert_called_with(self.player2)
        self.view.on_deactivate.assert_called_with(self.player1)
        self.view.on_game_end(self.player2)
        self.assertEquals(self.game_start_state, self.game.get_state())
        self.view.on_challenge.assert_called_with(
            self.player2, 
            self.player1,
            {self.player1:player1dice, self.player2:player2dice},
            first_bid)

    def testRestartingGameFromFirstBid(self) :
        pass

    def testRestartingGameFromSecondBid(self) :
        pass

    def testRestartingGameFromWinState(self) :
        pass

    def testAddingNewPlayer(self) :
        pass

    def testRemovingAPlayer(self) :
        pass

    def testRemovingAPlayerResultingInAWin(self) :
        pass

    def testRemovingCurrentPlayer(self) :
        pass

def suite() :
    """Return a test suite of all tests in this module"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(GameIntegrationTest))
    return test_suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
