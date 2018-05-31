"""A game of Schnapsen.

https://en.wikipedia.org/wiki/Sixty-six_(card_game)#Schnapsen
"""

from time import sleep

from schnapsen_classes import SchnapsenPlayer, SchnapsenGame


PLAYER_NAMES = ("Human", "Computer")

# Change this number to make the game run slower or faster.
SECONDS = 1.5


def create_players():
    """Create the players."""
    player1 = SchnapsenPlayer(PLAYER_NAMES[0], human=True)
    player2 = SchnapsenPlayer(PLAYER_NAMES[1])
    players = [player1, player2]
    print(f"Welcome, {player1.name} and {player2.name}!", end=" ")
    print(f"{player1.name}, you will begin.")
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
                print("\nWe've run out of cards.")
                print("The player who took the last trick wins.")
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
                        print(f"\n< You take the {game.trump_card['name']}.")
                    else:
                        print(f"\n< {player.name} takes the", end=" ")
                        print(f"{game.trump_card['name']}.")
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
                print(f"> You play the {chosen_card['name']}.")
            else:
                print(f"> {player.name} plays the", end=" ")
                print(f"{chosen_card['name']}.")

        sleep(SECONDS)

        # One of the players takes the trick.
        if chosen_card:
            taker = game.decide_taker(trick, game.trump_suit)
            for player in players:
                if player.name == taker:
                    if player.human:
                        print("\nYou take this trick.")
                    else:
                        print(f"\n{player.name} takes this trick.")
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
        print("You WIN this round!")
    else:
        print(f"{players[0].name} WINS this round!")
    input("Press Enter to see the results. ")

    if players[1].points == 0:
        players[0].score += 3
    elif players[1].points < 33:
        players[0].score += 2
    else:
        players[0].score += 1

    print("\nPOINTS")
    player_points = sorted(players, key=lambda p: p.points, reverse=True)
    for player in player_points:
        print(f"{player.name}: {player.points}")

    print("\nTOTAL SCORE")
    player_score = sorted(players, key=lambda p: p.score, reverse=True)
    for player in player_score:
        print(f"{player.name}: {player.score}")


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
        while answer not in ("y", "n"):
            answer = input("\nStart a new game? (y/n) ").strip().lower()
        if answer == "y":
            players = reset_attributes(players)
            print("Both players will keep their current score.")
        else:
            break


if __name__ == "__main__":
    main()
