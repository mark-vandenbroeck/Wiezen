from cards import Card
from cards import Deck
from cards import Suit, suits
from users.player import Player
from game.spel import Spel
import random

boek = Deck.full_deck()
boek.shuffle()
# print(boek)

# Maak spelers aan
spelers = []
spelersnamen = [
    'Jan',
    'Piet',
    'Joris',
    'Korneel'
]
maxlen = max(len(x) for x in spelersnamen)

for naam in spelersnamen:
    spelers.append(Player(naam))

# Initieel delen om kaarten te steken
deel_aantallen = [4, 4, 5]
random.shuffle(deel_aantallen)
for aantal in deel_aantallen:
    for speler in spelers:
        for i in range(aantal):
            speler.hand.give(boek.take_first(), sort=True)

for speler in spelers:
    for i in range(13):
        boek.give(speler.hand.take_first())

# Speel
deler = 0
spel = Spel(spelers, deler)
spel.delen(boek)

for speler in spelers:
    fillersize = maxlen - len(speler.naam)
    print(f"{speler}{' '*fillersize}: {speler.hand}  Aantal azen: {speler.aantal_azen}  Aantal troeven: {speler.aantal_troef}")

dummy = 1