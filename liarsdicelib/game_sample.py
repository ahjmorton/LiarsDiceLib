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

def generate_face_value(current, highest, lowest) :
    next_val = (current + 1) % highest
    if next_val < lowest :
        next_val = lowest
    return next_val

class RobotGameView(game_views.GameView) :
    
    __GAME_STARTED = "stated_game"
    __GAME_ENDED = "end_game"
    __GAME_CHALLENGED = "challenge"

    def __init__(self, game_obj, face_val_gen) :
        self.game = game_obj
        self.face_gen = face_val_gen
        self.event_loop = list()

    def on_bid_reset(self) :
        """This method is called at the start of a round"""
        print "Bid has been reset"

    def on_game_start(self, first_player, player_list) :
        """This method is called when the game begins. It contains a list of pla
yers who are in the game"""
        print "Game started first player %s out of %s" % (first_player, player_list)
        self.event_loop.append(RobotGameView.__GAME_STARTED)

    def on_bid(self, player_name, bid) :
        """This method is called when a player bids with the players name and a 
bid"""
        print "Player %s made bid %s" % (player_name, bid)

    def on_challenge(self, winner, loser, old_dice_map, bid) :
        """This method is called at the end of a challenge with the challenger, 
challenged, the winner and dice of each player"""
        print "Challenge Bid: %s Dice map %s. Winner : %s Loser: %s" \
              % (bid, old_dice_map, winner, loser)
        self.event_loop.append(RobotGameView.__GAME_CHALLENGED)

    def on_activation(self, player_name) :
        """This method is called when a player is made active"""
        print "%s made active" % player_name
    
    def on_player_start_turn(self, player_name) :
        """This method is called when a player is made the current player"""
        print "%s started turn" % player_name
            
    def on_player_end_turn(self, player_name) :
        """This methodi s called when a player's turns ends"""
        print "%s ended turn" % player_name

    def on_player_addition(self, player_name) :
        """This method is called when a player is added to the game"""
        print "%s added to game" % player_name

    def on_player_remove(self, player_name) :
        """This method is called when a player is removed from the game"""
        print "%s removed from game" % player_name

    def on_deactivate(self, player_name) :
        """This method is called when a player is deactivated"""
        print "%s made inactive" % player_name

    def on_game_end(self, winner_name) : 
        """This method is called when the game ends and gives the 
        players name"""
        print "Game over! Winner: %s" % winner_name
        self.event_loop.append(RobotGameView.__GAME_ENDED)
    
    def on_set_dice(self, player_name, dice) :
        """This method is called when the dice are set for the player"""
        print "Player %s had dice set : %s" % (player_name, dice)

    def on_new_dice_amount(self, player_name, amount) :
        """This method is called when a players dice aomunt changes"""
        print "Player %s had new dice amount : %s" % \
            (player_name, amount)

    def on_error(self, value) :
        """This method is called when there is an error with the remote"""
        print "Error detected : %s" % value

    def __create_bid(self) :
        truths = [True, False]
        current = self.game.get_previous_bid()
        next_bid = list(current)
        if random.choice(truths) :
            next_bid[0] = next_bid[0] + 1
        else :
            next_bid[1] = self.face_gen(next_bid[1])
            if next_bid[1] == 1 :
                next_bid[0] = next_bid[0] + 1
        return next_bid

    def go(self) :
        current = self.event_loop[0]
        event_loop = self.event_loop[1:]
        if current is not RobotGameView.__GAME_STARTED :
            raise Exception("first event is not game_started")
        while RobotGameView.__GAME_ENDED not in self.event_loop:
            if len(self.event_loop) > 0 :
                current = self.event_loop[0]
            else :
                current = None
            if self.game.get_previous_bid() is None :
                next_bid = (1, 1)
                self.game.make_bid(next_bid)
            else :
                if random.random() < 0.3 or \
                    self.game.get_previous_bid()[0] >= \
                    self.game.number_of_starting_dice() :
                    self.game.make_challenge()
                else :
                    next_bid = self.__create_bid()
                    self.game.make_bid(next_bid)
            if len(self.event_loop) > 0 :
                self.event_loop = self.event_loop[1:]
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
    proxy = game_proxy.ProxyGame(None, data_store)
    proxy_dispatcher = game_proxy.ProxyDispatcher(None, proxy)
    face_val_gen = partial(generate_face_value, \
               highest = highest_face, \
               lowest = lowest_face)
    view = RobotGameView(proxy_dispatcher, face_val_gen)
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
    bid_reset = game.bid_reset
    
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
        win_checker, bid_reset)
    game_obj.set_state(game_start_state)
    proxy.game = game_obj
    proxy_dispatcher.game = game_obj
    proxy_dispatcher.start_game()
    view.go()

if __name__ == "__main__" :
    main()
