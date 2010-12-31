class GameData(object) :
    """The game object is responsible for maintaining state about the game in progresss.

    It maintains a list of players in the game as well as the dice values for each player"""
    
    def __init__(self) :
        """Create a game object with a random source"""
        self.dice = dict()

    def add_player(self, player) :
        """Add a player to the list of players in the game. If this method is not called then any call to add dice will fail"""
        self.dice[player] = [None, None]

    def get_players(self) :
        """Return the players currently in the game"""
        return list(self.dice)

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
    """This state is the state the game first enters in after the players have been added to the game but before any moves have been played"""
    
    def __init__(self, game, enter_state) :
        GameState.__init__(self, game)
        self.first = enter_state

    def on_game_start(self, human_player) : 
        """Game start should check the player provided is in the game data, if not thrown an error"""
        if human_player not in self.game.get_state().get_players() :
            raise MissingPlayerError("Player provided for starting of game not in list of players")
        else : 
            #Could also add logic to do random number generation to work out who goes first
            self.game.set_current_player(human_player)
            return self.first


class Game(object) :
    """The game object provides the application logic for the game and enforcing the game rules."""

    def __init__(self, data, start_state) :
        self.plays = data
        self.state = start_state
        self.cur_player = None

    def start_game(self, human_player) :
        self.state = self.state.on_game_start(human_player)

    def set_current_player(self, player) :
        self.cur_player = player

    def get_current_player(self) :
        return self.cur_player

    def make_bid(self, bid) :
        """Make a bid for the current player in a tuple format"""
        self.state = self.state.on_bid(self.cur_player, bid)

    def make_challenge(self, challenger) :
        """Register a challange against the current player"""
        self.state = self.state.on_challenge(challenger, self.cur_player)

    def get_state(self) :
        return self.state
