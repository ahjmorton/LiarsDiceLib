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

The module also provides objects to have messages sent out to all players
and views based on certain events in the game through the Proxy classes"""

class ProxyGame(object) :
    """The proxy game class is reponsible for dispatching events to game
and player listeners based on various events.
The way this is performed is that the proxy game sits between a client 
caller and the game object.
All calls are forwarded to the game object unaltered but events are generated
and dispatched"""

    def __init__(self, game, data_store) :
        self.game = game
        self.store = data_store
    
    def add_game_view(self, view) :
        """Add a game view to the list of objects to dispatch to"""
        self.store.add_game_view(view)

    def _get_game_views(self) :
        """Return a list of game views"""
        return self.store.get_game_views()

    def _get_all_players(self) :
        """Return a list of all players"""
        return self.store.get_all_players()

    def _burst_to_game_views(self, func) :
        """Burst an event to all game views.
Function should take one arguement"""
        for view in self._get_game_views() :
            func(view)

    def _burst_activations(self, players) :
        for player in players :
            self._burst_to_game_views(lambda view : 
                view.on_activation(player))

    def start_game(self) :
        """Start a game then burst to all game and player views"""
        self.game.start_game()
        player_names = self._get_all_players()
        cur = self.game.get_current_player()
        self._burst_to_game_views(lambda view : 
            view.on_game_start(cur, player_names))

    def activate_players(self) :
        """Activate all players, inform all game views and players"""
        self.game.activate_players()
        self._burst_activations(self._get_all_players())

    def end_game(self, winner) :
        """End the game then, inform all game views and players"""
        self.game.end_game(winner)
        self._burst_to_game_views(lambda view : 
             view.on_game_end(winner))

    def set_current_player(self, player) :
        """Set the current player.
If a previous player is available then inform them that there turn is over
and burst this to game views.
Always inform the current player that there turn has started and burst
to game views"""
        cur = self.game.get_current_player()
        self.game.set_current_player(player)
        if cur is not None :
            # Avoid this section if setting the first player
            self._burst_to_game_views(lambda view : 
                view.on_player_end_turn(cur))
            self._burst_to_game_views(lambda view : 
                view.on_player_start_turn(player))

    def add_player(self, player) :
        """Add a player to the game and inform all game views"""
        self.game.add_player(player)
        self._burst_to_game_views(lambda view : 
             view.on_player_addition(player))

    def remove_player(self, player) :
        """Remove a player to the game and inform all game views"""
        self.game.remove_player(player)
        self._burst_to_game_views(lambda view : 
            view.on_player_remove(player))

    def set_dice(self, player, dice) :
        """Set the dice for a player, burst the new amounts and inform
the player that they have been updated"""
        self.game.set_dice(player, dice)
        new_dice = len(self.game.get_dice(player))
        self._burst_to_game_views(lambda view : 
              view.on_new_dice_amount(player, new_dice))
        self._burst_to_game_views(lambda view : 
              view.on_set_dice(player, dice))
    
    def set_bid(self, player, bid) :
        """Set the bid assigned to a player, burst the bid to game views"""
        self.game.set_bid(player, bid) 
        self._burst_to_game_views(lambda view : 
            view.on_bid(player, bid))

    def remove_dice(self, player) :
        """Remove a dice from a player then burst to player and game views"""
        self.game.remove_dice(player)
        new_dice = len(self.game.get_dice(player))
        self._burst_to_game_views(lambda view : 
              view.on_new_dice_amount(player, new_dice))

    def on_win(self, winner, loser, bid) :
        """Get the dice map before the lose conditions occur.
Convert the player objects into strings representing there names
and dice values. 
Burst this out to the game views"""
        dice_map = self.game.get_dice_map()
        self.game.on_win(winner, loser, bid)
        self._burst_to_game_views(lambda view : 
            view.on_challenge(winner, loser, dice_map, bid))

    def deactivate_player(self, player) :
        """Deactivate player, inform them and burst to game views"""
        self.game.deactivate_player(player)
        self._burst_to_game_views(lambda view : 
            view.on_deactivate(player))

class ProxyDispatcher(object) :
    """The proxy dispatcher object dispatches attribute lookups"""

    def __init__(self, game, proxy) :
        self.game = game
        self.proxy = proxy

    def __getattr__(self, attrib) :
        """If the game object provided at construction has an attribute
that is not available in the proxy then dispatch to the game object.
Otherwise disptach to the proxy object"""
        if hasattr(self.game, attrib) and not hasattr(self.proxy, attrib) :
            return getattr(self.game, attrib)
        else :
            return getattr(self.proxy, attrib)


if __name__ == "__main__" :
    pass
