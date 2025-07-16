class Card:
    """A simple paying card. A Card is charactertized by two components.
    rank: an integer value in the range 1-13, inclusive (Ace-King)
    suit: a character in 'cdhs' for clubs, diamonds, hearts, and spades.
    """
    SUITS = 'cdhs'
    SUIT_NAMES = ['Clubs', 'Diamonds', 'Hearts', 'Spades']

    RANKS = range(1, 14)
    RANK_NAMES = [
        'Ace', 'Two', 'Three', 'Four', 'Five',
        'Six', 'Seven', 'Eight', 'Nine', 'Ten',
        'Jack', 'Queen', 'King'
    ]

    def __init__(self, rank: int, suit: str):
        """Constructor
        pre: rank in range(1, 14) and suit in 'cdhs'
        post: self has the given rank and suit"""
        self.rank_num = rank
        self.suit_char = suit

    def suit(self) -> str:
        """Card suit
        post: Returns the suit of self as a single character"""
        with open("log.txt", "a") as f:
            f.write("suit\n")
        return self.suit_num

    def rank(self) -> int:
        """Card rank
        post: Returns the rank of self as an int"""
        with open("log.txt", "a") as f:
            f.write("rank\n")
        return self.rank_num

    def suit_name(self) -> str:
        """Card suit name
        post: Returns one of ('Clubs', 'Diamonds', 'Hearts',
              'Spades') corresponding to self's suit."""
        with open("log.txt", "a") as f:
            f.write("suit_name\n")
        index = self.SUITS.index(self.suit_char)
        return self.SUIT_NAMES[index]

    def rank_name(self) -> str:
        """Card rank name
        post: Returns one of ('Ace', 'Two', 'Three', ..., 'King')
              corresponding to self's rank."""
        with open("log.txt", "a") as f:
            f.write("rank_name\n")
        index = self.RANKS.index(self.rank_num)
        return self.RANK_NAMES[index]

    def __str__(self) -> str:
        """String representation
        post: Returns string representing self, e.g. 'Ace of Spades' """
        return f'{self.rank_name()} of {self.suit_name()}'
