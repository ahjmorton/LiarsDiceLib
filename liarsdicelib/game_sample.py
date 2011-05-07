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

This module provides a sample game showing how the game will flow with
text output."""

from functools import partial

import random
import game
import game_state
import game_views
import game_data
import game_proxy

class RobotGameView(game_views.GameView) :
    pass

def main() :

    #Initialise game data store and add players
    starting_dice = 6
    lowest_face = 1
    highest_face = 6
    data_store = game_data.GameData(
        starting_dice, 
        lowest_face, 
        highest_face)

    #Create the proxy game objects with game views
    view = RobotGameView()
    proxy = game_proxy.ProxyGame(None, data_store)
    proxy_dispatcher = game_proxy.ProxyDispatcher(None, proxy)
    data_store.add_game_view(view)

    #Initialise players
    players = ["Player %i" % x for x in xrange(0, 6)]
    for player in players :
        data_store.add_player(player)

    #Create the utility objects
    dice_roller = game_state.roll_set_of_dice
    win_checker = game.get_winner
    bid_checker = game.check_bids
    win_handler = game.on_win
    win_handler = partial(win_handler, game=proxy_dispatcher)
    
    #Create the game states from last to first
    bid_state = game_state.BidState(proxy_dispatcher, 
        None)
    first_bid_state = game_state.FirstBidState(proxy_dispatcher, 
        bid_state)
    game_start_state = game_state.GameStartState(proxy_dispatcher, 
        first_bid_state, dice_roller)
    bid_state.next = game_start_state

    #Create the game object
    game_obj = game.Game(data_store, win_handler, bid_checker, 
        win_checker)
    game_obj.set_state(game_start_state)
    proxy.game = game_obj
    proxy_dispatcher.game = game_obj
    proxy_dispatcher.start_game()

if __name__ == "__main__" :
    main()
