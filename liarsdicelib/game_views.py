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

This module defines the game view objects"""


class GameView(object) :
    """This object represents an observer on the game object for updating a user
 interface"""

    
    def on_game_start(self, starting_player, player_list) :
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
    
    def on_set_dice(self, player_name, dice) :
        """This method is called when the dice are set for the player"""
        pass

    def on_new_dice_amount(self, player_name, amount) :
        """This method is called when a players dice aomunt changes"""
        pass

    def on_bid_reset(self) :
        """This method is called when the bid is reset to None after
a challenge"""
        pass

    def on_error(self, value) :
        """This method is called when there is an error with the remote"""
        pass


if __name__ == "__main__" : 
    pass
