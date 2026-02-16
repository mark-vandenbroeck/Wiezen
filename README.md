# Wiezen - Belgisch Kaartspel

Een Flask web applicatie om het Belgische kaartspel Wiezen te spelen tegen 3 computer tegenstanders.

## Kenmerken

- **Visueel aantrekkelijke interface**: Moderne dark theme met custom SVG kaarten
- **4 spelers**: Menselijke speler onderaan, 3 AI tegenstanders (links, boven, rechts)
- **AI moeilijkheidsniveaus**: Kies tussen makkelijk, gemiddeld, en moeilijk voor elke AI speler
- **Debug modus**: Toon alle kaarten van tegenstanders voor debugging doeleinden
- **Volledige spelregels**: Bieden (Vraag, Mee, Solo Slim, Miserie, etc.), slagen spelen, en score bijhouden
- **Partnerschap Badges**: Duidelijke visualisatie van wie met wie speelt tijdens een ronde
- **Database persistentie**: Spellen worden opgeslagen in SQLite

## Technologie Stack

- **Backend**: Python 3, Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Kaarten**: Custom SVG generatie

## Installatie

1. **Clone de repository** (of navigeer naar de directory):
   ```bash
   cd /Users/mark/Documents/Python/Wiezen
   ```

2. **Installeer dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start de applicatie**:
   ```bash
   python app.py
   ```

4. **Open in browser**:
   ```
   http://localhost:5005
   ```

## Gebruik

### Nieuw Spel Starten

1. Open de home page
2. Vul je naam in
3. Kies moeilijkheidsniveaus voor de 3 AI spelers:
   - **Makkelijk**: Simpele random-achtige beslissingen
   - **Gemiddeld**: Redelijke strategie met basis regels
   - **Moeilijk**: Geavanceerde strategie met kaart analyse
4. Optioneel: Activeer debug modus om alle kaarten te zien
5. Klik op "Start Spel"

### Spelen

1. **Bieden**: Klik op je gewenste bod in de overzichtelijke 2-rijen layout.
2. **Kaarten spelen**: Klik op een kaart in je hand om te spelen.
3. **Slagen**: Na 4 kaarten wordt de slag automatisch bepaald.
4. **Score**: Scores worden bijgehouden en getoond bij elke speler.
5. **Miserie**: Bij een Miserie bod stopt het spel onmiddellijk zodra de bieder een slag haalt.

### Debug Modus

Klik op de "Debug Aan/Uit" knop tijdens het spel om de kaarten van tegenstanders te tonen of te verbergen.

## Spelregels (Uitgebreid)

### Delen
- 52 kaarten worden gedeeld (13 per speler).
- De troefkaart blijft het hele spel zichtbaar.
- Bij **Abondance** mag de bieder de troefkleur kiezen, waarna de zichtbare troefkaart wordt aangepast.

### Bieden
- **Vraag**: Zoek een partner om samen 8+ slagen te winnen.
- **Mee**: Accepteer een Vraag bod.
- **Solo**: Alleen 5+ slagen winnen.
- **Abondance**: Alleen 9+ slagen winnen. De bieder kiest de troef.
- **Solo Slim**: Alle 13 slagen winnen.
- **Miserie**: Geen enkele slag halen. Het spel stopt zodra de bieder een slag haalt.
- **Open Miserie**: Geen enkele slag halen met open kaarten (16 punten).
- **Pas**: Niet bieden.

### Spelen
- Volg kleur als je kan.
- Hoogste kaart van de uitgekomen kleur wint (tenzij troef gespeeld wordt).
- Troef kaarten winnen altijd van niet-troef kaarten.

## Project Structuur

```
Wiezen/
├── app.py                 # Hoofdapplicatie met routes
├── models.py              # Database modellen
├── game_engine.py         # Spel logica orchestratie
├── ai_player.py           # AI speler strategieën
├── card_svg.py            # SVG kaart generatie
├── config.py              # Configuratie
├── requirements.txt       # Python dependencies
├── wiezen.db             # SQLite database (wordt aangemaakt)
├── templates/
│   ├── base.html         # Basis template
│   ├── index.html        # Home pagina
│   └── game.html         # Spel interface
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       ├── cards.js      # Kaart rendering
│       └── game.js       # Spel logica
└── arch/                 # Bestaande game logica
    ├── cards/
    ├── game/
    └── users/
```

## Ontwikkeling

### Database Reset

Om de database te resetten:
```bash
rm wiezen.db
python app.py  # Database wordt opnieuw aangemaakt
```

### Debug Modus Activeren via Environment

```bash
export DEBUG_MODE=true
python app.py
```

## Toekomstige Uitbreidingen

- Geavanceerdere AI voor Abondance en Solo Slim
- Spel geschiedenis en statistieken
- Multiplayer ondersteuning
- Animaties verbeteren
- Geluid effecten

## Licentie

Persoonlijk project voor educatieve doeleinden.
