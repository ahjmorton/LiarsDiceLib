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
Test the game data object.
This module relies on the mock library for mocking of dependencies."""


import unittest

from mock import Mock

import game
import game_views
import game_data

class GameDataTest(unittest.TestCase) :

    def setUp(self) :
        self.starting = 3
        self.subject = game_data.GameData(self.starting)

    def testSettingPlayer(self) :
        player1 = Mock(spec=game_views.Player)
        self.subject.set_current_player(player1)
        self.assertEquals(player1, self.subject.get_current_player())
    
    def testSettingState(self) :
        state = Mock()
        self.subject.set_current_state(state)
        self.assertEquals(state, self.subject.get_current_state())

    def testStartingState(self) : 
        players = self.subject.get_players()
        self.assertTrue(players is not None)
        self.assertEquals(None, self.subject.get_current_player())
        self.assertEquals(None, self.subject.get_current_state())
        self.assertEquals(0, len(players))
        self.assertEquals(self.subject.get_num_of_starting_dice(), 
                          self.starting)

    def testAddingPlayer(self) :
        player = Mock(spec=game_views.Player)
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
        player = Mock(spec=game_views.Player)
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
        player = Mock(spec=game_views.Player)
        self.subject.add_player(player)
        dice = [1, 2, 3, 4]
        self.subject.set_dice(player, dice)
        self.assertTrue(dice == self.subject.get_dice(player))

    def testMakingPlayerInactive(self) :
        player = Mock(spec=game_views.Player)
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
        player = Mock(spec=game_views.Player)
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

    def testAddingDiceWithNoPlayerThrowsException(self) :
        player = Mock(spec=game_views.Player)
        dice = [1, 2, 3, 4]
        def caller() :
            self.subject.set_dice(player, dice)
        self.assertRaises(ValueError, caller)
    
    def testAddingBids(self) :
        player = Mock(spec=game_views.Player)
        self.subject.add_player(player)
        bid = (2, 4)
        self.subject.set_bid(player, bid)
        self.assertTrue(bid == self.subject.get_bid(player))

    def testCheckingForActive(self) :
        player = Mock(spec=game_views.Player)
        self.subject.add_player(player)
        self.subject.make_all_active()

        ret = self.subject.is_active(player)

        self.assertTrue(ret)
        self.subject.mark_inactive(player)

        ret = self.subject.is_active(player)

        self.assertTrue(not ret)

    def testSettingBidWithNoPlayerThrowsException(self) :
        player = Mock(spec=game_views.Player)
        bid = (1, 2)
        def caller() :
            self.subject.set_bid(player, bid)
        self.assertRaises(ValueError, caller)

def suite() :
    """Return a test suite of all tests defined in this module"""
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(GameDataTest))
    return test_suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
