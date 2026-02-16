from arch.util import OrderedEnum, auto


class Suit(OrderedEnum):
    Unknown = auto()
    Spade   = auto()
    Diamond = auto()
    Club    = auto()
    Heart   = auto()

    @property
    def name(self):
        return suit_name[self]

    @property
    def symbol(self):
        return suit_symbol[self]


suit_name = {
    Suit.Unknown: "unknown",
    Suit.Club:    "Klaveren",
    Suit.Diamond: "Ruiten",
    Suit.Heart:   "Harten",
    Suit.Spade:   "Schuppen",
}

suit_symbol = {
    Suit.Unknown: "_",
    Suit.Club: "♣",
    Suit.Diamond: "♦",
    Suit.Heart: "♥",
    Suit.Spade: "♠",
}

suits = (
    Suit.Club,
    Suit.Diamond,
    Suit.Heart,
    Suit.Spade,
)