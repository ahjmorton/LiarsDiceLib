import prng

class Player(object) :
    """This game object represents a game player with event based methods"""
    
    def __init__(self, name) :
        self.name = name

    def get_name(self) :
        return self.name

    def on_game_start(self, dice) :
        """This method is called when the game is started and the dice the player has are given"""
        pass

    def on_made_active(self) :
        """This method is called when a player is set as the current player"""
        pass

    def on_made_inactive(self) :
        """This method is called when a plahyer is made inactive"""
        pass

    def on_game_end(self) :
        """This method is called when the game ends"""
        pass

    def on_new_dice_amount(self, amount) :
        """This method is called when the dice amount changes, possibly due to a loss of dice"""
        pass

class GameView(object) :
    """This object represents an observer on the game object for updating a user interface"""

    
    def on_game_start(self, player_list) :
        """This method is called when the game begins. It contains a list of players who are in the game"""
        pass

    def on_bid(self, player_name, bid) :
        """This method is called when a player bids with the players name and a bid"""
        pass

    def on_challenge(self, challaneger, challenged, winner, dice_map) :
        """This method is called at the end of a challenge with the challenger, challenged, the winner and dice of each player"""
        pass

    def on_activation(self, player_name) :
        """This method is called when a player is made active"""
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

    def on_game_end(self, winner) : 
        """This method is called when the game ends and gives the players name"""
        pass

    def on_new_dice_amount(self, player, amount) :
        """This method is called when a players dice aomunt changes"""
        pass

class GameData(object) :
    """The game object is responsible for maintaining state about the game in progresss.

    It maintains a list of players in the game as well as the dice values for each player
    
    Additionally it holds the number of starting dice """
    
    def __init__(self, starting_dice=5) :
        """Create a game object with a random source"""
        self.dice = dict()
        self.inactive = set()
        self.starting = starting_dice

    def add_player(self, player) :
        """Add a player to the list of players in the round. If this method is not called then any call to add dice will fail. The player is added and is considered active on adding"""
        self.dice[player] = [None, None]

    def remove_player(self, player) : 
        """Remove player from the game"""
        del self.dice[player]
        self.inactive.discard(player)
    
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
        """Mark a player as being inactive, an inactive player is not included in a call to get_players"""
        self.inactive.add(player)

    def get_dice(self, player) :
        """Get the dice for a particular player"""
        return self.dice[player][0]

    def get_bid(self, player) :
        """Get the bid for a particular player"""
        return self.dice[player][1]

    def set_dice(self, player, dice) :
        """Set the dice a particular player has in their hand. If player has not had players added to it then raise a ValueError"""
        if player not in self.dice :
            raise ValueError
        else :
            self.dice[player][0] = dice
     
    def set_bid(self, player, bid) :
        """Set the bid for a particular player has made. If player has not been added to object then raise a value error"""
        if player not in self.dice :
            raise ValueError
        else :
            self.dice[player][1] = bid

    def get_num_of_starting_dice(self) :
        return self.starting

    def get_dice_map(self) :
        ret = dict() 
        for player in self.dice :
            ret[player] = self.get_dice(player)
        return ret

class MissingPlayerError(Exception) :
    
    def __init__(self, value) :
        self.val = value

    def __str__(self) :
        return repr(self.value)

class IllegalStateChangeError(Exception) :
    
    def __init__(self, value) :
        self.val = value

    def __str__(self) :
        return repr(self.value)

class IllegalBidError(Exception) :

    def __init__(self, value) :
        self.val = value

    def __str__(self) :
        return repr(self.value)

class BidChecker(object) :
    
    def check_bids(self, bid, dice) :
        die = bid[1]
        count = 0
        for x in dice :
            count = count + dice[x].count(die)
        return count >= bid[0]

class WinChecker(object) :
    
    def get_winner(self, dice_map) :
        cur_win = None
        for x in dice_map :
            if len(dice_map[x]) > 0 :
                if cur_win is not None :
                    return None
                else :
                    cur_win = x
        return cur_win

class DiceRoller(object) :
    
    def __init__(self, max_face=6, min_face=1, random=prng.get_random()) :
        self.face_min = min_face
        self.face_max = max_face
        self.rand = random

    def roll_dice(self) :
        return self.rand.randint(self.min_face, self.max_face)

    def roll_set_of_dice(self, num) :
        return [self.roll_dice() for x in xrange(num)]

class WinHandler(object) :

    def on_win(self, winner, loser, bid, game) :
        game.remove_dice(loser)

class GameState(object) :
    """The game state object controls the games reaction to certain events based on the current event. Default implementations of all state methods thrown illegal state change error"""

    def __init__(self, game) :
        self.game = game

    def on_game_start(self, human_player) :
        raise IllegalStateChangeError("Cannot call on_game_start")
        
    def on_bid(self, player, bid) :
        raise IllegalStateChangeError("Cannot call on_bid")

    def on_challenge(self, challanger, challenged) :
        raise IllegalStateChangeError("Cannot call on_challenge")

class GameStartState(GameState) :
    """This state is the state the game first enters in after the players have been added to the game. At this point the dice are shuffled and the first player for the round is chosen"""
    
    def __init__(self, game, enter_state, dice_roller) :
        GameState.__init__(self, game)
        self.first = enter_state
        self.dice_roll = dice_roller

    def on_game_start(self, human_player) : 
        """Game start should check the player provided is in the game data, if not thrown an error.
Also performs shuffling of dice """
        if not self.game.has_player(human_player) :
            raise MissingPlayerError("Player provided for starting of game not in list of players")
        else : 
            #Could also add logic to do random number generation to work out who goes first
            self.game.set_current_player(human_player)
            max_dice = self.game.number_of_starting_dice()
            for x in self.game.get_players() :
                self.game.set_dice(x, self.dice_roll.roll_set_of_dice(max_dice))
            return self.first

class FirstBidState(GameState) :
    def __init__(self, game, bid_state, new_game_state) :
        GameState.__init__(self, game)
        self.next = bid_state
        self.restart = new_game_state

    def on_game_start(self, human_player) :
        return self.restart.on_game_start(human_player)

    def on_bid(self, player, bid) :
        self.game.set_bid(player, bid)
        self.game.set_current_player(self.game.get_next_player())
        return self.next

class BidState(GameState) :

    def __init__(self, game, bid_state, new_game_state) :
        GameState.__init__(self, game)
        self.next = bid_state
        self.restart = new_game_state

    def on_game_start(self, human_player) :
        return self.restart.on_game_start(human_player)

    def on_bid(self, player, bid) :
        cur_bid = self.game.get_previous_bid()
        if bid[0] >= cur_bid[0] and bid[1] > cur_bid[1] :
            self.game.set_bid(player, bid)
            self.game.set_current_player(self.game.get_next_player())
            return self.next
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
            return self.next
        else :
            return self
        
class FinishedState(GameState) : 
    def __init__(self, game, end) :
        GameState.__init__(self, game)
        self.end = end

    def on_game_start(self, human_player) :
        return self.end.on_game_start(human_player)


class Game(object) :
    """The game object provides the application logic for the game and enforcing the game rules."""

    def __init__(self, data, start_state, bid_checker, win_checker, win_handler) :
        self.plays = data
        self.state = start_state
        self.cur_player = None
        self.bid_checker = bid_checker
        self.win_checker = win_checker
        self.win_handler = win_handler

    def start_game(self, first_player) :
        self.state = self.state.on_game_start(first_player)

    def get_winning_player(self) :
        return self.win_checker.get_winner(self.plays.get_dice_map())

    def end_game(self, winner) :
        pass

    def set_current_player(self, player) :
        self.cur_player = player

    def get_current_player(self) :
        return self.cur_player

    def get_next_player(self) :
        players = self.plays.get_players()
        index = players.index(self.cur_player) + 1
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
        return self.bid_checker.check_bids(bid, self.plays.get_dice_map())

    def remove_dice(self, player) :
        dice = self.plays.get_dice(player)
        dice = dice[:-1]
        self.plays.set_dice(player, dice)

    def get_previous_player(self) :
        players = self.plays.get_players()
        index = players.index(self.cur_player) - 1
        if index < 0 :
            index = len(players) - 1
        return players[index]

    def finished(self) :
        return self.win_checker.get_winner(self.plays.get_dice_map()) is not None

    def on_win(self, winner, loser, bid) :
        self.win_handler.on_win(winner, loser, bid, self)

    def get_previous_bid(self) :
        return self.plays.get_bid(self.get_previous_player())

    def get_current_bid(self) :
        return self.plays.get_bid(self.cur_player)

    def make_bid(self, bid) :
        """Make a bid for the current player in a tuple format"""
        self.state = self.state.on_bid(self.cur_player, bid)

    def make_challenge(self, challenger) :
        """Register a challange against the current player"""
        self.state = self.state.on_challenge(challenger, self.cur_player)

class GameObservable(object) :
    
    def __init__(self, game) :
        self.game = game

if __name__ == "__main__" :
    pass
