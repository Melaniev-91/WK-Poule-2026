import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import streamlit as st
st.set_option('client.showErrorDetails', False)# Waarschuwing verouderd systeem uitzetten
from collections import defaultdict
import base64
import os
import unicodedata
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import firebase_admin
from firebase_admin import credentials, firestore

# _______________________________________________________________________________________________________
# Firebase database connectie maken
# _______________________________________________________________________________________________________

firebase_config = dict(st.secrets["firebase"])

cred = credentials.Certificate(firebase_config)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# _______________________________________________________________________________________________________
# >>>>>>>>>>STREANMLIT: WK POULE APP BOUWEN<<<<<<<<<<
# _______________________________________________________________________________________________________

# Stap 1: User Interface Start

# Stap 1.1 Pagina breedte
st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container {
    max-width: 1400px;   
    padding-left: 2rem;
    padding-right: 2rem;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

# Stap 1.2 Achtergrond kleur pagina
# Stap 1.2 Achtergrond kleur pagina
st.markdown("""
<style>
.stApp {
    background-color: #2A398D;
}
</style>
""", unsafe_allow_html=True)

# Stap 1.3 BANNER
st.markdown("""
<style>

@keyframes fifaMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.fifa-banner {
    background: linear-gradient(
        90deg,
        #F2C94C,
        #FDB719,
        #FFD36A,
        #FDB719,
        #F2C94C
    );

    background-size: 400% 400%;
    animation: fifaMove 8s ease infinite;

    padding: 28px;
    border-radius: 18px;

    margin-bottom: 25px;

    border: 3px solid #FFFFFF;

    /* 🔥 CENTREREN */
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;

    box-shadow: 0px 6px 18px rgba(0,0,0,0.25);
}

.fifa-banner h1 {
    margin: 0;
    color: #001F3F;
    font-size: 48px;
    font-weight: 900;
    letter-spacing: 2px;
    text-shadow: 0px 2px 6px rgba(255,255,255,0.3);
}

</style>

<div class="fifa-banner">
    <h1>🏆 WK Poule 2026</h1>
</div>
""", unsafe_allow_html=True)

# Stap 1.4 Algemene spacing & input styling
st.markdown("""
<style>

# ULTRA COMPACT MODE 
div[data-testid="stVerticalBlock"] {
    gap: 0.15rem !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 0.15rem !important;
}

# Number input styling (invoerveld)
div[data-testid="stNumberInput"] {
    width: 80px !important;
    margin-top: -20px;
}

# Remove extra markdown spacing
div[data-testid="stMarkdownContainer"] {
    margin-bottom: 0px !important;
}

</style>
""", unsafe_allow_html=True)

# Stap 1.5 Naam invullen
st.markdown("""
<style>

div[data-testid="stTextInput"] p {
    color: white !important;
    font-size: 18px !important;  
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

user = st.text_input("Vul hier je naam in")


# Stap 2: LANDEN OPMAKEN
# _______________________________________________________________________________________________________

# Stap 2.1.1 Functie Tekst normaliseren van landen (letten op bijv spaties)
def normalize_text(text):

    text = text.strip()

    text = unicodedata.normalize('NFKD', text)\
        .encode('ASCII', 'ignore')\
        .decode('ASCII')

    return text.lower()

# Stap 2.1.2 Functie Teamnamen (landen) opschonen
def clean_team(team):
    return unicodedata.normalize('NFKC', team).strip()

# Stap 2.1.3 Vlaggenlijst maken
def country_code(team):
    codes = {
        "nederland": "nl",
        "belgie": "be",
        "frankrijk": "fr",
        "duitsland": "de",
        "spanje": "es",
        "portugal": "pt",
        "engeland": "gb-eng",
        "schotland": "gb-sct",
        "wales": "gb-wls",
        "italie": "it",
        "kroatie": "hr",
        "denemarken": "dk",
        "zwitserland": "ch",
        "oostenrijk": "at",
        "polen": "pl",
        "servie": "rs",
        "tsjechie": "cz",
        "oekraine": "ua",
        "turkije": "tr",
        "noorwegen": "no",
        "zweden": "se",
        "bosnie": "ba",
        "brazilie": "br",
        "argentinie": "ar",
        "uruguay": "uy",
        "colombia": "co",
        "chili": "cl",
        "peru": "pe",
        "ecuador": "ec",
        "paraguay": "py",
        "venezuela": "ve",
        "haiti": "ht",
        "mexico": "mx",
        "verenigde staten": "us",
        "canada": "ca",
        "costa rica": "cr",
        "curacao": "cw",
        "panama": "pa",
        "jamaica": "jm",
        "marokko": "ma",
        "dr congo": "cd",
        "senegal": "sn",
        "egypte": "eg",
        "tunesie": "tn",
        "algerije": "dz",
        "nigeria": "ng",
        "kameroen": "cm",
        "ghana": "gh",
        "ivoorkust": "ci",
        "zuid-afrika": "za",
        "kaapverdie": "cv",
        "japan": "jp",
        "zuid-korea": "kr",
        "australie": "au",
        "iran": "ir",
        "saoedi-arabie": "sa",
        "qatar": "qa",
        "verenigde arabische emiraten": "ae",
        "irak": "iq",
        "oezbekistan": "uz",
        "jordanie": "jo",
        "nieuw-zeeland": "nz"
    }

    return codes.get(normalize_text(team))


def style_country(team):

    code = country_code(team)

    if code:
        flag_html = (
            f'<img src="https://flagcdn.com/24x18/{code}.png" '
            f'style="width:24px; height:18px; object-fit:cover; border-radius:2px;">'
        )
    else:
        flag_html = ""

    if normalize_text(team) == "nederland":
        land_naam = team.upper()
        land_kleur = "#FF8C00"
        font_weight = "900"
    else:
        land_naam = team
        land_kleur = "white"
        font_weight = "700"

    return f"""
    <span style="
        display:flex;
        align-items:center;
        gap:6px;
        color:{land_kleur};
        font-weight:{font_weight};
        white-space:nowrap;
    ">
        {flag_html}
        {land_naam}
    </span>
    """

# Stap 3: WEDSTRIJDEN OPHALEN FIRESTORE
# _______________________________________________________________________________________________________

wedstrijden = db.collection("Wedstrijden").stream()

# Stap 3.1 Structuur per poule maken
poules = {}

for w in wedstrijden:
    data = w.to_dict()

    poule = data.get("Poule")
    fase = data.get("Fase")

    if fase != "Poule":
        continue

    if poule not in poules:
        poules[poule] = []

    poules[poule].append(data)

    # sorteren op ronde
    for poule in poules:
        poules[poule] = sorted(
            poules[poule],
            key=lambda x: x["Ronde"]
        )


# Stap 4: UI PER POULE
# _______________________________________________________________________________________________________

# Stap 4.1 De + - weghalen achter de invoervelden
st.markdown("""
<style>
/* Verberg + en - bij number_input */
div[data-testid="stNumberInput"] button {
    display: none;
}
</style>
""", unsafe_allow_html=True)

standen = {}

# Stap 4.2 Opmaak poulfase
# _______________________________________________________________________________________________________

# Stap 4.2.1 Titel toevoegen aan kolommen / ruimtes (Poule & Stand)

# 🏆 MINI FIFA BANNER alleen bij Poule
st.markdown("""
        <style>
        .poule-banner {
            background: linear-gradient(90deg,#0A5546,#1F8F7A,#5FF2D5);
            padding: 14px 20px;
            border-radius: 12px;
            margin-bottom: 10px;
            text-align: center;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
        }

        .poule-banner h2 {
            margin: 0;
            color: white;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        </style>

        <div class="poule-banner">
            <h2>Poulefase</h2>
        </div>
        """, unsafe_allow_html=True)

for poule in sorted(poules.keys()):

    # Hoeveelheid ruimte
    title_left, spacer_title, title_right = st.columns([3.2, 0.4, 2.3])

    header_style = """
        <div style="
            background: linear-gradient(90deg, #002B5C, #004B8D);
            padding: 6px 12px;
            border-radius: 10px;
            text-align: center;
            border: 1.5px solid #D4AF37;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.12);
        ">
            <span style="
                color: white;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 1px;
            ">
    """

    # POULE (links)
    with title_left:
        st.markdown(
            header_style + f"Poule {poule}</span></div>",
            unsafe_allow_html=True
        )

    # STAND (rechts)
    with title_right:
        st.markdown(
            header_style + "Stand</span></div>",
            unsafe_allow_html=True
        )

    left_col, spacer, right_col = st.columns([3.2, 0.4, 2.3])

    standen[poule] = {}

    wedstrijden_sorted = sorted(
        poules[poule],
        key=lambda x: x.get("Ronde", 0)
    )

    # LINKS = wedstrijden
    with left_col:

        for wedstrijd in wedstrijden_sorted:

            home = clean_team(wedstrijd["home_team"])
            away = clean_team(wedstrijd["away_team"])
            match_id = wedstrijd["match_id"]
            ronde = wedstrijd.get("Ronde", "")

            # teams initialiseren
            for team in [home, away]:

                if team not in standen[poule]:
                    standen[poule][team] = {
                        "punten": 0,
                        "gespeeld": 0,
                        "voor": 0,
                        "tegen": 0,
                        "saldo": 0
                    }

            col0, col1, col2, col3, col4, col5 = st.columns(
                [0.5, 1.5, 0.5, 1, 1.5, 0.5],
                vertical_alignment="center"
            )

            with col0:
                st.markdown(
                    f"<div style='font-weight:700; color:white;'>{ronde}</div>",
                    unsafe_allow_html=True
                )

            with col1:
                st.markdown(
                    f"{style_country(home)}",
                    unsafe_allow_html=True
                )

            with col2:
                st.number_input(
                    label="",
                    min_value=0,
                    max_value=20,
                    step=1,
                    value=None,
                    placeholder="-",
                    key=f"{match_id}_home"
                )

            with col3:
                st.markdown(
                    "<div style='text-align:center; color:white; font-size:16px; font-weight:900;'>VS</div>",
                    unsafe_allow_html=True
                )

            with col4:
                st.markdown(
                    f"{style_country(away)}",
                    unsafe_allow_html=True
                )

            with col5:
                st.number_input(
                    label="",
                    min_value=0,
                    max_value=20,
                    step=1,
                    value=None,
                    placeholder="-",
                    key=f"{match_id}_away"
                )

            # LIVE STAND BEREKENEN
            home_score = st.session_state.get(f"{match_id}_home")
            away_score = st.session_state.get(f"{match_id}_away")

            # Alleen berekenen als beide velden ingevuld zijn
            if home_score is not None and away_score is not None:

                standen[poule][home]["gespeeld"] += 1
                standen[poule][away]["gespeeld"] += 1

                standen[poule][home]["voor"] += home_score
                standen[poule][home]["tegen"] += away_score

                standen[poule][away]["voor"] += away_score
                standen[poule][away]["tegen"] += home_score

                standen[poule][home]["saldo"] = (
                        standen[poule][home]["voor"]
                        - standen[poule][home]["tegen"]
                )

                standen[poule][away]["saldo"] = (
                        standen[poule][away]["voor"]
                        - standen[poule][away]["tegen"]
                )

                if home_score > away_score:
                    standen[poule][home]["punten"] += 3

                elif away_score > home_score:
                    standen[poule][away]["punten"] += 3

                else:
                    standen[poule][home]["punten"] += 1
                    standen[poule][away]["punten"] += 1

    # RECHTS = LIVE STAND TABEL
    with right_col:

        # kleine spacing bovenaan
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

        from collections import defaultdict
        import pandas as pd


        # HEAD TO HEAD functie
        def head_to_head(teams, wedstrijden):

            h2h = defaultdict(lambda: {
                "punten": 0,
                "saldo": 0,
                "voor": 0
            })

            for w in wedstrijden:

                home = clean_team(w["home_team"])
                away = clean_team(w["away_team"])

                if home not in teams or away not in teams:
                    continue

                hs = st.session_state.get(f"{w['match_id']}_home")
                aw = st.session_state.get(f"{w['match_id']}_away")

                # alleen meenemen als beide ingevuld
                if hs is None or aw is None:
                    continue

                hs = int(hs)
                aw = int(aw)

                # punten
                if hs > aw:
                    h2h[home]["punten"] += 3

                elif aw > hs:
                    h2h[away]["punten"] += 3

                else:
                    h2h[home]["punten"] += 1
                    h2h[away]["punten"] += 1

                # goals
                h2h[home]["voor"] += hs
                h2h[home]["saldo"] += hs - aw

                h2h[away]["voor"] += aw
                h2h[away]["saldo"] += aw - hs

            return h2h


        h2h = head_to_head(
            list(standen[poule].keys()),
            poules[poule]
        )


        # sortering
        def final_sort(item):

            team, stats = item
            h = h2h[team]

            return (
                stats["punten"],
                stats["saldo"],
                stats["voor"],
                h["punten"],
                h["saldo"],
                h["voor"]
            )


        ranking = sorted(
            standen[poule].items(),
            key=final_sort,
            reverse=True
        )

        # DATAFRAME bouwen
        table_data = []

        for i, (team, stats) in enumerate(ranking, start=1):
            code = country_code(team)

            if code:
                flag_html = f'<img src="https://flagcdn.com/24x18/{code}.png" style="width:24px; height:18px; object-fit:cover; border-radius:2px;">'
            else:
                flag_html = ""

            land_naam = team.upper() if normalize_text(team) == "nederland" else team
            land_kleur = "#FF8C00" if normalize_text(team) == "nederland" else "black"

            table_data.append({
                "NR": i,
                "Land": f'<span style="display:flex; align-items:center; gap:6px; color:{land_kleur}; font-weight:700;">{flag_html}{land_naam}</span>',
                "Pt": stats["punten"],
                "DS": stats["saldo"],
                "DV": stats["voor"],
                "DT": stats["tegen"]
            })

        df = pd.DataFrame(table_data)

        # TABEL STYLING
        st.markdown("""
        <style>

        .stand-table table {
            width: 100%;
            border-collapse: collapse;
            font-size: 15px;
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }

        .stand-table thead tr {
            background: #001F3F;
            color: white;
        }

        .stand-table th {
            padding: 10px;
            text-align: center;
            font-weight: 700;
        }

        .stand-table td {
            padding: 9px;
            text-align: center;
            border-bottom: 1px solid #EAEAEA;
            font-weight: 600;
        }

        .stand-table tbody tr:nth-child(1),
        .stand-table tbody tr:nth-child(2) {
            background-color: #C8F7C5;
        }

        .stand-table tbody tr:nth-child(3) {
            background-color: #FFE0B2;
        }

        .stand-table tbody tr:nth-child(4) {
            background-color: #FFFFFF;
        }

        </style>
        """, unsafe_allow_html=True)

        # dataframe tonen als HTML
        st.markdown(
            f"""
            <div class="stand-table">
                {df.to_html(index=False, escape=False)}
            </div>
            """,
            unsafe_allow_html=True
        )


# Stap .. : Opmaak 16e FINALE
# _______________________________________________________________________________________________________

# Placeholder Banner 16e finale
st.markdown("""
        <style>
        .knockout-banner {
            background: linear-gradient(90deg, #D62828, #F77F00);
            padding: 14px 20px;
            border-radius: 12px;
            margin-top: 25px;
            margin-bottom: 10px;
            text-align: center;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
        }

        .knockout-banner h2 {
            margin: 0;
            color: white;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        </style>

        <div class="knockout-banner">
            <h2>16e finale</h2>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================================
# 16e FINALE
# =====================================================================================

# =====================================================================================
# MATCHES
# =====================================================================================

matches = [
    ("A", "B"),
    ("C", "D"),
    ("E", "F"),
    ("G", "H"),
    ("I", "J"),
    ("K", "L"),
    ("M", "N"),
    ("O", "P"),
    ("Q", "R"),
    ("S", "T"),
    ("U", "V"),
    ("W", "X"),
    ("Y", "Z"),
    ("AA", "AB"),
    ("AC", "AD"),
    ("AE", "AF"),
]

# Officieel Wedstrijdnummer (FIFA)
match_number_map = {
    0: 73,
    1: 76,
    2: 74,
    3: 75,
    4: 78,
    5: 77,
    6: 79,
    7: 80,
    8: 82,
    9: 81,
    10: 84,
    11: 83,
    12: 85,
    13: 88,
    14: 86,
    15: 87
}

# =====================================================================================
# HELPERS
# =====================================================================================

def get_poule_ranking(poule):
    wedstrijden_poule = poules[poule]

    h2h = head_to_head(
        list(standen[poule].keys()),
        wedstrijden_poule
    )

    def final_sort(item):
        team, stats = item
        h = h2h[team]

        return (
            stats["punten"],
            stats["saldo"],
            stats["voor"],
            h["punten"],
            h["saldo"],
            h["voor"]
        )

    return sorted(
        standen[poule].items(),
        key=final_sort,
        reverse=True
    )

fifa_ranking = {
    "Argentinië": 1,
    "Spanje": 2,
    "Frankrijk": 3,
    "Engeland": 4,
    "Brazilië": 5,
    "Nederland": 6,
    "Portugal": 7,
    "België": 8,
    "Italië": 9,
    "Duitsland": 10,
    "Kroatië": 11,
    "Marokko": 12,
    "Uruguay": 13,
    "Colombia": 14,
    "Japan": 15,
    "Mexico": 16,
    "Verenigde Staten": 17,
    "Zwitserland": 18,
    "Iran": 19,
    "Denemarken": 20,
    "Oostenrijk": 21,
    "Zuid-Korea": 22,
    "Senegal": 23,
    "Australië": 24,
    "Oekraïne": 25,
    "Turkije": 26,
    "Zweden": 27,
    "Noorwegen": 28,
    "Polen": 29,
    "Servië": 30,
    "Tsjechië": 31,
    "Nigeria": 32,
    "Egypte": 33,
    "Tunesië": 34,
    "Algerije": 35,
    "Ghana": 36,
    "Kameroen": 37,
    "Ivoorkust": 38,
    "DR Congo": 39,
    "Zuid-Afrika": 40,
    "Canada": 41,
    "Costa Rica": 42,
    "Panama": 43,
    "Jamaica": 44,
    "Qatar": 45,
    "Saoedi-Arabië": 46,
    "Irak": 47,
    "Jordanië": 48,
    "Oezbekistan": 49,
    "Verenigde Arabische Emiraten": 50,
    "Nieuw-Zeeland": 51,
    "Ecuador": 52,
    "Peru": 53,
    "Paraguay": 54,
    "Chili": 55,
    "Venezuela": 56,
    "Bosnië": 57,
    "Haiti": 58,
    "Curaçao": 59
}

def get_sorted_third_places(standen):

    third_places = []

    for poule, teams in standen.items():

        ranking = get_poule_ranking(poule)

        if len(ranking) >= 3:
            team, stats = ranking[2]

            third_places.append({
                "team": team,
                "poule": poule,
                "punten": stats["punten"],
                "saldo": stats["saldo"],
                "voor": stats["voor"]
            })

    third_places = sorted(
        third_places,
        key=lambda x: (
            x["punten"],
            x["saldo"],
            x["voor"],
            -fifa_ranking.get(x["team"], 999)
        ),
        reverse=True
    )

    return third_places[:8]


def pick_third_place_for_slot(allowed_groups, used):

    pool = get_sorted_third_places(standen)

    for p in pool:

        if p["poule"] not in allowed_groups:
            continue

        if p["team"] in used:
            continue

        used.add(p["team"])
        return p["team"]

    return "TBD"


# =====================================================================================
# POULE MAP
# =====================================================================================

poule_map = {
    "A": ("A", 2),
    "B": ("B", 2),
    "C": ("C", 1),
    "D": ("F", 2),
    "E": ("E", 1),
    "F": ("3:A/B/C/D/F", 0),
    "G": ("F", 1),
    "H": ("C", 2),
    "I": ("E", 2),
    "J": ("I", 2),
    "K": ("I", 1),
    "L": ("3:C/D/F/G/H", 0),
    "M": ("A", 1),
    "N": ("3:C/E/F/H/I", 0),
    "O": ("L", 1),
    "P": ("3:E/H/I/J/K", 0),
    "Q": ("G", 1),
    "R": ("3:A/E/H/I/J", 0),
    "S": ("D", 1),
    "T": ("3:B/E/F/I/J", 0),
    "U": ("H", 1),
    "V": ("J", 2),
    "W": ("K", 2),
    "X": ("L", 2),
    "Y": ("B", 1),
    "Z": ("3:E/F/G/I/J", 0),
    "AA": ("D", 2),
    "AB": ("G", 2),
    "AC": ("J", 1),
    "AD": ("H", 2),
    "AE": ("K", 1),
    "AF": ("3:D/E/I/J/L", 0)
}


# =====================================================================================
# RESOLVE TEAM
# =====================================================================================

def resolve_team(team_key, used_third_places):

    rule = poule_map.get(team_key)

    if rule is None:
        return team_key

    poule, pos = rule

    if isinstance(poule, str) and poule.startswith("3:"):
        groups = poule.replace("3:", "").split("/")
        return pick_third_place_for_slot(groups, used_third_places)

    if poule not in standen:
        return "TBD"

    ranking = get_poule_ranking(poule)

    if len(ranking) < pos:
        return "TBD"

    return ranking[pos - 1][0]


used_third_places = set()


# =====================================================================================
# 16E FINALE TEAMS EENMALIG PER RERUN OPBOUWEN
# =====================================================================================

def build_round16_teams():
    used_third_places = set()
    resolved = {}

    for team_key in poule_map.keys():
        resolved[team_key] = resolve_team(
            team_key,
            used_third_places
        )

    return resolved


round16_teams = build_round16_teams()

def get_knockout_winner(home_key, away_key, winner_key, home_team, away_team):
    home_score = st.session_state.get(home_key)
    away_score = st.session_state.get(away_key)

    if home_score is None or away_score is None:
        return "TBD"

    if home_score > away_score:
        return home_team

    if away_score > home_score:
        return away_team

    return st.session_state.get(winner_key, "TBD")

st.markdown("""
<style>
/* Radio tekst wit maken */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] p,
div[data-testid="stRadio"] span {
    color: white !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

def toon_winnaar_bij_gelijk(match_id, home_team, away_team, home_key, away_key, winner_key):
    home_score = st.session_state.get(home_key)
    away_score = st.session_state.get(away_key)

    if home_score is not None and away_score is not None and home_score == away_score:

        st.markdown(
            f"""
            <div style="
                color:#FFD36A;
                font-weight:800;
                font-size:15px;
                margin-top:8px;
                margin-bottom:4px;
            ">
                Gelijke stand: kies wie doorgaat na verlenging/penalty's
            </div>
            """,
            unsafe_allow_html=True
        )

        st.radio(
            label="",
            options=[home_team, away_team],
            key=winner_key,
            horizontal=True,
            label_visibility="collapsed"
        )

# =====================================================================================
# UI 16e FINALE
# =====================================================================================

for row in range(0, len(matches), 2):

    match1 = matches[row]
    match2 = matches[row + 1]

    match1_id = match_number_map[row]
    match2_id = match_number_map[row + 1]

    (
        col1, col2, col3, col4, col5,
        spacer,
        col6, col7, col8, col9, col10
    ) = st.columns(
        [0.6, 0.4, 0.25, 0.6, 0.4, 1, 0.6, 0.4, 0.25, 0.6, 0.4],
        vertical_alignment="center"
    )

    # MATCH 1
    home1 = round16_teams.get(match1[0], "TBD")
    away1 = round16_teams.get(match1[1], "TBD")

    with col1:
        st.markdown(style_country(home1), unsafe_allow_html=True)

    with col2:
        st.number_input(
            "",
            key=f"{match1_id}_home",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col3:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(style_country(away1), unsafe_allow_html=True)

    with col5:
        st.number_input(
            "",
            key=f"{match1_id}_away",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    # MATCH 2
    home2 = round16_teams.get(match2[0], "TBD")
    away2 = round16_teams.get(match2[1], "TBD")

    with col6:
        st.markdown(style_country(home2), unsafe_allow_html=True)

    with col7:
        st.number_input(
            "",
            key=f"{match2_id}_home",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col8:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col9:
        st.markdown(style_country(away2), unsafe_allow_html=True)

    with col10:
        st.number_input(
            "",
            key=f"{match2_id}_away",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    # GELIJKSPEL KEUZES ONDER DE JUISTE WEDSTRIJD
    tie_col1, tie_spacer, tie_col2 = st.columns([5.3, 1, 5.3])

    with tie_col1:
        toon_winnaar_bij_gelijk(
            match1_id,
            home1,
            away1,
            f"{match1_id}_home",
            f"{match1_id}_away",
            f"r16_winner_{match1_id}"
        )

    with tie_col2:
        toon_winnaar_bij_gelijk(
            match2_id,
            home2,
            away2,
            f"{match2_id}_home",
            f"{match2_id}_away",
            f"r16_winner_{match2_id}"
        )

    st.markdown(
        "<div style='height:8px;'></div>",
        unsafe_allow_html=True
    )

# =====================================================================================
# 8e FINALE (OUTPUT)
# =====================================================================================

eighth_matches = [
    (73, 75, 90),
    (74, 77, 89),
    (76, 78, 91),
    (79, 80, 92),
    (83, 84, 93),
    (81, 82, 94),
    (86, 88, 95),
    (85, 87, 96),
]

# =====================================================================================
# HELPER: WINNAAR UIT 16e FINALE
# =====================================================================================

round16_match_map = {
    match_number_map[i]: matches[i]
    for i in range(len(matches))
}

def get_16e_winner(match_id):
    home_key, away_key = round16_match_map[match_id]

    home_team = round16_teams.get(home_key, "TBD")
    away_team = round16_teams.get(away_key, "TBD")

    return get_knockout_winner(
        f"{match_id}_home",
        f"{match_id}_away",
        f"r16_winner_{match_id}",
        home_team,
        away_team
    )


# =====================================================================================
# RESOLVE 8e FINALE TEAM
# =====================================================================================

def resolve_eighth_team(value):

    if isinstance(value, int):
        return get_16e_winner(value)

    return value


# =====================================================================================
# 8e FINALE UI
# =====================================================================================

st.markdown("""
<div style="
    background: linear-gradient(90deg, #D62828, #F77F00);
    padding: 14px 20px;
    border-radius: 12px;
    margin-top: 25px;
    margin-bottom: 10px;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
">
    <h2 style="
        margin:0;
        color:white;
        font-size:26px;
        font-weight:800;
        letter-spacing:1px;
    ">
        8e finale
    </h2>
</div>
""", unsafe_allow_html=True)


for row in range(0, len(eighth_matches), 2):

    match1 = eighth_matches[row]
    match2 = eighth_matches[row + 1]

    col1, col2, col3, col4, col5, spacer, col6, col7, col8, col9, col10 = st.columns(
        [0.6, 0.4, 0.25, 0.6, 0.4, 1, 0.6, 0.4, 0.25, 0.6, 0.4],
        vertical_alignment="center"
    )

    # MATCH 1
    home1 = resolve_eighth_team(match1[0])
    away1 = resolve_eighth_team(match1[1])

    with col1:
        st.markdown(style_country(home1), unsafe_allow_html=True)

    with col2:
        st.number_input(
            "",
            key=f"eighth_home_{match1[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col3:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(style_country(away1), unsafe_allow_html=True)

    with col5:
        st.number_input(
            "",
            key=f"eighth_away_{match1[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    # MATCH 2
    home2 = resolve_eighth_team(match2[0])
    away2 = resolve_eighth_team(match2[1])

    with col6:
        st.markdown(style_country(home2), unsafe_allow_html=True)

    with col7:
        st.number_input(
            "",
            key=f"eighth_home_{match2[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col8:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col9:
        st.markdown(style_country(away2), unsafe_allow_html=True)

    with col10:
        st.number_input(
            "",
            key=f"eighth_away_{match2[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    # GELIJKSPEL KEUZES
    tie_col1, tie_spacer, tie_col2 = st.columns([5.3, 1, 5.3])

    with tie_col1:
        toon_winnaar_bij_gelijk(
            match1[2],
            home1,
            away1,
            f"eighth_home_{match1[2]}",
            f"eighth_away_{match1[2]}",
            f"eighth_winner_{match1[2]}"
        )

    with tie_col2:
        toon_winnaar_bij_gelijk(
            match2[2],
            home2,
            away2,
            f"eighth_home_{match2[2]}",
            f"eighth_away_{match2[2]}",
            f"eighth_winner_{match2[2]}"
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# =====================================================================================
# KWARTFINALE
# =====================================================================================

quarter_matches = [
    (89, 90, 97),
    (93, 94, 98),
    (91, 92, 99),
    (95, 96, 100),
]


# =====================================================================================
# RESOLVE WINNER UIT 8E FINALE
# =====================================================================================

eighth_match_map = {
    match[2]: (match[0], match[1])
    for match in eighth_matches
}

def get_eighth_winner(match_id):
    home_source, away_source = eighth_match_map[match_id]

    home_team = resolve_eighth_team(home_source)
    away_team = resolve_eighth_team(away_source)

    return get_knockout_winner(
        f"eighth_home_{match_id}",
        f"eighth_away_{match_id}",
        f"eighth_winner_{match_id}",
        home_team,
        away_team
    )


# =====================================================================================
# RESOLVE KWARTFINALE TEAM
# =====================================================================================

def resolve_quarter_team(match_id):
    return get_eighth_winner(match_id)


# =====================================================================================
# UI KWARTFINALE
# =====================================================================================

st.markdown("""
<div style="
    background: linear-gradient(90deg, #D62828, #F77F00);
    padding: 14px 20px;
    border-radius: 12px;
    margin-top: 25px;
    margin-bottom: 10px;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
">
    <h2 style="
        margin:0;
        color:white;
        font-size:26px;
        font-weight:800;
        letter-spacing:1px;
    ">
        Kwartfinales
    </h2>
</div>
""", unsafe_allow_html=True)


for i in range(0, len(quarter_matches), 2):

    match1 = quarter_matches[i]
    match2 = quarter_matches[i + 1]

    col1, col2, col3, col4, col5, spacer, col6, col7, col8, col9, col10 = st.columns(
        [0.6, 0.4, 0.25, 0.6, 0.4, 1, 0.6, 0.4, 0.25, 0.6, 0.4],
        vertical_alignment="center"
    )

    # MATCH 1
    home1 = resolve_quarter_team(match1[0])
    away1 = resolve_quarter_team(match1[1])

    with col1:
        st.markdown(style_country(home1), unsafe_allow_html=True)

    with col2:
        st.number_input(
            "",
            key=f"qf_home_{match1[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col3:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(style_country(away1), unsafe_allow_html=True)

    with col5:
        st.number_input(
            "",
            key=f"qf_away_{match1[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    # MATCH 2
    home2 = resolve_quarter_team(match2[0])
    away2 = resolve_quarter_team(match2[1])

    with col6:
        st.markdown(style_country(home2), unsafe_allow_html=True)

    with col7:
        st.number_input(
            "",
            key=f"qf_home_{match2[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col8:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col9:
        st.markdown(style_country(away2), unsafe_allow_html=True)

    with col10:
        st.number_input(
            "",
            key=f"qf_away_{match2[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    # GELIJKSPEL KEUZES
    tie_col1, tie_spacer, tie_col2 = st.columns([5.3, 1, 5.3])

    with tie_col1:
        toon_winnaar_bij_gelijk(
            match1[2],
            home1,
            away1,
            f"qf_home_{match1[2]}",
            f"qf_away_{match1[2]}",
            f"qf_winner_{match1[2]}"
        )

    with tie_col2:
        toon_winnaar_bij_gelijk(
            match2[2],
            home2,
            away2,
            f"qf_home_{match2[2]}",
            f"qf_away_{match2[2]}",
            f"qf_winner_{match2[2]}"
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# =====================================================================================
# RESOLVE WINNAAR UIT KWARTFINALE
# =====================================================================================

quarter_match_map = {
    match[2]: (match[0], match[1])
    for match in quarter_matches
}

def get_quarter_winner(match_id):
    home_source, away_source = quarter_match_map[match_id]

    home_team = resolve_quarter_team(home_source)
    away_team = resolve_quarter_team(away_source)

    return get_knockout_winner(
        f"qf_home_{match_id}",
        f"qf_away_{match_id}",
        f"qf_winner_{match_id}",
        home_team,
        away_team
    )

# =====================================================================================
# HALVE FINALE
# =====================================================================================

semi_matches = [
    (97, 98, 101),
    (99, 100, 102),
]


# =====================================================================================
# RESOLVE HALVE FINALE TEAM
# =====================================================================================

def resolve_semi_team(match_id):
    return get_quarter_winner(match_id)


# =====================================================================================
# UI HALVE FINALE
# =====================================================================================

st.markdown("""
<div style="
    background: linear-gradient(90deg, #D62828, #F77F00);
    padding: 14px 20px;
    border-radius: 12px;
    margin-top: 25px;
    margin-bottom: 10px;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
">
    <h2 style="margin:0; color:white; font-size:26px; font-weight:800; letter-spacing:1px;">
        Halve finales
    </h2>
</div>
""", unsafe_allow_html=True)


for i in range(0, len(semi_matches), 2):

    match1 = semi_matches[i]
    match2 = semi_matches[i + 1]

    col1, col2, col3, col4, col5, spacer, col6, col7, col8, col9, col10 = st.columns(
        [0.6, 0.4, 0.25, 0.6, 0.4, 1, 0.6, 0.4, 0.25, 0.6, 0.4],
        vertical_alignment="center"
    )

    home1 = resolve_semi_team(match1[0])
    away1 = resolve_semi_team(match1[1])

    with col1:
        st.markdown(style_country(home1), unsafe_allow_html=True)

    with col2:
        st.number_input("", key=f"sf_home_{match1[2]}", min_value=0, max_value=20, step=1, value=None, placeholder="-", label_visibility="collapsed")

    with col3:
        st.markdown("<div style='text-align:center;color:white;font-weight:900;'>VS</div>", unsafe_allow_html=True)

    with col4:
        st.markdown(style_country(away1), unsafe_allow_html=True)

    with col5:
        st.number_input("", key=f"sf_away_{match1[2]}", min_value=0, max_value=20, step=1, value=None, placeholder="-", label_visibility="collapsed")

    home2 = resolve_semi_team(match2[0])
    away2 = resolve_semi_team(match2[1])

    with col6:
        st.markdown(style_country(home2), unsafe_allow_html=True)

    with col7:
        st.number_input("", key=f"sf_home_{match2[2]}", min_value=0, max_value=20, step=1, value=None, placeholder="-", label_visibility="collapsed")

    with col8:
        st.markdown("<div style='text-align:center;color:white;font-weight:900;'>VS</div>", unsafe_allow_html=True)

    with col9:
        st.markdown(style_country(away2), unsafe_allow_html=True)

    with col10:
        st.number_input("", key=f"sf_away_{match2[2]}", min_value=0, max_value=20, step=1, value=None, placeholder="-", label_visibility="collapsed")

    # GELIJKSPEL KEUZES
    tie_col1, tie_spacer, tie_col2 = st.columns([5.3, 1, 5.3])

    with tie_col1:
        toon_winnaar_bij_gelijk(
            match1[2],
            home1,
            away1,
            f"sf_home_{match1[2]}",
            f"sf_away_{match1[2]}",
            f"sf_winner_{match1[2]}"
        )

    with tie_col2:
        toon_winnaar_bij_gelijk(
            match2[2],
            home2,
            away2,
            f"sf_home_{match2[2]}",
            f"sf_away_{match2[2]}",
            f"sf_winner_{match2[2]}"
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# =====================================================================================
# RESOLVE WINNAAR UIT HALVE FINALE
# =====================================================================================

semi_match_map = {
    match[2]: (match[0], match[1])
    for match in semi_matches
}

def get_semi_winner(match_id):
    home_source, away_source = semi_match_map[match_id]

    home_team = resolve_semi_team(home_source)
    away_team = resolve_semi_team(away_source)

    return get_knockout_winner(
        f"sf_home_{match_id}",
        f"sf_away_{match_id}",
        f"sf_winner_{match_id}",
        home_team,
        away_team
    )

# =====================================================================================
# FINALE
# =====================================================================================

final_matches = [
    (101, 102, 103),
]


# =====================================================================================
# RESOLVE FINALE TEAM
# =====================================================================================

def resolve_final_team(match_id):
    return get_semi_winner(match_id)


# =====================================================================================
# UI FINALE
# =====================================================================================

st.markdown("""
<div style="
    background: linear-gradient(90deg,#6B8E00,#98C400,#BFE715);
    padding: 14px 20px;
    border-radius: 12px;
    margin-top: 25px;
    margin-bottom: 10px;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.2);
">
    <h2 style="
        margin:0;
        color:white;
        font-size:26px;
        font-weight:900;
        letter-spacing:1px;
    ">
        🏆 Finale
    </h2>
</div>
""", unsafe_allow_html=True)


for i in range(len(final_matches)):

    match = final_matches[i]

    col1, col2, col3, col4, col5 = st.columns(
        [0.6, 0.4, 0.25, 0.6, 0.4],
        vertical_alignment="center"
    )

    home = resolve_final_team(match[0])
    away = resolve_final_team(match[1])

    with col1:
        st.markdown(style_country(home), unsafe_allow_html=True)

    with col2:
        st.number_input(
            "",
            key=f"final_home_{match[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    with col3:
        st.markdown(
            "<div style='text-align:center;color:white;font-weight:900;'>VS</div>",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(style_country(away), unsafe_allow_html=True)

    with col5:
        st.number_input(
            "",
            key=f"final_away_{match[2]}",
            min_value=0,
            max_value=20,
            step=1,
            value=None,
            placeholder="-",
            label_visibility="collapsed"
        )

    toon_winnaar_bij_gelijk(
        match[2],
        home,
        away,
        f"final_home_{match[2]}",
        f"final_away_{match[2]}",
        f"final_winner_{match[2]}"
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# =====================================================================================
# WINNAAR FINALE
# =====================================================================================

def get_final_winner(match_id):
    home = resolve_final_team(final_matches[0][0])
    away = resolve_final_team(final_matches[0][1])

    return get_knockout_winner(
        f"final_home_{match_id}",
        f"final_away_{match_id}",
        f"final_winner_{match_id}",
        home,
        away
    )

# =====================================================================================
# BONUSVRAGEN
# =====================================================================================

st.markdown("""
<div style="
    background: linear-gradient(90deg,#6F52CC,#8F6EF0,#AE88FB);
    padding: 14px 20px;
    border-radius: 12px;
    margin-top: 30px;
    margin-bottom: 15px;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.15);
">
    <h2 style="
        margin:0;
        color:white;
        font-size:26px;
        font-weight:800;
        letter-spacing:1px;
    ">
        ⭐ Bonusvragen
    </h2>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<style>

.bonus-label {
    color: white;
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 2px;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)


# 1. GELE KAARTEN
st.markdown(
    '<div class="bonus-label">🟨 Totaal aantal gele kaarten tijdens het WK 2026</div>',
    unsafe_allow_html=True
)

gele_kaarten = st.number_input(
    "",
    min_value=0,
    max_value=500,
    step=1,
    value=None,
    placeholder="Aantal gele kaarten",
    key="bonus_gele_kaarten",
    label_visibility="collapsed"
)


# 2. RODE KAARTEN
st.markdown(
    '<div class="bonus-label">🟥 Totaal aantal rode kaarten tijdens het WK 2026</div>',
    unsafe_allow_html=True
)

rode_kaarten = st.number_input(
    "",
    min_value=0,
    max_value=100,
    step=1,
    value=None,
    placeholder="Aantal rode kaarten",
    key="bonus_rode_kaarten",
    label_visibility="collapsed"
)


# 3. DOELPUNTEN
st.markdown(
    '<div class="bonus-label">⚽ Totaal aantal doelpunten tijdens het WK 2026</div>',
    unsafe_allow_html=True
)

doelpunten = st.number_input(
    "",
    min_value=0,
    max_value=500,
    step=1,
    value=None,
    placeholder="Aantal doelpunten",
    key="bonus_doelpunten",
    label_visibility="collapsed"
)


# 4. TOPSCOORDER
st.markdown(
    '<div class="bonus-label">👑 Topscoorder van het WK 2026</div>',
    unsafe_allow_html=True
)

st.markdown("""
<style>
div[data-testid="stTextInput"] {
    margin-top: -18px;
}
</style>
""", unsafe_allow_html=True)

topscorer = st.text_input(
    "",
    key="bonus_topscorer",
    placeholder="Naam speler",
    label_visibility="collapsed"
)

# =================================================================================
# CONTROLEREN OF ALLES IS INGEVULD
# =================================================================================

def alles_ingevuld():

    # Poulefase
    for poule in poules.values():
        for wedstrijd in poule:
            match_id = wedstrijd["match_id"]

            if st.session_state.get(f"{match_id}_home") is None:
                return False
            if st.session_state.get(f"{match_id}_away") is None:
                return False

    # 16e finale
    for i, match in enumerate(matches):
        match_id = match_number_map[i]

        if st.session_state.get(f"{match_id}_home") is None:
            return False
        if st.session_state.get(f"{match_id}_away") is None:
            return False

    # 8e finale
    for match in eighth_matches:
        match_id = match[2]

        if st.session_state.get(f"eighth_home_{match_id}") is None:
            return False
        if st.session_state.get(f"eighth_away_{match_id}") is None:
            return False

    # Kwartfinale
    for match in quarter_matches:
        match_id = match[2]

        if st.session_state.get(f"qf_home_{match_id}") is None:
            return False
        if st.session_state.get(f"qf_away_{match_id}") is None:
            return False

    # Halve finale
    for match in semi_matches:
        match_id = match[2]

        if st.session_state.get(f"sf_home_{match_id}") is None:
            return False
        if st.session_state.get(f"sf_away_{match_id}") is None:
            return False

    # Finale
    for match in final_matches:
        match_id = match[2]

        if st.session_state.get(f"final_home_{match_id}") is None:
            return False
        if st.session_state.get(f"final_away_{match_id}") is None:
            return False

    # Bonusvragen
    if st.session_state.get("bonus_gele_kaarten") is None:
        return False

    if st.session_state.get("bonus_rode_kaarten") is None:
        return False

    if st.session_state.get("bonus_doelpunten") is None:
        return False

    if not st.session_state.get("bonus_topscorer"):
        return False

    return True

# =================================================================================
# MELDINGEN IN EIGEN STIJL
# =================================================================================

def toon_error_bericht(tekst):
    st.markdown(f"""
    <div style="
        background-color:#D62828;
        color:white;
        padding:12px 16px;
        border-radius:10px;
        font-weight:700;
        font-size:15px;
        margin-top:10px;
        margin-bottom:10px;
        width:fit-content;
        min-width:420px;
        max-width:700px;
        box-shadow:0px 2px 6px rgba(0,0,0,0.2);
    ">
        ✕ &nbsp; {tekst}
    </div>
    """, unsafe_allow_html=True)


def toon_success_bericht(tekst):
    st.markdown(f"""
    <div style="
        background-color:#2E8B57;
        color:white;
        padding:12px 16px;
        border-radius:10px;
        font-weight:700;
        font-size:15px;
        margin-top:10px;
        margin-bottom:10px;
        width:fit-content;
        min-width:420px;
        max-width:700px;
        box-shadow:0px 2px 6px rgba(0,0,0,0.2);
    ">
        ✓ &nbsp; {tekst}
    </div>
    """, unsafe_allow_html=True)


# =================================================================================
# DOWNLOAD BUTTON
# =================================================================================

st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

if st.button("Download je ingevulde pool", key="download_pool"):

    if not user:
        toon_error_bericht(
            "Vul eerst je naam in voordat je je pool downloadt."
        )

    elif not alles_ingevuld():
        toon_error_bericht(
            "Zorg dat je alle wedstrijden en bonusvragen hebt ingevuld voordat je je pool downloadt."
        )

    else:
        pdf_buffer = maak_pool_pdf(user, voorspellingen_pdf)

        st.download_button(
            label="Klik hier om je PDF te downloaden",
            data=pdf_buffer,
            file_name=f"WK_Poule_2026_{user}.pdf",
            mime="application/pdf",
            key="download_pdf_final"
        )


# =================================================================================
# OPSLAAN BUTTON
# =================================================================================

if st.button("Opslaan en versturen", key="save_all"):

    if not user:
        toon_error_bericht(
            "Vul eerst je naam in voordat je je pool opslaat."
        )

    elif not alles_ingevuld():
        toon_error_bericht(
            "Zorg dat je alle wedstrijden en bonusvragen hebt ingevuld voordat je je pool opslaat."
        )

    else:

        # =========================================================================
        # POULEFASE OPSLAAN
        # =========================================================================

        for poule in poules.values():
            for wedstrijd in poule:
                match_id = wedstrijd["match_id"]

                db.collection("toto").document(
                    f"{user}_{match_id}"
                ).set({
                    "Deelnemer": user,
                    "Fase": "Poule",
                    "match_id": match_id,
                    "home_team": wedstrijd["home_team"],
                    "away_team": wedstrijd["away_team"],
                    "home_score": st.session_state.get(f"{match_id}_home"),
                    "away_score": st.session_state.get(f"{match_id}_away"),
                    "ingediend_op": firestore.SERVER_TIMESTAMP
                })


        # =========================================================================
        # 16E FINALE OPSLAAN
        # =========================================================================

        save_used_thirds = set()

        for i, match in enumerate(matches):
            match_id = match_number_map[i]

            db.collection("toto").document(
                f"{user}_16e_{match_id}"
            ).set({
                "Deelnemer": user,
                "Fase": "16e Finale",
                "match_id": match_id,
                "home_team": resolve_team(match[0], save_used_thirds),
                "away_team": resolve_team(match[1], save_used_thirds),
                "home_score": st.session_state.get(f"{match_id}_home"),
                "away_score": st.session_state.get(f"{match_id}_away"),
                "ingediend_op": firestore.SERVER_TIMESTAMP
            })


        # =========================================================================
        # 8E FINALE OPSLAAN
        # =========================================================================

        for match in eighth_matches:
            match_id = match[2]

            db.collection("toto").document(
                f"{user}_8e_{match_id}"
            ).set({
                "Deelnemer": user,
                "Fase": "8e Finale",
                "match_id": match_id,
                "home_team": resolve_eighth_team(match[0]),
                "away_team": resolve_eighth_team(match[1]),
                "home_score": st.session_state.get(f"eighth_home_{match_id}"),
                "away_score": st.session_state.get(f"eighth_away_{match_id}"),
                "ingediend_op": firestore.SERVER_TIMESTAMP
            })


        # =========================================================================
        # KWARTFINALE OPSLAAN
        # =========================================================================

        for match in quarter_matches:
            match_id = match[2]

            db.collection("toto").document(
                f"{user}_qf_{match_id}"
            ).set({
                "Deelnemer": user,
                "Fase": "Kwartfinale",
                "match_id": match_id,
                "home_team": resolve_quarter_team(match[0]),
                "away_team": resolve_quarter_team(match[1]),
                "home_score": st.session_state.get(f"qf_home_{match_id}"),
                "away_score": st.session_state.get(f"qf_away_{match_id}"),
                "ingediend_op": firestore.SERVER_TIMESTAMP
            })


        # =========================================================================
        # HALVE FINALE OPSLAAN
        # =========================================================================

        for match in semi_matches:
            match_id = match[2]

            db.collection("toto").document(
                f"{user}_sf_{match_id}"
            ).set({
                "Deelnemer": user,
                "Fase": "Halve finale",
                "match_id": match_id,
                "home_team": resolve_semi_team(match[0]),
                "away_team": resolve_semi_team(match[1]),
                "home_score": st.session_state.get(f"sf_home_{match_id}"),
                "away_score": st.session_state.get(f"sf_away_{match_id}"),
                "ingediend_op": firestore.SERVER_TIMESTAMP
            })


        # =========================================================================
        # FINALE OPSLAAN
        # =========================================================================

        for match in final_matches:
            match_id = match[2]

            db.collection("toto").document(
                f"{user}_final_{match_id}"
            ).set({
                "Deelnemer": user,
                "Fase": "Finale",
                "match_id": match_id,
                "home_team": resolve_final_team(match[0]),
                "away_team": resolve_final_team(match[1]),
                "home_score": st.session_state.get(f"final_home_{match_id}"),
                "away_score": st.session_state.get(f"final_away_{match_id}"),
                "ingediend_op": firestore.SERVER_TIMESTAMP
            })


        # =========================================================================
        # BONUSVRAGEN OPSLAAN
        # =========================================================================

        bonus_doc_id = normalize_text(user).replace(" ", "_")

        db.collection("bonusvragen").document(
            bonus_doc_id
        ).set({
            "Deelnemer": user,
            "gele_kaarten": st.session_state.get("bonus_gele_kaarten"),
            "rode_kaarten": st.session_state.get("bonus_rode_kaarten"),
            "doelpunten": st.session_state.get("bonus_doelpunten"),
            "topscorer": st.session_state.get("bonus_topscorer"),
            "ingediend_op": firestore.SERVER_TIMESTAMP
        })


        # =========================================================================
        # SUCCESMELDING
        # =========================================================================

        toon_success_bericht("Alle voorspellingen opgeslagen!")
