"""The game module provides a number of primitive and implementations for
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
    return [rand.randint(face_vals[0], face_vals[1]) 
           for i in xrange(num)]

def on_win(winner, loser, bid, game) :
    """Called at the end of a round to determine the effects for both
the winner and the loser based on the bid"""
    game.remove_dice(loser)
    if len(game.get_dice(loser)) <= 0 :
        game.deactivate_player(loser)
        game.set_current_player(winner)
    else :
        game.set_current_player(loser)

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


class MissingPlayerError(Exception) :
    """This exception occurs when a player that has not been added to the
game attempts to perform some action"""
    
    def __init__(self, value) :
        Exception.__init__()
        self.val = value

    def __str__(self) :
        return repr(self.value)


class IllegalStateChangeError(Exception) :
    """This exception occurs when a state method is called that would 
transition the game to an illegal state, for example bidding when the game
is over"""
    
    def __init__(self, value) :
        Exception.__init__(self)
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


class GameState(object) :
    """The game state object controls the games reaction to certain 
events based on the current event. Default implementations of all 
state methods thrown illegal state change error"""

    def __init__(self, game) :
        self.game = game

    def on_game_start(self, human_player) :
        raise IllegalStateChangeError("Cannot call on_game_start")
        
    def on_bid(self, player, bid) :
        raise IllegalStateChangeError("Cannot call on_bid")

    def on_challenge(self, challanger, challenged) :
        raise IllegalStateChangeError("Cannot call on_challenge")


class GameStartState(GameState) :
    """This state is the state the game first enters in after the players 
have been added to the game. 
At this point the dice are shuffled and the first player for 
the round is chosen"""
    
    def __init__(self, game, enter_state, dice_roller=roll_set_of_dice) :
        GameState.__init__(self, game)
        self.first = enter_state
        self.dice_roll = dice_roller

    def on_game_start(self, human_player) : 
        """Game start should check the player provided is in the game data, 
        if not thrown an error. Also performs shuffling of dice """
        if not self.game.has_player(human_player) :
            raise MissingPlayerError("""Player 
                provided for starting of game not in list of players""")
        else : 
            #Could also add logic to do random number generation 
            # to work out who  goes first
            self.game.activate_players()
            self.game.set_current_player(human_player)
            max_dice = self.game.number_of_starting_dice()
            face = self.game.get_face_values()
            for x in self.game.get_players() :
                self.game.set_dice(x, self.dice_roll(max_dice, face))
            self.game.set_state(self.first)

class FirstBidState(GameState) :
    def __init__(self, game, bid_state, new_game_state) :
        GameState.__init__(self, game)
        self.next = bid_state
        self.restart = new_game_state

    def on_game_start(self, human_player) :
        self.restart.on_game_start(human_player)

    def on_bid(self, player, bid) :
        self.game.set_bid(player, bid)
        self.game.set_current_player(self.game.get_next_player())
        self.game.set_state(self.next)

class BidState(GameState) :

    def __init__(self, game, bid_state, new_game_state) :
        GameState.__init__(self, game)
        self.next = bid_state
        self.restart = new_game_state

    def on_game_start(self, human_player) :
        self.restart.on_game_start(human_player)

    def on_bid(self, player, bid) :
        cur_bid = self.game.get_previous_bid()
        if bid[0] >= cur_bid[0] and bid[1] > cur_bid[1] :
            self.game.set_bid(player, bid)
            self.game.set_current_player(self.game.get_next_player())
        else :
            raise IllegalBidError((bid, cur_bid))
    
    def on_challenge(self, challenger, challenged) :
        bid = self.game.get_previous_bid()
        if self.game.true_bid(bid) :
            self.game.on_win(challenged, challenger, bid)
        else :
            self.game.on_win(challenger, challenged, bid)
        if self.game.finished() :
            self.game.end_game(self.game.get_winning_player())
            self.game.set_state(self.next)
        
class FinishedState(GameState) : 
    def __init__(self, game, end) :
        GameState.__init__(self, game)
        self.restart = end

    def on_game_start(self, human_player) :
        self.restart.on_game_start(human_player)


class Game(object) :
    """The game object provides the application logic for the game and enforcing
 the game rules."""

    def __init__(self, data, win_handler=on_win, bid_checker=check_bids, win_checker=get_winner) :
        self.plays = data
        self.bid_checker = bid_checker
        self.win_checker = win_checker
        self.win_handler = win_handler

    def set_state(self, state) :
        self.plays.set_current_state(state)

    def is_player_active(self, player) :
        return self.plays.is_active(player)

    def get_state(self) :
        return self.plays.get_current_state()

    def start_game(self, first_player) :
        self.get_state().on_game_start(first_player)

    def activate_players(self) :
        self.plays.make_all_active()

    def get_winning_player(self) :
        return self.win_checker(self.plays.get_dice_map())

    def end_game(self, winner) :
        pass

    def set_current_player(self, player) :
        self.plays.set_current_player(player)

    def get_current_player(self) :
        return self.plays.get_current_player()

    def get_next_player(self) :
        players = self.plays.get_players()
        index = players.index(self.get_current_player()) + 1
        if index >= len(players) :
            index = 0
        return players[index]

    def add_player(self, player) :
        self.plays.add_player(player)

    def remove_player(self, player) :
        self.plays.remove_player(player)

    def get_all_players(self) :
        return self.plays.get_all_players() 

    def set_dice(self, player, dice) :
        self.plays.set_dice(player, dice)

    def get_dice(self, player) :
        return self.plays.get_dice(player)

    def set_bid(self, player, bid) :
        self.plays.set_bid(player, bid)

    def get_bid(self, player) :
        return self.plays.get_bid(player)

    def get_players(self) :
        return self.plays.get_players()

    def number_of_starting_dice(self) :
        return self.plays.get_num_of_starting_dice()

    def has_player(self, player) :
        return player in self.plays.get_players()

    def true_bid(self, bid) :
        return self.bid_checker(bid, self.plays.get_dice_map())

    def get_dice_map(self) :
        return self.plays.get_dice_map()

    def remove_dice(self, player) :
        dice = self.plays.get_dice(player)
        dice = dice[:-1]
        self.plays.set_dice(player, dice)

    def get_previous_player(self) :
        players = self.plays.get_players()
        index = players.index(self.get_current_player()) - 1
        if index < 0 :
            index = len(players) - 1
        return players[index]

    def finished(self) :
        return self.win_checker(
              self.plays.get_dice_map()) is not None

    def on_win(self, winner, loser, bid) :
        self.win_handler(winner, loser, bid)

    def deactivate_player(self, player) :
        self.plays.mark_inactive(player)

    def get_previous_bid(self) :
        return self.plays.get_bid(self.get_previous_player())

    def get_current_bid(self) :
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

class ProxyGame(object) :
    
    def __init__(self, game) :
        self.game = game
        self.game_views = list()
    
    def add_game_view(self, view) :
        self.game_views.append(view)

    def get_game_views(self) :
        return self.game_views

    def _burst_to_game_views(self, func) :
        for view in self.game_views :
            func(view)

    def _burst_to_players(self, func) :
        for player in self.game.get_all_players() :
            func(player)

    def __get_all_player_names(self) :
        return [player.get_name() for player in self.game.get_all_players()]

    def _burst_dice_amounts(self, player) :
        new_dice = len(self.game.get_dice(player))
        player.on_new_dice_amount(new_dice)
        self._burst_to_game_views(lambda view : 
              view.on_new_dice_amount(player.get_name(), new_dice))
    
    def start_game(self, first_player) :
        self.game.start_game(first_player)
        player_names = self.__get_all_player_names()
        self._burst_to_game_views(lambda view : 
            view.on_game_start(player_names))
        self._burst_to_players(lambda player : player.on_game_start())

    def activate_players(self) :
        self.game.activate_players()
        self._burst_to_game_views(lambda view : 
            view.on_multi_activation(self.__get_all_player_names()))
        self._burst_to_players(lambda player : player.on_made_active())

    def end_game(self, winner) :
        self.game.end_game(winner)
        self._burst_to_game_views(lambda view : view.on_game_end(winner.get_name
()))
        self._burst_to_players(lambda player : player.on_game_end())

    def set_current_player(self, player) :
        cur = self.game.get_current_player()
        self.game.set_current_player(player)
        if cur is not None :
            # Avoid this section if setting the first player
            curname = cur.get_name()
            cur.on_end_turn()
            self._burst_to_game_views(lambda view : 
                view.on_player_end_turn(curname))
        playername = player.get_name()
        player.on_start_turn()
        self._burst_to_game_views(lambda view : 
             view.on_player_start_turn(playername))

    def add_player(self, player) :
        self.game.add_player(player)
        self._burst_to_game_views(lambda view : 
             view.on_player_addition(player.get_name()))

    def remove_player(self, player) :
        self.game.remove_player(player)
        self._burst_to_game_views(lambda view : 
            view.on_player_remove(player.get_name()))

    def set_dice(self, player, dice) :
        self.game.set_dice(player, dice)
        self._burst_dice_amounts(player)
        player.on_set_dice(dice)
    
    def set_bid(self, player, bid) :
        self.game.set_bid(player, bid) 
        self._burst_to_game_views(lambda view : 
            view.on_bid(player.get_name(), bid))

    def remove_dice(self, player) :
        self.game.remove_dice(player)
        self._burst_dice_amounts(player)

    def on_win(self, winner, loser, bid) :
        dice_map = self.game.get_dice_map()
        self.game.on_win(winner, loser, bid)
        ret_map = dict()
        for player in dice_map :
            ret_map[player.get_name()] = dice_map[player]
        winner = winner.get_name()
        loser = loser.get_name()
        self._burst_to_game_views(lambda view : 
            view.on_challenge(winner, loser, ret_map, bid))

    def deactivate_player(self, player) :
        self.game.deactivate_player(player)
        player.on_made_inactive()
        self._burst_to_game_views(lambda view : 
            view.on_deactivate(player.get_name()))

class ProxyDispatcher(object) :
    
    def __init__(self, game, proxy) :
        self.game = game
        self.proxy = proxy

    def __getattr__(self, attrib) :
        if hasattr(self.game, attrib) and not hasattr(self.proxy, attrib) :
            return getattr(self.game, attrib)
        else :
            return getattr(self.proxy, attrib)


if __name__ == "__main__" :
    pass
