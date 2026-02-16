from cards.deck import Deck
from cards.ranks import Rank, ranks, rank_symbol
from cards.suits import Suit, suits
from cards import Card

class Player():

    def __init__(self, naam):
        self.naam = naam
        self.hand = Deck.empty()
        self.troefkaart = None
        self.aantal_azen = 0
        self.aantal_troef = 0

#-----------------------------------------------------------------------------------------------------------------------

    def post_delen(self, troefkaart):
        self.troefkaart   = troefkaart
        self.aantal_azen  = self.hand.aantal_waarde(Rank.Ace)
        self.aantal_troef = self.hand.aantal_soort(troefkaart.suit)

# -----------------------------------------------------------------------------------------------------------------------

    def check_troel(self):
        if self.aantal_azen < 3:
            return None

        # Zoek ontbrekende aas
        if self.aantal_azen == 3:
            soorten = suits
            for soort in suits:
                if Card(soort, Rank.Ace) in self.hand:
                    soorten.remove(soort)
            return Card(soorten[0], Rank.Ace)

        # Speler heeft alle azen, we zoeken wie de hoogste harten heeft
        # TODO

# -----------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.naam