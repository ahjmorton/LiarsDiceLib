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

from game_common import roll_set_of_dice

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

def on_win(winner, loser, bid, game) :
    """Called at the end of a round to determine the effects for both
the winner and the loser based on the bid"""
    game.reset_bid()
    game.remove_dice(loser)
    if len(game.get_dice(loser)) <= 0 :
        game.deactivate_player(loser)
        game.set_current_player(winner)
    else :
        game.set_current_player(loser)

def bid_reset(game) :
    """Reset the current bid of the game, this occurs at the end
of a challenge to set the bid to None"""
    game.set_bid(game.get_previous_player(), None)


class Game(object) :
    """The game object provides the application logic for the game and 
enforcing the game rules.
The game object can best be thought of as glue between the different 
game objects."""

    def __init__(self, data, win_handler=on_win, 
                 bid_checker=check_bids, win_checker=get_winner,
                 bid_reset=bid_reset) :
        self.plays = data
        self.bid_checker = bid_checker
        self.win_checker = win_checker
        self.win_handler = win_handler
        self.bid_reset = bid_reset

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

    def num_of_dice(self, player) :
        """Return the number of dice a player has"""
        return self.plays.get_number_of_dice(player)

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

    def reset_bid(self) :
        """Reset the bid at the start of a round"""
        self.bid_reset(self)

if __name__ == "__main__" :
    pass
