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

This module contains a the data store for the game"""

class GameData(object) :
    """The game object is responsible for maintaining state about the game in pr
ogresss.
    It maintains a list of players in the game as well as the dice values for ea
ch player
    Additionally it holds the number of starting dice """
    
    def __init__(self, starting_dice=5, lowest_face=1, highest_face=6) :
        """Create a game object with a random source"""
        self.dice = dict()
        self.inactive = set()
        self.starting = starting_dice
        self.low = lowest_face
        self.high = highest_face
        self.cur_player = None
        self.cur_state = None
        self.game_views = list()

    def add_game_view(self, view) :
        """Add a game view to the list of game views"""
        self.game_views.append(view)

    def get_game_views(self) :
        """Return a list of game views"""
        return self.game_views

    def set_current_state(self, state) :
        """Set the current state of the game"""
        self.cur_state = state

    def get_current_state(self) :
        """Return the current state of the game"""
        return self.cur_state

    def get_current_player(self) :
        """Return the player whose turn it currently is"""
        return self.cur_player

    def set_current_player(self, player) :
        """Set the player whose current turn it is"""
        self.cur_player = player

    def add_player(self, player) :
        """Add a player to the list of players in the round. 
If this method is not called then any call to add dice will fail. 
The player is added and is considered active on adding"""
        self.dice[player] = [None, None]

    def remove_player(self, player) : 
        """Remove player from the game"""
        del self.dice[player]
        self.inactive.discard(player)

    def is_active(self, player) :
        """Return if a player is active"""
        return player not in self.inactive
    
    def get_players(self) :
        """Return the players currently marked active"""
        return list(set(self.dice) - self.inactive) 

    def get_all_players(self) :
        """Return all players, including those marked inactive"""
        return list(self.dice)

    def make_all_active(self) :
        """Mark all players as active"""
        self.inactive.clear()

    def mark_inactive(self, player) :
        """Mark a player as being inactive, an inactive player is not included i
n a call to get_players"""
        self.inactive.add(player)

    def get_dice(self, player) :
        """Get the dice for a particular player"""
        return self.dice[player][0]

    def get_bid(self, player) :
        """Get the bid for a particular player"""
        return self.dice[player][1]

    def set_dice(self, player, dice) :
        """Set the dice a particular player has in their hand. If player has not
 had players added to it then raise a ValueError"""
        if player not in self.dice :
            raise ValueError
        else :
            self.dice[player][0] = dice
     
    def set_bid(self, player, bid) :
        """Set the bid for a particular player has made. If player has not been 
added to object then raise a value error"""
        if player not in self.dice :
            raise ValueError
        else :
            self.dice[player][1] = bid

    def get_num_of_starting_dice(self) :
        """Get the number of dice given to each player at the start of the
game"""
        return self.starting

    def get_dice_map(self) :
        """Create a dictionary with each player and the dice values"""
        ret = dict() 
        for player in self.dice :
            ret[player] = self.get_dice(player)
        return ret

    def get_lowest_dice(self) :
        """Return the lowest possible face on a dice"""
        return self.low
    
    def get_highest_dice(self) :
        """Return the highest possible face on a dice"""
        return self.high


if __name__ == "__main__" :
    pass
