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

## Strategie en AI Logica

Het spel bevat drie AI niveaus, waarbij het "Moeilijk" (Hard) niveau gebruik maakt van geavanceerde technieken en simulaties.

### Biedstrategie (Hard AI)
De AI bepaalt zijn bod niet op basis van simpele regeltjes, maar door **Monte Carlo Simulaties**:
1.  **Hand Evaluatie**: De AI simuleert 30-40 keer het uitspelen van zijn eigen hand tegen willekeurige tegenstander-handen voor *elke* mogelijke troefkleur.
2.  **Verwachte Slagen**: Op basis hiervan berekent hij het gemiddeld aantal verwachte slagen.
3.  **Drempelwaardes**:
    -   **Solo Slim**: > 12.5 verwachte slagen.
    -   **Abondance**: > 9.0 verwachte slagen in de beste kleur.
    -   **Vraag**: > 5.5 verwachte slagen met de gedraaide troef.
    -   **Mee**: > 4.5 verwachte slagen.
    -   **Miserie**: < 1.5 verwachte slagen in de *beste* kleur (dus zelfs met zijn beste kleur haalt hij bijna niets).

### Speelstrategie (Hard AI)
De AI past zijn speelstijl aan op basis van zijn rol (Aanvaller vs. Verdediger) en het type spel.

#### 1. Algemene Technieken
-   **Kansen Berekening**: Voor elke kaart berekent de AI de winstkans (0-100%) op basis van nog niet gespeelde hogere kaarten en mogelijke troeven bij tegenstanders.
-   **Void Tracking**: De AI onthoudt welke spelers niet konden volgen op een kleur. Hij past zijn kansberekening hier op aan (risico op introeven) en kan zelfs bewust die kleuren spelen om troeven te "forceren".
-   **Partnerschap Herkenning**: De AI weet wie zijn partner is (bieder of mee-gaander) en zal nooit een slag van zijn partner proberen over te nemen als die al wint.

#### 2. Aanvallende Tactieken (Bieder/Partner)
-   **Troeven Trekken**: Als aanvaller zal de AI agressief **troef uitkomen** om de verdedigers te ontwapenen totdat hun troeven op zijn.
-   **Sure Winners**: Speelt kaarten uit met een berekende winstkans van >90% om zekerheid in te bouwen.

#### 3. Verdedigende Tactieken
-   **Troef Vermijden**: Verdedigers zullen bijna nooit troef uitkomen, tenzij ze hiertoe gedwongen worden. Ze bewaren hun troeven om slagen van de bieder af te troeven.
-   **Miserie Verdediging**:
    -   Als de Miserie-speler al gespeeld heeft en de slag *niet* wint (veilig is), zal de AI-verdediger zijn **hoogste kaart** van die kleur weggooien om 'gevaarlijke' slagen kwijt te raken.

#### 4. Miserie Zelf Spelen
-   **Starten**: Komt uit met de laagste kaart van zijn langste kleur (veiligheid).
-   **Volgen**: Speelt altijd de hoogst mogelijke kaart die *onder* de huidige winnende kaart ligt (ducken). Als hij gedwongen wordt te winnen, pakt hij de laagst mogelijke winnaar.
-   **Afgooien**: Gooit direct zijn gevaarlijkste hoge kaarten (Azen/Heren) weg als hij niet kan volgen.

#### 5. Samenwerking & Seinen (Bridge-style)
De Hard AI probeert informatie door te geven aan zijn partner:
-   **Seinen (Zenden)**: Als de AI moet afgooien (niet kan volgen), zal hij proberen een **hoge kaart** (7, 8, 9, 10) van een sterke kleur af te gooien. Dit is een signaal ("High Call") dat hij die kleur graag gespeeld wil hebben.
-   **Lezen & Samenwerken**: De AI analyseert de afgooi van zijn partner. Als hij een signaal detecteert, zal hij (als hij aan de beurt is) bij voorkeur **die kleur uitkomen** om zijn partner in de hand te spelen.

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
