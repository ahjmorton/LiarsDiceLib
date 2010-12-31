class GameData(object) :
    """The game object is responsible for maintaining state about the game in progresss.

    It maintains a list of players in the game as well as the dice values for each player"""
    
    def __init__(self) :
    """Create a game object with a random source"""
        self.dice_roll = dice_sim
        self.dice = map()

    def add_player(self, player) :
    """Add a player to the list of players in the game. If this method is not called then any call to add dice will fail"""
        self.dice[player] = list()

    def get_players(self) :
    """Return the players currently in the game"""
        return list(self.dice)

    def get_dice(self, player) :
    """Get the dice for a particular player"""
        return self.dice[player]

    def set_dice(self, player, dice) :
    """Set the dice a particular player has in their hand. If player has not had players added to it then raise a ValueError"""
        if player not in self.dice :
            raise ValueError
        else :
            self.dice[player] = dice

class GameState(object) :
    """The game state object controls the games reaction to certain events based on the current event"""

    def __init__(self, game) :
        self.game = game

    def on_game_start(self, human_player) :
        pass

    def on_game_end(self) :
        pass

    def on_bid(self, player) :
        pass

    def on_no_challange(self, challanger, challenged) :
        pass

    def on_challenge(self, challanger, challenged) :
        pass

class Game(object) :

    """The game object provides the application logic for the game and enforcing the game rules."""
    def __init__(self, data, dice_roller, dice_sides, start_state) :
        self.plays = state
        self.roll = dice_roller
        self.dice_max = dice_sides
        self.state = start_state
        self.cur_player = None

    def start_game(self, human_player) :
        self.state = self.state.on_game_start(start_player)

    def set_current_player(self, player) :
        self.cur_player = player

    def get_current_player(self) :
        return self.cur_player

