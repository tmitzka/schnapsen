"""Schnapsen is a text-based card game for two players."""

from time import sleep
import gettext

from schnapsen_classes import SchnapsenPlayer, SchnapsenGame


# Set language.
LANGUAGE = "en"

# Translate strings.
translation = gettext.translation("schnapsen", "locales", [LANGUAGE])
translation.install()

# Set other constants.
PLAYER_NAMES = (_("Player"), _("Computer"))
SECONDS = 1.5


def create_players():
    """Create the players."""
    player1 = SchnapsenPlayer(PLAYER_NAMES[0], human=True)
    player2 = SchnapsenPlayer(PLAYER_NAMES[1])
    players = [player1, player2]
    print(_("Welcome, {} and {}!").format(player1.name, player2.name), end=" ")
    print(_("{}, you will begin.").format(player1.name))
    return players


def start_new_game(players):
    """Create the game instance. Shuffle and deal the cards."""
    game = SchnapsenGame()
    game.create_cards()
    game.shuffle_cards()
    for player in players:
        for dummy in range(5):
            card = game.draw_from_stock()
            player.add_card(card)
    return game


def game_loop(game, players):
    """Run the game loop."""
    while True:

        # Start a new trick.
        trick = []
        for player in players:

            # Check whether the players have run out of cards.
            if not player.cards:
                print()
                print(_("We've run out of cards."))
                print(_("The player who took the last trick wins."))
                return

            # The first player may exchange the trump Jack
            # and/or close the stock.
            if not trick and not game.closed:
                if player.human:
                    exchange, close = player.choose_action_human(
                        game.trump_suit, game.trump_card
                    )
                else:
                    exchange, close = player.choose_action_computer(
                        game.trump_suit
                    )

                # The active player has chosen to exchange the trump
                # Jack for the trump card. The stock isn't closed yet.
                if exchange and not game.closed:
                    trump_jack = player.pop_trump_jack(game.trump_suit)
                    if player.human:
                        print("\n<", end=" ")
                        print(_("You take the {}.").format(
                                game.trump_card['name']
                            ))
                    else:
                        print("\n<", end=" ")
                        print(
                            _("{} takes the {}.").format(
                                player.name,
                                game.trump_card['name'],
                        ))
                    game.exchange_trump_jack(trump_jack)

                # The active player has chosen to close the stock.
                if close:
                    game.close_stock()

            sleep(SECONDS)
            # The active player chooses a card to play.
            couples = player.get_couples()

            # A human player chooses the first or the second card.
            if player.human:
                chosen_card = player.choose_card_human(
                    couples, game.trump_suit, trick, game.closed
                )
            # A computer player chooses the first card.
            elif not player.human and not trick:
                chosen_card = player.choose_card1_computer(
                    couples, game.trump_suit
                )
            # A computer player chooses the second card.
            elif not player.human and trick:
                chosen_card = player.choose_card2_computer(
                    game.trump_suit, trick, game.closed
                )

            # Check for a victory by marriage.
            if player.points >= 66:
                return

            # Display a message to show that the active player has
            # chosen a card to play.
            # Append that card to the current trick.
            card_tuple = (chosen_card, player.name)
            trick.append(card_tuple)
            if player.human:
                print(">", end=" ")
                print(_("You play the {}.").format(chosen_card['name']))
            else:
                print(">", end=" ")
                print(_("{} plays the {}.").format(
                    player.name,
                    chosen_card['name'],
                ))

        sleep(SECONDS)

        # One of the players takes the trick.
        if chosen_card:
            taker = game.decide_taker(trick, game.trump_suit)
            for player in players:
                if player.name == taker:
                    if player.human:
                        print()
                        print(_("You take this trick."))
                    else:
                        print()
                        print(_("{} takes this trick.").format(player.name))
                    player.add_trick_points(trick)

            # If the second player has taken the trick, switch turns.
            if taker == players[1].name:
                players.reverse()

            # Check for a victory by trick-taking.
            for player in players:
                if player.points >= 66:
                    return

            # Both players draw cards.
            sleep(SECONDS)
            for player in players:
                sleep(SECONDS)
                card = game.draw_from_stock()
                if card:
                    player.add_card(card)


def results(players):
    """Declare the winner, raise score, and show results."""
    if players[0].human:
        print(_("You WIN this round!"))
    else:
        print(_("{} WINS this round!").format(players[0].name))
    input(_("Press Enter to see the results. "))

    if players[1].points == 0:
        players[0].score += 3
    elif players[1].points < 33:
        players[0].score += 2
    else:
        players[0].score += 1

    print()
    print(_("POINTS"))
    player_points = sorted(players, key=lambda p: p.points, reverse=True)
    for player in player_points:
        print("{}: {}".format(player.name, player.points))

    print()
    print(_("TOTAL SCORE"))
    player_score = sorted(players, key=lambda p: p.score, reverse=True)
    for player in player_score:
        print("{}: {}".format(player.name, player.score))


def reset_attributes(players):
    """Reset players' attributes to prepare for the next round."""
    for player in players:
        player.points, player.marriage_points = 0, 0
        player.cards = []
        player.trump_jack = False
    return players


def main():
    """Call methods to play the game."""
    print("SCHNAPSEN\n")
    players = create_players()
    while True:
        game = start_new_game(players)
        game_loop(game, players)
        results(players)

        # Ask whether the player wants to start a new game.
        answer = ""
        while answer not in (_("y"), _("n")):
            print()
            prompt = _("Start a new game? (y/n) ")
            answer = input(prompt).strip().lower()
        if answer == _("y"):
            players = reset_attributes(players)
            print(_("Both players will keep their current score."))
        else:
            break


if __name__ == "__main__":
    main()
