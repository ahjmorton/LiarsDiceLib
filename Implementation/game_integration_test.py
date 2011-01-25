import unittest
from mock import Mock

import game
import prng

class GameIntegrationTest(unittest.TestCase) :

    def set_mocks_up(self) : 
        self.player1.get_name.return_value = self.player1name
        self.player2.get_name.return_value = self.player2name

    def reset_mocks(self) :
        self.player1.reset_mock()
        self.player2.reset_mock()
        self.view.reset_mock()

    def reset_and_setup_mocks(self) :
        self.reset_mocks()
        self.set_mocks_up()

    def setUp(self) :
        
        #Initialise players
        self.player1 = Mock(spec=game.Player)
        self.player2 = Mock(spec=game.Player)
        self.player1name = "Player1"
        self.player2name = "Player2"
        self.set_mocks_up()

        #Initialise game data store and add players
        self.starting_dice = 3
        self.lowest_face = 1
        self.highest_face = 6
        self.data_store = game.GameData(self.starting_dice, self.lowest_face, self.highest_face)
        self.data_store.add_player(self.player1)
        self.data_store.add_player(self.player2)
 
        #Create the proxy game objects with game views
        self.view = Mock(spec=game.GameView)
        self.proxy = game.ProxyGame(None)
        self.proxy_dispatcher = game.ProxyDispatcher(None, self.proxy)
        self.proxy.add_game_view(self.view)

        #Create the utility objects
        self.random = prng.get_random()
        self.dice_roller = game.DiceRoller(self.random)
        self.win_checker = game.WinChecker()
        self.bid_checker = game.BidChecker()
        self.win_handler = game.WinHandler(self.proxy_dispatcher)
        
        #Create the game states from last to first
        self.game_end_state = game.FinishedState(self.proxy_dispatcher, None)
        self.bid_state = game.BidState(self.proxy_dispatcher, self.game_end_state, None)
        self.first_bid_state = game.FirstBidState(self.proxy_dispatcher, self.bid_state, None)
        self.game_start_state = game.GameStartState(self.proxy_dispatcher, self.first_bid_state, self.dice_roller)
        self.game_end_state.restart = self.game_start_state
        self.first_bid_state.restart = self.game_start_state
        self.bid_state.restart = self.game_start_state

        #Create the game object
        self.game = game.Game(self.data_store, self.game_start_state, self.bid_checker, self.win_checker, self.win_handler)
        self.proxy.game = self.game
        self.proxy_dispatcher.game = self.game

    def testStartingAGame(self) :
        self.proxy_dispatcher.start_game(self.player1)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player1, self.game.get_current_player())
        self.player1.on_made_active.assert_called_with()
        self.player2.on_made_active.assert_called_with()
        self.player1.on_game_start.assert_called_with()
        self.player2.on_game_start.assert_called_with()
        self.player1.on_new_dice_amount.assert_called_with(self.starting_dice)
        self.player1.on_start_turn.assert_called_with()
        dice_map = self.data_store.get_dice_map()
        self.assertEquals(2, len(dice_map))
        self.assertTrue(self.player1 in dice_map)
        self.assertTrue(self.player2 in dice_map)
        for player in dice_map :
            dice = dice_map[player]
            self.assertEquals(self.starting_dice, len(dice))
            self.assertTrue(all(map(lambda x : self.lowest_face <= x <= self.highest_face, dice)))
            player.on_set_dice.assert_called_with(dice)
        player_names = map(lambda player : player.get_name(), dice_map)
        self.view.on_game_start.assert_called_with(player_names)
        self.view.on_multi_activation.assert_called_with(player_names)
        self.assertEquals(2, self.view.on_new_dice_amount.call_count)
        players = set(player_names)
        for args in self.view.on_new_dice_amount.call_args_list :
            self.assertEquals(self.starting_dice, args[0][1])
            player = args[0][0]
            self.assertTrue(player in players)
            players.remove(player)
        self.assertEquals(0, len(players))
        self.assertEquals(self.first_bid_state, self.game.get_state())

    def testBiddingWithoutStartingGameThrowsException(self) :
        cur_bid = (1,2)
        def call() :
            self.proxy_dispatcher.make_bid(cur_bid)
        self.assertRaises(game.IllegalStateChangeError, call)
        self.assertTrue(self.game.get_current_player() is None)
        self.assertTrue(self.game.get_state() is not None)
        self.assertEquals(self.game_start_state, self.game.get_state())

    def testFirstBid(self) :
        self.proxy_dispatcher.start_game(self.player1)
        self.reset_and_setup_mocks()
        cur_bid = (2, 5)

        self.proxy_dispatcher.make_bid(cur_bid)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player2, self.game.get_current_player())
        player_names = map(lambda player : player.get_name(), (self.player1, self.player2))
        self.player1.on_end_turn.assert_called_with()
        self.player2.on_start_turn.assert_called_with()
        self.view.on_bid.assert_called_with(self.player1name, cur_bid)
        self.view.on_player_end_turn.assert_called_with(self.player1name)
        self.view.on_player_start_turn.assert_called_with(self.player2name)
        self.assertEquals(self.bid_state, self.game.get_state())

    def testTwoBidsWithBidAfterwards(self) :
        self.proxy_dispatcher.start_game(self.player1)
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        self.reset_and_setup_mocks()
        cur_bid = (3, 6)

        self.proxy_dispatcher.make_bid(cur_bid)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player1, self.game.get_current_player())
        player_names = map(lambda player : player.get_name(), (self.player1, self.player2))
        self.player1.on_start_turn.assert_called_with()
        self.player2.on_end_turn.assert_called_with()
        self.view.on_bid.assert_called_with(self.player2name, cur_bid)
        self.view.on_player_start_turn.assert_called_with(self.player1name)
        self.view.on_player_end_turn.assert_called_with(self.player2name)
        self.assertEquals(self.bid_state, self.game.get_state())

    def testTwoBidsWithBadBid(self) :
        self.proxy_dispatcher.start_game(self.player1)
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        self.reset_and_setup_mocks()
        cur_bid = (2, 3)

        def call() :
            self.proxy_dispatcher.make_bid(cur_bid)
        self.assertRaises(game.IllegalBidError, call)

        self.assertTrue(self.game.get_current_player() is not None)
        self.assertEquals(self.player2, self.game.get_current_player())
        self.assertEquals(self.bid_state, self.game.get_state())
        self.assertTrue(not self.player2.on_end_turn.called)
        self.assertTrue(not self.view.on_bid.called)
        self.assertTrue(not self.view.on_player_start_turn.called)
        self.assertTrue(not self.view.on_player_end_turn.called)

    def testChallengeWithFirstPlayerWin(self) :
        self.proxy_dispatcher.start_game(self.player1)
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2,5]
        player2dice = [6,5]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        self.reset_and_setup_mocks()

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player2, self.game.get_current_player())
        self.player2.on_end_turn.assert_called_with()
        self.player2.on_start_turn.assert_called_with()
        self.assertEquals(1, len(self.data_store.get_dice(self.player2)))
        self.player2.on_new_dice_amount.assert_called_with(1)
        self.view.on_player_start_turn.assert_called_with(self.player2name)
        self.view.on_player_end_turn.assert_called_with(self.player2name)
        self.view.on_challenge.assert_called_with(self.player1name, self.player2name,{self.player1name:player1dice, self.player2name:player2dice}, first_bid)

    def testChallengeWithFirstPlayerLoss(self) :
        self.proxy_dispatcher.start_game(self.player1)
        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2,5]
        player2dice = [6,4]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        self.reset_and_setup_mocks()

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player1, self.game.get_current_player())
        self.player2.on_end_turn.assert_called_with()
        self.player1.on_start_turn.assert_called_with()
        self.assertEquals(1, len(self.data_store.get_dice(self.player1)))
        self.player1.on_new_dice_amount.assert_called_with(1)
        self.view.on_player_start_turn.assert_called_with(self.player1name)
        self.view.on_player_end_turn.assert_called_with(self.player2name)
        self.view.on_challenge.assert_called_with(self.player2name, self.player1name,{self.player1name:player1dice, self.player2name:player2dice}, first_bid)     

    def testChallengeResultingInFirstPlayerGettingDeactivated(self) :
        # Add a new player, don't want deactivation to end in a win
        player3 = Mock(spec=game.Player)
        player3name = "player 3"
        player3.get_name.return_value = player3name
        self.data_store.add_player(player3)

        self.proxy_dispatcher.start_game(self.player1)

        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [5]
        player2dice = [6,4]
        player3dice = [2,2]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        self.data_store.set_dice(player3, player3dice)
        self.reset_and_setup_mocks()

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player2, self.game.get_current_player())
        
        self.player2.on_end_turn.assert_called_with()
        self.player2.on_start_turn.assert_called_with()
        self.player1.on_made_inactive.assert_called_with()
        self.assertEquals(0, len(self.data_store.get_dice(self.player1)))
        self.assertTrue(not self.data_store.is_active(self.player1))
        self.player1.on_new_dice_amount.assert_called_with(0)
        self.view.on_player_start_turn.assert_called_with(self.player2name)
        self.view.on_player_end_turn.assert_called_with(self.player2name)
        self.view.on_challenge.assert_called_with(self.player2name, self.player1name,{self.player1name:player1dice, self.player2name:player2dice, player3name:player3dice}, first_bid)     
        self.view.on_deactivate.assert_called_with(self.player1name)

    def testChallengeResultingInLoserGettingDeactivated(self) :        
        player3 = Mock(spec=game.Player)
        player3name = "player 3"
        player3.get_name.return_value = player3name
        self.data_store.add_player(player3)

        self.proxy_dispatcher.start_game(self.player1)

        first_bid = (2, 5)
        self.proxy_dispatcher.make_bid(first_bid)
        player1dice = [2,5]
        player2dice = [5]
        player3dice = [2,2]
        self.data_store.set_dice(self.player1, player1dice)
        self.data_store.set_dice(self.player2, player2dice)
        self.data_store.set_dice(player3, player3dice)
        self.reset_and_setup_mocks()

        self.proxy_dispatcher.make_challenge()

        self.assertEquals(self.player1, self.game.get_current_player())
        
        self.player2.on_end_turn.assert_called_with()
        self.player1.on_start_turn.assert_called_with()
        self.player2.on_made_inactive.assert_called_with()
        self.assertEquals(0, len(self.data_store.get_dice(self.player2)))
        self.assertTrue(not self.data_store.is_active(self.player2))
        self.player2.on_new_dice_amount.assert_called_with(0)
        self.view.on_player_start_turn.assert_called_with(self.player1name)
        self.view.on_player_end_turn.assert_called_with(self.player2name)
        self.view.on_challenge.assert_called_with(self.player1name, self.player2name,{self.player1name:player1dice, self.player2name:player2dice, player3name:player3dice}, first_bid)     
        self.view.on_deactivate.assert_called_with(self.player2name)

    def testChallengeResultingInFirstPlayerWinning(self) :
        pass

    def testChallengeResultingInFirstPlayerLoosing(self) :
        pass

    def testRestartingGameFromFirstBid(self) :
        pass

    def testRestartingGameFromSecondBid(self) :
        pass

    def testRestartingGameFromWinState(self) :
        pass

    def testAddingNewPlayer(self) :
        pass

    def testRemovingAPlayer(self) :
        pass

    def testRemovingAPlayerResultingInAWin(self) :
        pass

    def testRemovingCurrentPlayer(self) :
        pass

def suite() :
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(GameIntegrationTest))
    return suite

if __name__ == "__main__" :
    unittest.TextTestRunner().run(suite())
