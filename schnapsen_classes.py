"""Classes for a game of Schnapsen."""

import random
from collections import defaultdict

SUITS = ("Clubs", "Diamonds", "Hearts", "Spades")


class SchnapsenPlayer():
    """A class to represent a player of Schnapsen."""

    def __init__(self, name, human=False):
        """Initialize attributes."""
        self.name = name
        self.human = human
        self.cards = []
        self.points, self.marriage_points = 0, 0
        self.score = 0

    def __repr__(self):
        return f"{self.name} is a player of Schnapsen."

    def add_card(self, card):
        """Add a card to the player's hand."""
        self.cards.append(card)
        if self.human:
            print(f"You have a new card: {card['name']}")
        else:
            print(f"{self.name} has a new card.")

    def get_couples(self):
        """Return a dictionary of matching kings and queens."""
        kings_queens = defaultdict(list)
        for card in self.cards:
            if card["rank"] in ("King", "Queen"):
                suit = card["suit"]
                kings_queens[suit].append(card)
        return {k: v for (k, v) in kings_queens.items() if len(v) == 2}

    def choose_card_human(self, couples, trump_suit, trick, closed):
        """Let a human player choose a card, and return it."""
        # Sort cards to show them in order.
        self.cards.sort(
            key=lambda card: (card["suit"], card["points"]), reverse=True
        )

        # Show enumerated cards.
        print()
        for number, card in enumerate(self.cards, 1):
            if card["suit"] == trump_suit:
                print(f"{counter} - {card['name']}*")
            else:
                print(f"{counter} - {card['name']}")
        # Show the "marry" option.
        if couples and not trick:
            print("M - Marry a couple")

        while True:
            print()
            if trick and closed:
                print("You have to match suit and take the trick if you can.")
            user_input = input("Your choice: ").strip()
            if (
                    user_input.isdigit() and
                    int(user_input) in range(1, len(self.cards)+1)
            ):
                index = int(user_input) - 1
                chosen_card = self.cards[index]
                break

            # The active player chooses a card from the matching
            # couples to play.
            elif user_input.upper() == "M" and couples and not trick:
                couple_cards = []
                for suit in couples:
                    couple_cards.extend(couples[suit])

                print()
                for counter, card in enumerate(couple_cards, 1):
                    if card["suit"] == trump_suit:
                        print(f"{counter} - {card['name']}*")
                    else:
                        print(f"{counter} - {card['name']}")
                user_input = ""
                while (
                        not user_input.isdigit() or
                        int(user_input) not in range(1, len(couple_cards)+1)
                ):
                    user_input = input("\nChoose a card: ").strip()
                index = int(user_input) - 1
                chosen_card = couple_cards[index]
                self.marry(chosen_card, trump_suit)
                break

            else:
                print("Please choose one of the options above.")

        # Remove the chosen card from the player's hand and return it.
        self.cards.remove(chosen_card)
        return chosen_card

    def choose_card1_computer(self, couples, trump_suit):
        """Choose the computer's first card in this trick."""
        if couples:
            # If you have the trump couple, marry it. Otherwise,
            # marry the couple of a random suit in the list.
            if trump_suit in couples:
                chosen_card = random.choice(couples[trump_suit])
                self.marry(chosen_card, trump_suit)
            else:
                suit = random.choice(list(couples))
                chosen_card = random.choice(couples[suit])
                self.marry(chosen_card, trump_suit)
        # If you have no couples, play your first card.
        else:
            chosen_card = self.cards[0]

        # Remove the chosen card from the player's hand and return it.
        self.cards.remove(chosen_card)
        return chosen_card

    def choose_card2_computer(self, trump_suit, trick, closed):
        """Choose the computer's second card in this trick."""
        opponent_card = trick[0][0]

        higher_suit_cards, lower_suit_cards = [], []
        trump_cards = []

        for card in self.cards:
            if (
                    card["suit"] == opponent_card["suit"] and
                    card["points"] > opponent_card["points"]
                ):
                higher_suit_cards.append(card)
            elif (
                    card["suit"] == opponent_card["suit"] and
                    card["points"] < opponent_card["points"]
                ):
                lower_suit_cards.append(card)
            elif (
                    card["suit"] == trump_suit and
                    opponent_card["suit"] != trump_suit
                ):
                trump_cards.append(card)

        # Never choose a card with a higher value than required.
        if higher_suit_cards:
            higher_suit_cards.sort(key=lambda d: d["points"])
            chosen_card = higher_suit_cards[0]
        # If the stock is closed, you have to match the suit.
        elif closed and lower_suit_cards:
            lower_suit_cards.sort(key=lambda d: d["points"])
            chosen_card = lower_suit_cards[0]
        elif trump_cards:
            trump_cards.sort(key=lambda d: d["points"])
            chosen_card = trump_cards[0]
        # If none of the above is true, choose your lowest card,
        # but not a trump card.
        else:
            no_trumps = [c for c in self.cards if c["suit"] != trump_suit]
            no_trumps.sort(key=lambda d: d["points"])
            chosen_card = no_trumps[0]

        # Remove the chosen card from the player's hand and return it.
        self.cards.remove(chosen_card)
        return chosen_card

    def add_trick_points(self, trick):
        """Count and add the points of a taken trick."""
        for card_tuple in trick:
            card = card_tuple[0]
            self.points += card["points"]
        # Add points from a previous marriage.
        if self.marriage_points:
            self.points += self.marriage_points
            self.marriage_points = 0
            print("Marriage points added.")

        # Show the player's current points.
        if self.human:
            print("Your", end=" ")
        else:
            print(f"{self.name}'s", end=" ")
        print(f"points: {self.points} / 66")

    def choose_action_human(self, trump_suit, trump_card):
        """Let a human player choose an action.

        The player may exchange the trump Jack and/or close the stock.
        """
        exchange, close = False, False
        choices = ["Close the stock"]
        for card in self.cards:
            if card["rank"] == "Jack" and card["suit"] == trump_suit:
                exchange_choice = f"Exchange your {card['name']} " \
                f"for the {trump_card['name']}"
                choices.append(exchange_choice)
                break

        while True:
            if choices:
                print("\nYou will play the first card.", end=" ")
                print("Do you want to perform an action?\n")
                for counter, choice in enumerate(choices, 1):
                    print(f"{counter} - {choice}")
                prompt = "\nChoose an action or press Enter: "
                user_input = input(prompt).strip()
            else:
                break
            if user_input:
                if user_input == "1":
                    close = True
                    break
                elif user_input == "2" and len(choices) > 1:
                    exchange = True
                    choices.pop(1)
                else:
                    print("Please choose one of the options above", end=" ")
                    print("or press Enter.")
            else:
                break

        return exchange, close

    def choose_action_computer(self, trump_suit):
        """Exchange a computer player's trump card, if possible."""
        exchange, close = False, False
        for card in self.cards:
            if card["rank"] == "Jack" and card["suit"] == trump_suit:
                exchange = True
                break
        return exchange, close

    def marry(self, card, trump_suit):
        """Marry a king and a queen."""
        if card["suit"] == trump_suit:
            points = 40
        else:
            points = 20

        # Marriage points are only counted after the player has taken
        # at least one trick.
        if self.human:
            print("X You marry the couple of", end=" ")
        else:
            print(f"X {self.name} marries the couple of", end=" ")
        print(f"{card['suit']} ({points} points).")

        if self.points:
            self.points += points
        else:
            self.marriage_points += points
            print("Points will be added after the first taken trick.")

    def pop_trump_jack(self, trump_suit):
        """Remove the trump Jack from the player's cards. Return it."""
        for card in self.cards:
            if card["rank"] == "Jack" and card["suit"] == trump_suit:
                trump_jack = card
                break
        self.cards.remove(trump_jack)
        return trump_jack


class SchnapsenGame():
    """A class to represent a game of Schnapsen."""

    def __init__(self):
        """Initialize attributes."""
        self.stock = []
        self.trump_card, self.trump_suit = None, None
        self.closed = False

    def __repr__(self):
        return "Schnapsen is a text-based card game for two players."

    def create_cards(self):
        """Create the cards."""
        ranks_points = (
            ("Jack", 2),
            ("Queen", 3),
            ("King", 4),
            ("Ten", 10),
            ("Ace", 11)
        )

        for suit in SUITS:
            for rank, points in ranks_points:
                name = f"[{rank} of {suit}]"
                card = {
                    "name": name,
                    "suit": suit,
                    "rank": rank,
                    "points": points
                }
                self.stock.append(card)

    def shuffle_cards(self):
        """Shuffle the cards."""
        random.shuffle(self.stock)
        self.trump_card = self.stock[0]
        self.trump_suit = self.trump_card["suit"]
        print("Cards are shuffled.", end=" ")
        print(f"Trump card: {self.trump_card['name']}\n")

    @staticmethod
    def decide_taker(trick, trump_suit):
        """Decide who takes the trick."""
        (card1, player1), (card2, player2) = trick
        if card1["suit"] == card2["suit"]:
            # Both cards have the same suit.
            # The player with the higher card takes the trick.
            trick.sort(key=lambda t: t[0]["points"])
            card_tuple = trick[-1]
            taker = card_tuple[1]
        else:
            # Cards have different suites.
            # If player2 chose a trump suit card, he takes the trick.
            if card2["suit"] == trump_suit:
                taker = player2
            else:
                taker = player1
        return taker

    def draw_from_stock(self):
        """Draw a new card from the stock."""
        if not self.closed:
            card = self.stock.pop()
            if len(self.stock) == 2:
                print("\nThere are only two more cards in the stock.\n")
            elif not self.stock:
                print(
                    "\nThe last card has been drawn!\n"
                    "From now on, players must match suits "
                    "and take tricks if they can.\n"
                )
                self.closed = True
            return card
        else:
            return None

    def close_stock(self):
        """Close the stock."""
        self.closed = True
        print(
            "The stock is closed. "
            "Players cannot draw cards anymore."
        )
        print(
            "From now on, players must match suits "
            "and take tricks if they can."
        )

    def exchange_trump_jack(self, trump_jack):
        """Exchange a trump Jack for the trump card."""
        self.stock[0] = trump_jack
        self.trump_card = trump_jack
        print(f"New trump card: {self.trump_card['name']}")


if __name__ == "__main__":
    print("This module is meant to be imported by the main module.")
