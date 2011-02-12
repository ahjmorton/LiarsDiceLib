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

This module defines the player and game view objects"""


class Player(object) :
    """This game object represents a game player with event based methods"""
    
    def __init__(self, name) :
        """Create a player with a given name"""
        self.name = name

    def get_name(self) :
        """Return the name of the player passed in at creation"""
        return self.name

    def on_game_start(self) :
        """This method is called when the game is started and the dice the playe
r has are given"""
        pass

    def on_set_dice(self, dice) :
        """This method is called when the dice are set for the player"""
        pass

    def on_start_turn(self) :
        """This method is called when the player is made the current player"""
        pass

    def on_end_turn(self) :
        """This method is called when the player is done with his turn"""
        pass

    def on_made_active(self) :
        """This method is called when a player is set as active, at the start of
 a round"""
        pass

    def on_made_inactive(self) :
        """This method is called when a plahyer is made inactive"""
        pass

    def on_game_end(self) :
        """This method is called when the game ends"""
        pass

    def on_new_dice_amount(self, amount) :
        """This method is called when the dice amount changes, possibly due to a
 loss of dice"""
        pass


class GameView(object) :
    """This object represents an observer on the game object for updating a user
 interface"""

    
    def on_game_start(self, player_list) :
        """This method is called when the game begins. It contains a list of pla
yers who are in the game"""
        pass

    def on_bid(self, player_name, bid) :
        """This method is called when a player bids with the players name and a 
bid"""
        pass

    def on_challenge(self, winner, loser, old_dice_map, bid) :
        """This method is called at the end of a challenge with the challenger, 
challenged, the winner and dice of each player"""
        pass

    def on_activation(self, player_name) :
        """This method is called when a player is made active"""
        pass
    
    def on_multi_activation(self, player_names) :
        """This method is called when a number of players are made active"""
        pass

    def on_player_start_turn(self, player_name) :
        """This method is called when a player is made the current player"""
        pass
    
    def on_player_end_turn(self, player_name) :
        """This methodi s called when a player's turns ends"""
        pass

    def on_player_addition(self, player_name) :
        """This method is called when a player is added to the game"""
        pass

    def on_player_remove(self, player_name) :
        """This method is called when a player is removed from the game"""
        pass

    def on_deactivate(self, player_name) :
        """This method is called when a player is deactivated"""
        pass

    def on_game_end(self, winner_name) : 
        """This method is called when the game ends and gives the 
        players name"""
        pass

    def on_new_dice_amount(self, player_name, amount) :
        """This method is called when a players dice aomunt changes"""
        pass

    def on_error(self, value) :
        """This method is called when there is an error with the remote"""
        pass


if __name__ == "__main__" : 
    pass
