import random

class Spel():

    def __init__(self, spelers, deler_idx):
        self.mogelijke_biedingen = [
            'Troel',
            'Troel mee',
            'Vraag',
            'Mee',
            'Miserie',
            'Abondance',
            'Solo Slim',
            'Pas',
        ]

        # Lijst van spelers in volgorde van spelen. Dus starten met speler na de deler
        self.spelers    = []
        for speler_idx in range(4):
            self.spelers.append(spelers[(deler_idx + speler_idx) % 4])

        self.deler_idx  = deler_idx
        self.deler      = self.spelers[deler_idx]
        self.troefkaart = None

    def delen(self, boek):

        # Voorbereidingr
        boek.aflangen()
        self.troefkaart = boek.laatste()
        print(f"Troefkaart: {str(self.troefkaart)}")
        print(f"Deler: {self.deler}")

        # Delen
        deel_aantallen = [4, 4, 5]
        random.shuffle(deel_aantallen)
        for aantal in deel_aantallen:
            for speler in self.spelers:
                for i in range(aantal):
                    speler.hand.give(boek.take_first(), sort=True)

        print("")
        print("Kontroleer troel")
        for speler in self.spelers:

            speler.post_delen(self.troefkaart)
            meegaan_kaart = speler.check_troel()
            if meegaan_kaart:
                print(f"{speler.naam}: {meegaan_kaart}")
                self.troefkaart = meegaan_kaart
            else:
                print(f"{speler.naam}: Pas troel")