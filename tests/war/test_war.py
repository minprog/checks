from war import Card, Deck, DrawPile

def test_card_description():
    card = Card('Hearts', 'A')
    assert card.description() == 'A of Hearts'

def test_card_get_value():
    card = Card('Spades', 'K')
    assert card.get_value() == 13

def test_deck_deal():
    values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    
    all_combinations: list[tuple[str, str]] = []
    for suit in suits:
        for value in values:
            all_combinations.append((suit, value))
    
    # assert that all 52 cards are dealt
    deck = Deck()
    for _ in range(52):
        dealt_card = deck.deal()

        combination = (dealt_card.suit, dealt_card.value)
        assert combination in all_combinations
        all_combinations.remove(combination)

def test_deck_split():
    deck = Deck()
    pile1, pile2 = deck.split_deck()
    assert pile1.count_cards() == 26
    assert pile2.count_cards() == 26
    assert deck.deal() == None

def test_draw_pile_count_cards():
    draw_pile = DrawPile()
    assert draw_pile.count_cards() == 0

    card = Card('Spades', 'Q')
    draw_pile.add_card(card)
    assert draw_pile.count_cards() == 1

def test_draw_pile_add_card():
    card = Card('Hearts', '9')
    draw_pile = DrawPile()
    draw_pile.add_card(card)
    assert draw_pile.count_cards() == 1

def test_draw_pile_draw_card():
    card1 = Card('Diamonds', '7')
    card2 = Card('Clubs', '8')
    
    draw_pile = DrawPile()
    draw_pile.add_card(card1)
    draw_pile.add_card(card2)
    
    drawn_card = draw_pile.draw_card()
    assert drawn_card == card1
    assert draw_pile.count_cards() == 1
    
    drawn_card = draw_pile.draw_card()
    assert drawn_card == card2
    assert draw_pile.count_cards() == 0
