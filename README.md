# Wiezen - Belgisch Kaartspel

Een Flask web applicatie om het Belgische kaartspel Wiezen te spelen tegen 3 computer tegenstanders.

## Kenmerken

- **Visueel aantrekkelijke interface**: Moderne dark theme met custom SVG kaarten
- **4 spelers**: Menselijke speler onderaan, 3 AI tegenstanders (links, boven, rechts)
- **AI moeilijkheidsniveaus**: Kies tussen makkelijk, gemiddeld, en moeilijk voor elke AI speler
- **Debug modus**: Toon alle kaarten van tegenstanders voor debugging doeleinden
- **Volledige spelregels**: Bieden (Vraag, Mee, Solo Slim, Miserie, etc.), slagen spelen, en score bijhouden
- **Partnerschap Badges**: Duidelijke visualisatie van wie met wie speelt tijdens een ronde
- **Resilient Game Loop**: Automatisch herstel bij verbindingsproblemen of verbreken van de verbinding (bijv. na sleep mode).
- **Slimme Sortering**: Kaarten in de hand worden nu gesorteerd met interleaved kleuren (Rood-Zwart-Rood-Zwart) voor betere leesbaarheid.
- **Verbindingsindicator**: Visuele feedback via een status indicator als de server onbereikbaar is.
- **Statistieken Dashboard**: Uitgebreid overzicht van gewonnen spellen, contract frequenties en speler ranglijsten.
- **Geluidseffecten**: Subtiele geluiden voor delen, kaarten spelen en slagen winnen (gegenereerd via Web Audio API, geen externe bestanden nodig).

## Technologie Stack

- **Backend**: Python 3, Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js (voor statistieken)
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
   - **Moeilijk**: Geavanceerde strategie met kaarten tellen (onthoudt hoge kaarten) en void tracking (exploiteert kleuren waar tegenstanders vrij van zijn).
4. Optioneel: Activeer debug modus om alle kaarten te zien
5. Klik op "Start Spel"
6. **Statistieken**: Klik op "Bekijk Statistieken" op de homepagina om je prestaties te zien.

### Spelen

1. **Bieden**: Klik op je gewenste bod in de overzichtelijke 2-rijen layout. De interface blokkeert automatisch biedingen die lager zijn dan het huidige maximum.
2. **Kaarten spelen**: Klik op een kaart in je hand om te spelen met vloeiende animaties.
3. **Slagen**: Na 4 kaarten wordt de slag automatisch bepaald.
4. **Score**: Scores worden bijgehouden en getoond bij elke speler.
5. **Miserie**: Bij een Miserie bod stopt het spel onmiddellijk zodra de bieder een slag haalt.
6. **Herstel**: Als het spel vastloopt (bijv. AI zet niet door), herstelt de loop zich automatisch na een korte timeout.

### Debug Modus

Klik op de "Debug Aan/Uit" knop tijdens het spel om de kaarten van tegenstanders te tonen of te verbergen.

## Spelregels (Uitgebreid)

### Delen
- 52 kaarten worden gedeeld (13 per speler).
- De troefkaart blijft het hele spel zichtbaar.
- Bij **Abondance** mag de bieder de troefkleur kiezen, waarna de zichtbare troefkaart wordt aangepast.
- **Troel**: Als een speler 3 Azen heeft, wordt dit automatisch herkend. De speler met de 4e Aas wordt de partner en MOET de eerste slag leiden met die Aas.

### Bieden (Hiërarchie)
De biedingen volgen een strikte rangorde:
1. **Vraag / Mee / Alleen** (Niveau 1)
2. **Abondance** (Niveau 2)
3. **Miserie** (Niveau 3)
4. **Open Miserie** (Niveau 4)
5. **Solo Slim** (Niveau 5)

**Regels**:
- Je mag nooit lager bieden dan het huidige maximum.
- Bij biedingen van hetzelfde niveau (Niveau 2-5) behoudt de eerste bieder het contract; je moet strikt hoger bieden om het over te nemen.
- **Alleen** kan een lone **Vraag** overnemen op Niveau 1.

### Spelen
- Volg kleur als je kan.
- Hoogste kaart van de uitgekomen kleur wint (tenzij troef gespeeld wordt).
- Troef kaarten winnen altijd van niet-troef kaarten.

## Geavanceerde AI Logica

De AI op het "Moeilijk" niveau gebruikt de volgende technieken:
- **Kaarten Tellen**: De AI onthoudt welke Azen en Heren zijn gespeeld om te weten of hun eigen kaarten nu "meesters" zijn.
- **Void Tracking**: Identificeert welke suits tegenstanders niet meer hebben. De AI kan deze kleuren trekken om tegenstanders te dwingen hun troeven te gebruiken.
- **Partnerschap Logica**: De AI herkent teamgenoten en speelt defensief/ondersteunend (bijv. laag spelen als de partner de slag al wint).
- **Miserie Verdediging**: De AI speelt slim tegen Miserie door hoge kaarten weg te gooien als de Miserie-speler in een slag al "veilig" (laag) heeft gespeeld.
- **Biedingsbewustzijn**: De AI volgt de strikte hiërarchie en zal niet proberen ongeldige biedingen te doen.

## Ontwikkeling

### Testen
Er zijn unit tests beschikbaar voor de kernfunctionaliteiten:
```bash
pytest tests/
```

## Toekomstige Uitbreidingen

- Multiplayer ondersteuning

## Licentie

Persoonlijk project voor educatieve doeleinden.
