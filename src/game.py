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

The game module provides a number of primitive and implementations for
playing liars dice. Included are objects to represent players, a datastore
interface with in-memory implemenation, game views, game state and condition
checkers.

The module also provides objects to have messages sent out to all players
and views based on certain events in the game through the Proxy classes"""

import random

def check_bids(bid, dice_map) :
    """Determine if the bid provided is correct, for example in the
commen hand version of liars dice
The bid object should be a sequence with the first entry being the number
of dice associated with the bid and the second being the face value.
The dice should be a dictionary type with the value of the dictionary
being a list of dice values.
Returns true if the bid is correct, false otherwise"""
    die = bid[1]
    count = 0
    for player in dice_map :
        count = count + dice_map[player].count(die)
    return count >= bid[0]


def get_winner(dice_map) :
    """Determine the winner of a round based on a dice map.
If there is no clear winner of the dicemap then return None"""
    cur_win = None
    for player in dice_map :
        if len(dice_map[player]) > 0 :
            if cur_win is not None :
                return None
            else :
                cur_win = player
    return cur_win


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

def on_win(winner, loser, bid, game) :
    """Called at the end of a round to determine the effects for both
the winner and the loser based on the bid"""
    game.remove_dice(loser)
    if len(game.get_dice(loser)) <= 0 :
        game.deactivate_player(loser)
        game.set_current_player(winner)
    else :
        game.set_current_player(loser)


class MissingPlayerError(Exception) :
    """This exception occurs when a player that has not been added to the
game attempts to perform some action"""
    
    def __init__(self, value) :
        Exception.__init__()
        self.val = value

    def __str__(self) :
        return repr(self.value)


class IllegalBidError(Exception) :
    """This exception occurs when a bid attempt is made that is illegal
given the current state of the game.
For example if the previous bid of the game was two dice showing a five 
then a bid is attempted with one six then this exception is thrown"""
    def __init__(self, value) :
        Exception.__init__(self)
        self.val = value

    def __str__(self) :
        return repr(self.value)

class IllegalStateChangeError(Exception) :
    """This exception occurs when an attempt is made to perform an illegal
state transition"""
    def __init__(self, value) :
        Exception.__init__(self)
        self.val = value

    def __str__(self) :
        return repr(self.value)  

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
        self.game.set_current_player(self.game.get_players()[0])
        max_dice = self.game.number_of_starting_dice()
        face = self.game.get_face_values()
        for player in self.game.get_players() :
            self.game.set_dice(player, self.dice_roll(max_dice, face))
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
        self.game.set_current_player(self.game.get_next_player())
        self.game.set_state(self.next)

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
        

class Game(object) :
    """The game object provides the application logic for the game and 
enforcing the game rules.
The game object can best be thought of as glue between the different 
game objects."""

    def __init__(self, data, win_handler=on_win, 
                 bid_checker=check_bids, win_checker=get_winner) :
        self.plays = data
        self.bid_checker = bid_checker
        self.win_checker = win_checker
        self.win_handler = win_handler

    def set_state(self, state) :
        """Set the current game state"""
        self.plays.set_current_state(state)

    def is_player_active(self, player) :
        """Return if a player is active.
An active player can make bids and challenge"""
        return self.plays.is_active(player)

    def get_state(self) :
        """Return the current game state object"""
        return self.plays.get_current_state()

    def start_game(self) :
        """Start a new game"""
        self.get_state().on_game_start()

    def activate_players(self) :
        """Make all players active"""
        self.plays.make_all_active()

    def get_winning_player(self) :
        """Return the game winner.
If there is more than one possible winner then return None"""
        return self.win_checker(self.plays.get_dice_map())

    def end_game(self, winner) :
        """End the game with the winner taking victory"""
        pass

    def set_current_player(self, player) :
        """Set the current player who can either challenge or bid"""
        self.plays.set_current_player(player)

    def get_current_player(self) :
        """Get the current player"""
        return self.plays.get_current_player()

    def get_next_player(self) :
        """Return the next player who will go after the current player"""
        players = self.plays.get_players()
        index = players.index(self.get_current_player()) + 1
        if index >= len(players) :
            index = 0
        return players[index]

    def add_player(self, player) :
        """Add a player to the game"""
        self.plays.add_player(player)

    def remove_player(self, player) :
        """Remove a player from the game"""
        self.plays.remove_player(player)

    def get_all_players(self) :
        """Get all players, including inactive ones"""
        return self.plays.get_all_players() 

    def set_dice(self, player, dice) :
        """Set the dice assigned to a player"""
        self.plays.set_dice(player, dice)

    def get_dice(self, player) :
        """Get the dice associated with a player"""
        return self.plays.get_dice(player)

    def set_bid(self, player, bid) :
        """Set the bid made by a player"""
        self.plays.set_bid(player, bid)

    def get_bid(self, player) :
        """Return the bid assigned to a player"""
        return self.plays.get_bid(player)

    def get_players(self) :
        """Return all active players"""
        return self.plays.get_players()

    def number_of_starting_dice(self) :
        """Get the number of dice given to each player at the start of the 
game"""
        return self.plays.get_num_of_starting_dice()

    def true_bid(self, bid) :
        """Return whether a bid is true. A true bid is a bid that will
result in a win for the bidder"""
        return self.bid_checker(bid, self.plays.get_dice_map())

    def get_dice_map(self) :
        """Return a dice map containing each player with there current dice"""
        return self.plays.get_dice_map()

    def remove_dice(self, player) :
        """Remove a single dice from a player"""
        dice = self.plays.get_dice(player)
        dice = dice[:-1]
        self.plays.set_dice(player, dice)

    def get_previous_player(self) :
        """Return the player who went previously"""
        players = self.plays.get_players()
        index = players.index(self.get_current_player()) - 1
        if index < 0 :
            index = len(players) - 1
        return players[index]

    def finished(self) :
        """Return whether the game is over"""
        return self.win_checker(
              self.plays.get_dice_map()) is not None

    def on_win(self, winner, loser, bid) :
        """Called when a round has completed and a winner and loser
have been declared."""
        self.win_handler(winner, loser, bid)

    def deactivate_player(self, player) :
        """Deactivate a player from the game. Deactivated players cannot
make bids or challenges but remain as listed players that can be activated
later"""
        self.plays.mark_inactive(player)

    def get_previous_bid(self) :
        """Return the bid assoicated with the previous player"""
        return self.plays.get_bid(self.get_previous_player())

    def get_current_bid(self) :
        """Return the current bid, the current bid is the bid assoicated
with the current player"""
        return self.plays.get_bid(self.get_current_player())

    def make_bid(self, bid) :
        """Make a bid for the current player in a tuple format"""
        self.get_state().on_bid(self.get_current_player(), bid)

    def make_challenge(self, challenged=None, challenger=None) :
        """Register a challange against a certain player. 
        If Challenged is set to None then the previous player is used.
        If the challenger is none then the current player is used"""
        if challenged is None :
            challenged = self.get_previous_player()
        if challenger is None :
            challenger = self.get_current_player()
        self.get_state().on_challenge(challenger, challenged)

    def get_face_values(self) :
        """Return the highest and lowest faces on the dice"""
        return (self.plays.get_lowest_dice(), self.plays.get_highest_dice())

if __name__ == "__main__" :
    pass
