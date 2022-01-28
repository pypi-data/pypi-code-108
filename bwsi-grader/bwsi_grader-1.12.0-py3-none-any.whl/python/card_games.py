import random

from bwsi_grader.errors import StudentError

__seed__ = ["cardclass", "deckclass"]


def grade_card(StudentCard):
    from hashlib import sha224

    from bwsi_grader.print import print_passed

    def card_repr(rank, suit):
        _rank_to_str = {11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}
        _suit_to_str = {"C": "Clubs", "H": "Hearts", "S": "Spades", "D": "Diamonds"}

        rank = _rank_to_str[rank] if rank in _rank_to_str else str(rank)
        return f"{rank} of {_suit_to_str[suit]}"

    # ensure that we can create a card
    try:
        c = StudentCard(4, "H")
    except (NameError, TypeError):
        raise StudentError('Could not create card `Card(4, "H")`')

    # ensure there is a rank and a suit, and that they are correctly set
    try:
        c.rank
    except AttributeError:
        raise StudentError(
            'Could not access the `rank` attribute after creating `Card(4, "H")`'
        )

    try:
        c.suit
    except AttributeError:
        raise StudentError(
            'Could not access the `suit` attribute after creating `Card(4, "H")`'
        )

    if not (c.rank == 4):
        raise StudentError(
            f'The `rank` attribute did not match. Created card with `Card(4, "H")`. Expected 4; got {c.rank}'
        )

    if not (c.suit == "H"):
        raise StudentError(
            f'The `suit`attribute did not match. Created card with `Card(4, "H")`. Expected "H"; got {c.suit}'
        )

    if not (str(c).lower() == card_repr(4, "H").lower()):
        raise StudentError(
            f'__repr__ did not match after being lower-cased; expected {card_repr(4, "H").lower()} got {str(c).lower()}'
        )

    try:
        c = StudentCard(13, "S")
    except (NameError, TypeError):
        raise StudentError('Could not create card `Card(13, "S")`')

    if not (c.rank == 13):
        raise StudentError(
            f'The `rank` attribute did not match. Created card with `Card(13, "S")`. Expected 13; got {c.rank}'
        )

    if not (c.suit == "S"):
        raise StudentError(
            f'The `suit`attribute did not match. Created card with `Card(13, "S")`. Expected "S"; got {c.suit}'
        )

    if not (str(c).lower() == card_repr(13, "S").lower()):
        raise StudentError(
            f'__repr__ did not match after being lower-cased; expected {card_repr(13, "S").lower()} got {str(c).lower()}'
        )

    for _ in range(100):
        rank1 = random.randint(2, 14)
        suit = ("C", "H", "S", "D")[random.randint(0, 3)]
        student_card1 = StudentCard(rank1, suit)
        c1 = card_repr(rank1, suit)
        assert (
            str(student_card1).lower() == c1.lower()
        ), f"__repr__ did not match after being lower-cased; expected {c1.lower()} got {str(student_card1).lower()}"

        rank2 = random.randint(2, 14)
        suit = ("C", "H", "S", "D")[random.randint(0, 3)]
        student_card2 = StudentCard(rank2, suit)
        c2 = card_repr(rank2, suit)
        if not (str(student_card2).lower() == c2.lower()):
            raise StudentError(
                f"__repr__ did not match after being lower-cased; expected {c2.lower()} got {str(student_card2).lower()}"
            )

        if not (student_card1 < student_card2) == (rank1 < rank2):
            raise StudentError(
                f"Testing {c1} < {c2}. Expected {rank1 < rank2}; got {student_card1 < student_card2}"
            )

        if not (student_card1 > student_card2) == (rank1 > rank2):
            raise StudentError(
                f"Testing {c1} > {c2}. Expected {rank1 > rank2}; got {student_card1 > student_card2}"
            )

        if not (student_card1 == student_card2) == (rank1 == rank2):
            raise StudentError(
                f"Testing {c1} == {c2}. Expected {rank1 == rank2}; got {student_card1 == student_card2}"
            )

        if not (student_card1 <= student_card2) == (rank1 <= rank2):
            raise StudentError(
                f"Testing {c1} <= {c2}. Expected {rank1 <= rank2}; got {student_card1 <= student_card2}"
            )

        if not (student_card1 >= student_card2) == (rank1 >= rank2):
            raise StudentError(
                f"Testing {c1} >= {c2}. Expected {rank1 >= rank2}; got {student_card1 >= student_card2}"
            )

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())


def grade_deck(StudentDeck):
    import random
    from hashlib import sha224

    from bwsi_grader.print import print_passed

    # ensure that we can create a deck
    try:
        deck = StudentDeck()
    except NameError:
        raise StudentError(
            "Could not create deck by calling `Deck()`. Does `shuffled` have a default value?"
        )

    # ensure we can create a deck with a shuffled parameter
    try:
        deck = StudentDeck(True)
    except (NameError, TypeError):
        raise StudentError(
            "Could not create deck with shuffled=True by calling `Deck(True)`"
        )

    # ensure that a deck has a shuffled parameter
    try:
        deck.shuffled
    except AttributeError:
        raise StudentError("Could not access the shuffled attribute: `Deck().shuffled`")

    # ensure that a shuffle function exists
    try:
        deck.shuffle()
    except AttributeError:
        raise StudentError("Could not call `Deck().shuffle()`")

    # ensure that a deal_card function exists
    try:
        deck.deal_card()
    except AttributeError:
        raise StudentError("Could not call `Deck().deal_card()`")

    # ensure that a reset function exists
    try:
        deck.reset()
    except AttributeError:
        raise StudentError("Could not call `Deck().reset()`")

    # make sure the repr matches
    deck = str(StudentDeck()).lower()
    assert (
        deck == "deck(dealt 0, shuffled=false)"
    ), f'__repr__ did not match; expected "deck(dealt 0, shuffled=False)" got {deck}'

    # make sure the deck deals cards
    deck = StudentDeck()
    card = deck.deal_card()

    try:
        card.rank
        card.suit
    except AttributeError:
        raise StudentError(
            f"The Deck should deal Card-instances. Dealt an object of type: {type(card)}"
            f"\nTo reproduce this error, call:"
            f"\ndeck = Deck()"
            f"\ncard = deck.deal_card()"
            f"\ncard.rank"
            f"\ncard.suit"
        )

    # make sure the deck has 52 cards
    deck = StudentDeck()
    try:
        for _ in range(52):
            card = deck.deal_card()
            card.rank
            card.suit
    except Exception as e:
        raise StudentError(
            f"Trying to deal 52 cards produced the following error:"
            f"\n\t{type(e).__name__}:{e}"
        )

    try:
        # make sure that dealing past the end of the deck returns None
        card = deck.deal_card()
        assert (
            card is None
        ), f"Expected dealing more than 52 cards to return None but returned {card}"
    except Exception as e:
        raise StudentError(
            f"Expected dealing more than 52 cards to return None."
            f"\nTrying to deal 53 cards produced the following error:"
            f"\n\t{type(e).__name__}:{e}"
        )

    # make sure the counter stayed at 52
    assert (
        str(deck).lower() == "deck(dealt 52, shuffled=false)"
    ), f"Dealing more than 52 cards incremented the counter past 52; got {str(deck).lower()}"

    # make sure the deck has all four suits
    deck.reset()
    suits = set()
    for _ in range(52):
        suits.add(deck.deal_card().suit.upper())
    assert all(
        suit in suits for suit in ("C", "H", "S", "D")
    ), f"Expected all four suits (C, H, S, D) but found {suits}"

    # make sure that dealing cards updates the counter
    deck = StudentDeck()
    deal_amt = random.randint(1, 52)
    [deck.deal_card() for _ in range(deal_amt)]
    if str(deck).lower() != f"deck(dealt {deal_amt}, shuffled=false)":
        raise StudentError(
            f'`deal_card()` did not update the __repr__ correctly; expected "deck(dealt {deal_amt}, shuffled=False)" got {str(deck).lower()}'
        )

    # make sure reset resets the counter
    deck.reset()
    if str(deck).lower() != f"deck(dealt 0, shuffled=false)":
        raise StudentError(
            f'`reset()` did not reset the counter correctly; expected "deck(dealt 0, shuffled=false)" from the __repr__; got {str(deck).lower()}'
        )

    # make sure the ranks of all 52 cards in the right order
    deck.reset()
    expected_ranks = list(range(2, 15)) * 4
    actual_ranks = [deck.deal_card().rank for _ in range(52)]
    if actual_ranks != expected_ranks:
        raise StudentError(
            f"Expected unshuffled deck to be in the order:\n\t{expected_ranks}\nbut got:\n\t{actual_ranks}"
        )

    # make sure the suits of all 52 cards are correct
    deck.reset()
    suits = [deck.deal_card().suit for _ in range(52)]
    same_as_next = [suits[i] == suits[i + 1] for i in range(51)]
    expected = [True] * 12 + [False]
    expected *= 4
    expected = expected[:-1]
    if same_as_next != expected:
        raise StudentError(
            f"Expected the suits of an unshuffled deck to grouped together but they were not. Suits are:\n\t{suits}"
        )

    # make sure shuffling does something
    ordered_ranks = list(range(2, 15)) * 4
    ordered_suits = [True] * 12 + [False]
    ordered_suits *= 4
    ordered_suits = ordered_suits[:-1]
    deck_in_order = []
    for _ in range(10):
        deck.reset()
        deck.shuffle()
        _cards = [deck.deal_card() for _ in range(52)]
        _suits = [c.suit for c in _cards]
        actual_ranks = [c.rank for c in _cards]
        actual_suits = [_suits[i] == _suits[i + 1] for i in range(51)]
        deck_in_order.append(
            actual_ranks == ordered_ranks and actual_suits == ordered_suits
        )

    if all(deck_in_order):
        raise StudentError(
            "Calling `deck.shuffle()` is expected to change the order of cards but did not"
        )

    # make sure resetting puts the cards back in order
    deck.reset()
    actual_ranks = [deck.deal_card().rank for _ in range(52)]
    actual_suits = [suits[i] == suits[i + 1] for i in range(51)]
    
    if not (actual_ranks == ordered_ranks and actual_suits == ordered_suits):
        raise StudentError(
            "`reset()` should put the deck back in order but it was still shuffled"
        )

    # check that Deck(True) actually shuffles the deck
    deck_in_order = []
    for _ in range(10):
        deck = StudentDeck(True)
        _cards = [deck.deal_card() for _ in range(52)]
        _suits = [c.suit for c in _cards]
        actual_ranks = [c.rank for c in _cards]
        actual_suits = [_suits[i] == _suits[i + 1] for i in range(51)]
        deck_in_order.append(
            actual_ranks == ordered_ranks and actual_suits == ordered_suits
        )

    if all(deck_in_order):
        raise StudentError(
            "Calling `Deck(True)` is expected to produce a shuffled deck of cards"
        )

    print_passed(sha224(str.encode(__seed__[1])).hexdigest())
