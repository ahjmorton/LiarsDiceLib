class GameData(object) :
    """The game object is responsible for maintaining state about the game in progresss.

    It maintains a list of players in the game as well as the dice values for each player"""
    
    def __init__(self) :
        """Create a game object with a random source"""
        self.dice_roll = dice_sim
        self.dice = map()

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
        if player is not in self.dice :
            raise ValueError
        else :
            self.dice[player][1] = bid

class GameState(object) :
    """The game state object controls the games reaction to certain events based on the current event"""

    def __init__(self, game) :
        self.game = game

    def on_game_start(self, human_player) :
        pass

    def on_bid(self) :
        pass

    def on_challenge(self, challanger) :
        pass

class Game(object) :
    """The game object provides the application logic for the game and enforcing the game rules."""

    def __init__(self, data, start_state) :
        self.plays = state
        self.state = start_state
        self.cur_player = None

    def start_game(self, human_player) :
        self.state = self.state.on_game_start(start_player)

    def set_current_player(self, player) :
        self.cur_player = player

    def get_current_player(self) :
        return self.cur_player

    def make_bid(self, bid) :
        """Make a bid for the current player in a tuple format"""
        self.plays.set_bid(self.cur_player, bid)
        self.state = self.state.on_bid()

    def make_challenge(self, challenger) :
        """Register a challange against the current player"""
        self.state = self.state.on_challenge(challenger, self.cur_player)
