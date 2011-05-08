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

This module holds the states used by the application"""

import random

from game_common import IllegalStateChangeError, IllegalBidError


def roll_set_of_dice(num, face_vals, rand=random) :
    """Roll a set of dice with values that are 
face_vals[0] <= n <= face_valls[1].
Source of randomness comes from prng module"""
    random.seed()
    ret_list = list()
    count = 0
    while count < num :
        ret_list.append(rand.randint(face_vals[0], face_vals[1]))
        count = count + 1
    return ret_list


class GameStartState(object) :
    """This state is the state the game first enters in after the players 
have been added to the game. 
At this point the dice are shuffled and the first player for 
the round is chosen"""
    
    def __init__(self, game, enter_state, dice_roller=roll_set_of_dice) :
        self.game = game
        self.first = enter_state
        self.dice_roll = dice_roller

    def on_game_start(self) : 
        """Game start should check the player provided is in the game data, 
if not thrown an error. Also performs shuffling of dice.
Currently the game starts with the first active player taking the current
player position"""
        #Could also add logic to do random number generation 
        # to work out who  goes first
        self.game.activate_players()
        max_dice = self.game.number_of_starting_dice()
        face = self.game.get_face_values()
        for player in self.game.get_players() :
            self.game.set_dice(player, self.dice_roll(max_dice, face))
        self.game.set_current_player(self.game.get_players()[0])
        self.game.set_state(self.first)
    
    def on_bid(self, player, bid) :
        """Illegal state transition, throw an exception"""
        raise IllegalStateChangeError(
            "%s attempted to bid %s before game started" 
               % (player, bid))
   
    def on_challenge(self, challenger, challenged) :
        """Illegal state transition, throw an exception"""
        raise IllegalStateChangeError(
             "%s trying to challenge %s before game started" %
                 (challenger, challenged))


class FirstBidState(object) :
    """This state is the state the game assumes once the game has started.
It's job is to accept the bid from the player (without checking it for
validity) then setting the next player"""
    def __init__(self, game, bid_state) :
        self.game = game
        self.next = bid_state

    def on_game_start(self) :
        """Illegal state transition, throw an exception"""
        raise IllegalStateChangeError(
              "Attempt to start an already started game")

    def on_bid(self, player, bid) :
        """Accept the bid from the player without validation"""
        self.game.set_bid(player, bid)
        self.game.set_state(self.next)
        self.game.set_current_player(self.game.get_next_player())

    def on_challenge(self, challenger, challenged) :
        """Illegal state transition, throw an exception"""
        raise IllegalStateChangeError(
             "%s trying to challenge %s before first bid" %
                 (challenger, challenged))


class BidState(object) :
    """The bid state is the state the game is for the majority of the game.
It accepts bids and challenge and modifies game state accordingly"""
    def __init__(self, game, bid_state) :
        self.game = game
        self.next = bid_state
    
    def on_game_start(self) :
        """Illegal state transition, throw an exception"""
        raise IllegalStateChangeError(
            "Attempt to start an already started game")

    def on_bid(self, player, bid) :
        """Take a bid, validate it against the previous bid then set the
bid as the current bid and set the next player"""
        cur_bid = self.game.get_previous_bid()
        if bid[0] >= cur_bid[0] and bid[1] > cur_bid[1] :
            self.game.set_bid(player, bid)
            self.game.set_current_player(self.game.get_next_player())
        else :
            raise IllegalBidError((bid, cur_bid))
    
    def on_challenge(self, challenger, challenged) :
        """Handle a challenge, and end the game if finished"""
        bid = self.game.get_previous_bid()
        if self.game.true_bid(bid) :
            self.game.on_win(challenged, challenger, bid)
        else :
            self.game.on_win(challenger, challenged, bid)
        if self.game.finished() :
            self.game.end_game(self.game.get_winning_player())
            self.game.set_state(self.next)
        
if __name__ == "__main__" :
    pass
