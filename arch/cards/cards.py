from dataclasses import dataclass
from typing import List, Tuple
from colorama import Fore, Style

from .suits import Suit, suit_symbol
from .ranks import Rank, ranks, rank_symbol


@dataclass(order=True, frozen=True)
class Card:
    suit: Suit
    rank: Rank

    @property
    def name(self):
        if self == Card.joker:
            return "joker"
        else:
            return f"{self.rank}-{self.suit}"

    @property
    def symbol(self):
        return card_symbol_txt[self]

    def __str__(self):
        return suit_symbol[self.suit] + rank_symbol[self.rank]

Card.unknown = Card(Suit.Unknown, Rank.Unknown)
Card.joker = Card(Suit.Unknown, Rank.Joker)


card_symbol = {
    Card.unknown: "🂠",
    Card.joker: "🃏",
}

card_symbol_unicode = {
    Suit.Heart:   "🂱 🂲 🂳 🂴 🂵 🂶 🂷 🂸 🂹 🂺 🂻 🂽 🂾",
    Suit.Spade:   "🂡 🂢 🂣 🂤 🂥 🂦 🂧 🂨 🂩 🂪 🂫 🂭 🂮",
    Suit.Diamond: "🃁 🃂 🃃 🃄 🃅 🃆 🃇 🃈 🃉 🃊 🃋 🃍 🃎",
    Suit.Club:    "🃑 🃒 🃓 🃔 🃕 🃖 🃗 🃘 🃙 🃚 🃛 🃝 🃞",
}
card_symbol_txt = {}

for suit, line in card_symbol_unicode.items():
    symbols = line.split(" ")
    for rank, symbol in zip(ranks, symbols):
        card = Card(suit, rank)
        card_symbol[card] = symbol

        if card.suit in [Suit.Heart, Suit.Diamond]:
            kleur = Fore.RED
        else:
            kleur = Fore.BLACK
        filler = ''
        if card.rank != Rank.Ten:
            filler = ' '
        card_symbol_txt[card] = f"{Style.BRIGHT}{kleur}[{suit_symbol[card.suit]}{rank_symbol[card.rank]}]{filler}{Style.RESET_ALL}"
        #card_symbol_txt[card] = suit_symbol[card.suit] + rank_symbol[card.rank]