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
Tests for proxy game and dispatcher objects
This module relies on the mock library for mocking of dependencies."""

import unittest

from mock import Mock

import game
import game_proxy

class ProxyDispatcherTest(unittest.TestCase) :
    
    def setUp(self) :
        self.game = Mock(spec=[])
        self.prox = Mock(spec=[])
        self.subject = game_proxy.ProxyDispatcher(self.game, self.prox)

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
        self.data = Mock(spec=game.GameData)
        self.subject = game_proxy.ProxyGame(self.game, self.data)

    def testAddingGameView(self) :
        view = Mock(spec=game.GameView)
        self.subject.add_game_view(view)
        self.data.add_game_view.assert_called_with(view)

    def testStartingGame(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player = Mock(spec=game.Player)
        players = [player]
        playername = "player1"
        player.get_name.return_value = playername
        self.data.get_all_players.return_value = players

        self.subject.start_game()

        self.assertTrue(player.get_name.called)
        self.game.start_game.assert_called_with()
        view.on_game_start.assert_Called_with([playername])
        player.on_game_start.assert_called_with()
        self.data.get_game_views.assert_called_with()

    def testEndingGame(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        winner = Mock(spec=game.Player)
        player = Mock(spec=game.Player)
        players = [player]
        playername = "Player1"
        winner.get_name.return_value = playername
        self.data.get_all_players.return_value = players

        self.subject.end_game(winner)

        self.assertTrue(winner.get_name.called)
        self.game.end_game.assert_called_with(winner)
        view.on_game_end.assert_called_with(playername)
        player.on_game_end.assert_called_with()
        self.data.get_game_views.assert_called_with()


    def testSettingDiceAmount(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        players = [player1, player2]
        playername = "Player1"
        amount = 4
        dice = [1] * amount
        player1.get_name.return_value = playername
        self.data.get_all_players.return_value = players
        self.game.get_dice.return_value = dice

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
        self.data.get_game_views.assert_called_with()


    def testActivatingPlayers(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        players = [player1]
        playername = "Player1"
        player1.get_name.return_value = playername
        self.data.get_all_players.return_value = players

        self.subject.activate_players()

        player1.get_name.assert_called_with()
        self.game.activate_players.assert_called_with()
        view.on_multi_activation.assert_called_with([playername])
        player1.on_made_active.assert_called_with()
        self.data.get_game_views.assert_called_with()

    
    def testAddingPlayer(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        playername = "Player1"
        player1.get_name.return_value = playername

        self.subject.add_player(player1)

        player1.get_name.assert_called_with()
        self.game.add_player.assert_called_with(player1)
        view.on_player_addition.assert_called_with(playername)
        self.data.get_game_views.assert_called_with()


    def testRemovingPlayer(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        playername = "Player1"
        player1.get_name.return_value = playername

        self.subject.remove_player(player1)

        self.data.get_game_views.assert_called_with()
        player1.get_name.assert_called_with()
        self.game.remove_player.assert_called_with(player1)
        view.on_player_remove.assert_called_with(playername)    
 
    def testRemovingDice(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        players = [player1, player2]
        playername = "Player1"
        amount = 4
        dice = [1] * amount
        player1.get_name.return_value = playername
        self.data.get_all_players.return_value = players
        self.game.get_dice.return_value = dice

        self.subject.remove_dice(player1)

        self.data.get_game_views.assert_called_with()
        self.assertTrue(player1.get_name.called)
        self.assertTrue(not player2.get_name.called)
        self.game.remove_dice.assert_called_with(player1)
        self.game.get_dice.assert_called_with(player1)
        view.on_new_dice_amount.assert_called_with(playername, amount)
        player1.on_new_dice_amount.assert_called_with(amount)
        self.assertTrue(not player2.on_new_dice_amount.called)
    
    def testDeactivatePlayer(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        playername = "Player1"
        player1.get_name.return_value = playername

        self.subject.deactivate_player(player1)

        self.data.get_game_views.assert_called_with()
        player1.get_name.assert_called_with()
        player1.on_made_inactive.called_with()
        self.game.deactivate_player.assert_called_with(player1)
        view.on_deactivate.assert_called_with(playername)    

    def testSettingBid(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        playername = "Player1"
        player1.get_name.return_value = playername
        cur_bid = (1, 2)

        self.subject.set_bid(player1, cur_bid)

        self.data.get_game_views.assert_called_with()
        player1.get_name.assert_called_with()
        self.game.set_bid.assert_called_with(player1, cur_bid)
        view.on_bid.assert_called_with(playername, cur_bid)

    def testSettingCurrentPlayer(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        player1name = "Player1"
        player2name = "Player2"
        player1.get_name.return_value = player1name
        player2.get_name.return_value = player2name
        self.game.get_current_player.return_value = player1

        self.subject.set_current_player(player2)

        self.data.get_game_views.assert_called_with()
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
        views = [view]
        self.data.get_game_views.return_value = views
        player = Mock(spec=game.Player)
        playername = "Player1"
        player.get_name.return_value = playername
        self.game.get_current_player.return_value = None

        self.subject.set_current_player(player)

        self.data.get_game_views.assert_called_with()
        self.game.set_current_player.assert_called_with(player)
        self.game.get_current_player.assert_called_with()
        player.get_name.assert_called_with()
        player.on_start_turn.assert_called_with()
        view.on_player_start_turn.assert_called_with(playername)
    
    def testOnWinning(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        bid = (6, 5)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        player1name = "Player1"
        player2name = "Player2"
        player1.get_name.return_value = player1name
        player2.get_name.return_value = player2name
        dice_map = {player1:[1, 5, 4, 2], player2:[3, 5, 4, 5]}
        self.game.get_dice_map.return_value = dice_map
        ret_map = {player1name:[1, 5, 4, 2], player2name:[3, 5, 4, 5]}
        
        self.subject.on_win(player1, player2, bid)

        self.data.get_game_views.assert_called_with()
        self.game.on_win.assert_called_with(player1, player2, bid)
        player1.get_name.assert_called_with()
        player2.get_name.assert_called_with()
        self.game.get_dice_map.assert_called_with()
        view.on_challenge.assert_called_with(player1name, player2name, 
            ret_map, bid)
    
    def testOnWinningCallsGetDiceMapBeforeOnWin(self) :
        view = Mock(spec=game.GameView)
        views = [view]
        self.data.get_game_views.return_value = views
        bid = (6, 5)
        player1 = Mock(spec=game.Player)
        player2 = Mock(spec=game.Player)
        player1name = "Player1"
        player2name = "Player2"
        player1.get_name.return_value = player1name
        player2.get_name.return_value = player2name
        dice_map = {player1:[1, 5, 4, 2], player2:[3, 5, 4, 5]}
        self.game.get_dice_map.return_value = dice_map
        ret_map = {player1name:[1, 5, 4, 2], player2name:[3, 5, 4, 5]}
        
        self.subject.on_win(player1, player2, bid)

        self.data.get_game_views.assert_called_with()
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
    """Return a test suite of all tests defined in this module"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(ProxyDispatcherTest))
    test_suite.addTests(loader.loadTestsFromTestCase(ProxyGameTest))
    return test_suite


if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
