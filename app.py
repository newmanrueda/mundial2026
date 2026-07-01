from flask import Flask, render_template, request, jsonify, session, Response
import json
import os

app = Flask(__name__)
app.secret_key = 'mundial2026-panini-secret'

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
ADMIN_PASSWORD = "panini2026"

# ── Data Persistence ──────────────────────────────────────────────────────────

DEFAULT_GROUPS = {
    "A": {"teams": ["MEX", "RSA", "KOR", "CZE"], "host": "MEX",
          "results": {"MEX": {"w":3,"d":0,"l":0,"gf":6,"ga":0},
                      "RSA": {"w":1,"d":1,"l":1,"gf":2,"ga":3},
                      "KOR": {"w":1,"d":0,"l":2,"gf":2,"ga":3},
                      "CZE": {"w":0,"d":1,"l":2,"gf":2,"ga":6}},
          "advance": [1,2]},
    "B": {"teams": ["SUI", "CAN", "BIH", "QAT"], "host": "CAN",
          "results": {"SUI": {"w":2,"d":1,"l":0,"gf":7,"ga":3},
                      "CAN": {"w":1,"d":1,"l":1,"gf":8,"ga":3},
                      "BIH": {"w":1,"d":1,"l":1,"gf":5,"ga":6},
                      "QAT": {"w":0,"d":1,"l":2,"gf":2,"ga":10}},
          "advance": [1,2,3]},
    "C": {"teams": ["BRA", "MAR", "SCO", "HAI"], "host": None,
          "results": {"BRA": {"w":2,"d":1,"l":0,"gf":7,"ga":1},
                      "MAR": {"w":2,"d":1,"l":0,"gf":6,"ga":3},
                      "SCO": {"w":1,"d":0,"l":2,"gf":1,"ga":4},
                      "HAI": {"w":0,"d":0,"l":3,"gf":2,"ga":8}},
          "advance": [1,2]},
    "D": {"teams": ["USA", "AUS", "PAR", "TUR"], "host": "USA",
          "results": {"USA": {"w":2,"d":0,"l":1,"gf":8,"ga":4},
                      "AUS": {"w":1,"d":1,"l":1,"gf":2,"ga":2},
                      "PAR": {"w":1,"d":1,"l":1,"gf":2,"ga":4},
                      "TUR": {"w":1,"d":0,"l":2,"gf":3,"ga":5}},
          "advance": [1,2,3]},
    "E": {"teams": ["GER", "CIV", "ECU", "CUW"], "host": None,
          "results": {"GER": {"w":2,"d":0,"l":1,"gf":10,"ga":4},
                      "CIV": {"w":2,"d":0,"l":1,"gf":4,"ga":2},
                      "ECU": {"w":1,"d":1,"l":1,"gf":2,"ga":2},
                      "CUW": {"w":0,"d":1,"l":2,"gf":1,"ga":9}},
          "advance": [1,2,3]},
    "F": {"teams": ["NED", "JPN", "SWE", "TUN"], "host": None,
          "results": {"NED": {"w":2,"d":1,"l":0,"gf":10,"ga":4},
                      "JPN": {"w":1,"d":2,"l":0,"gf":7,"ga":3},
                      "SWE": {"w":1,"d":1,"l":1,"gf":7,"ga":7},
                      "TUN": {"w":0,"d":0,"l":3,"gf":2,"ga":12}},
          "advance": [1,2,3]},
    "G": {"teams": ["BEL", "EGY", "IRN", "NZL"], "host": None,
          "results": {"BEL": {"w":1,"d":2,"l":0,"gf":6,"ga":2},
                      "EGY": {"w":1,"d":2,"l":0,"gf":5,"ga":3},
                      "IRN": {"w":0,"d":3,"l":0,"gf":3,"ga":3},
                      "NZL": {"w":0,"d":1,"l":2,"gf":4,"ga":10}},
          "advance": [1,2]},
    "H": {"teams": ["ESP", "CPV", "URU", "KSA"], "host": None,
          "results": {"ESP": {"w":2,"d":1,"l":0,"gf":5,"ga":0},
                      "CPV": {"w":0,"d":3,"l":0,"gf":2,"ga":2},
                      "URU": {"w":0,"d":2,"l":1,"gf":3,"ga":4},
                      "KSA": {"w":0,"d":2,"l":1,"gf":1,"ga":5}},
          "advance": [1,2]},
    "I": {"teams": ["FRA", "NOR", "SEN", "IRQ"], "host": None,
          "results": {"FRA": {"w":3,"d":0,"l":0,"gf":10,"ga":2},
                      "NOR": {"w":2,"d":0,"l":1,"gf":8,"ga":7},
                      "SEN": {"w":1,"d":0,"l":2,"gf":8,"ga":6},
                      "IRQ": {"w":0,"d":0,"l":3,"gf":1,"ga":12}},
          "advance": [1,2,3]},
    "J": {"teams": ["ARG", "AUT", "ALG", "JOR"], "host": None,
          "results": {"ARG": {"w":3,"d":0,"l":0,"gf":8,"ga":1},
                      "AUT": {"w":1,"d":1,"l":1,"gf":6,"ga":6},
                      "ALG": {"w":1,"d":1,"l":1,"gf":5,"ga":7},
                      "JOR": {"w":0,"d":0,"l":3,"gf":3,"ga":8}},
          "advance": [1,2,3]},
    "K": {"teams": ["COL", "POR", "COD", "UZB"], "host": None,
          "results": {"COL": {"w":2,"d":1,"l":0,"gf":4,"ga":1},
                      "POR": {"w":1,"d":2,"l":0,"gf":6,"ga":1},
                      "COD": {"w":1,"d":1,"l":1,"gf":4,"ga":3},
                      "UZB": {"w":0,"d":0,"l":3,"gf":2,"ga":11}},
          "advance": [1,2,3]},
    "L": {"teams": ["ENG", "CRO", "GHA", "PAN"], "host": None,
          "results": {"ENG": {"w":2,"d":1,"l":0,"gf":6,"ga":2},
                      "CRO": {"w":2,"d":0,"l":1,"gf":5,"ga":5},
                      "GHA": {"w":1,"d":1,"l":1,"gf":2,"ga":2},
                      "PAN": {"w":0,"d":0,"l":3,"gf":0,"ga":4}},
          "advance": [1,2,3]}
}

DEFAULT_BRACKET = {
    "round_of_32": [
        {"id":"r32_1","team1":"GER","team2":"PAR","score1":1,"score2":1,"pens1":3,"pens2":4,"date":"Jun 29","time":"","venue":"Foxborough","status":"done"},
        {"id":"r32_2","team1":"FRA","team2":"SWE","score1":3,"score2":0,"date":"Jun 30","time":"","venue":"East Rutherford","status":"done"},
        {"id":"r32_3","team1":"RSA","team2":"CAN","score1":0,"score2":1,"date":"Jun 28","time":"","venue":"Inglewood","status":"done"},
        {"id":"r32_4","team1":"NED","team2":"MAR","score1":1,"score2":1,"pens1":2,"pens2":3,"date":"Jun 29","time":"","venue":"Guadalupe","status":"done"},
        {"id":"r32_5","team1":"POR","team2":"CRO","score1":None,"score2":None,"date":"Jul 2","time":"6:00pm ET","venue":"Toronto","status":"upcoming"},
        {"id":"r32_6","team1":"ESP","team2":"AUT","score1":None,"score2":None,"date":"Jul 2","time":"2:00pm ET","venue":"Inglewood","status":"upcoming"},
        {"id":"r32_7","team1":"USA","team2":"BIH","score1":None,"score2":None,"date":"Jul 1","time":"7:00pm ET","venue":"Santa Clara","status":"upcoming"},
        {"id":"r32_8","team1":"BEL","team2":"SEN","score1":None,"score2":None,"date":"Jul 1","time":"3:00pm ET","venue":"Seattle","status":"upcoming"},
        {"id":"r32_9","team1":"BRA","team2":"JPN","score1":2,"score2":1,"date":"Jun 29","time":"","venue":"Houston","status":"done"},
        {"id":"r32_10","team1":"CIV","team2":"NOR","score1":1,"score2":2,"date":"Jun 30","time":"","venue":"Arlington","status":"done"},
        {"id":"r32_11","team1":"MEX","team2":"ECU","score1":2,"score2":0,"date":"Jun 30","time":"","venue":"Mexico City","status":"done"},
        {"id":"r32_12","team1":"ENG","team2":"COD","score1":None,"score2":None,"date":"Jul 1","time":"11:00am ET","venue":"Atlanta","status":"upcoming"},
        {"id":"r32_13","team1":"ARG","team2":"CPV","score1":None,"score2":None,"date":"Jul 3","time":"5:00pm ET","venue":"Miami Gardens","status":"upcoming"},
        {"id":"r32_14","team1":"AUS","team2":"EGY","score1":None,"score2":None,"date":"Jul 3","time":"1:00pm ET","venue":"Arlington","status":"upcoming"},
        {"id":"r32_15","team1":"SUI","team2":"ALG","score1":None,"score2":None,"date":"Jul 2","time":"10:00pm ET","venue":"Vancouver","status":"upcoming"},
        {"id":"r32_16","team1":"COL","team2":"GHA","score1":None,"score2":None,"date":"Jul 3","time":"8:30pm ET","venue":"Kansas City","status":"upcoming"}
    ],
    "round_of_16": [
        {"id":"r16_1","team1":"PAR","team2":"FRA","score1":None,"score2":None,"date":"Jul 4","time":"4:00pm ET","venue":"Philadelphia","status":"upcoming","from":["r32_1","r32_2"]},
        {"id":"r16_2","team1":"CAN","team2":"MAR","score1":None,"score2":None,"date":"Jul 4","time":"12:00pm ET","venue":"Houston","status":"upcoming","from":["r32_3","r32_4"]},
        {"id":"r16_3","team1":"W83","team2":"W84","score1":None,"score2":None,"date":"Jul 6","time":"","venue":"Arlington","status":"waiting","from":["r32_5","r32_6"]},
        {"id":"r16_4","team1":"W81","team2":"W82","score1":None,"score2":None,"date":"Jul 6","time":"","venue":"Seattle","status":"waiting","from":["r32_7","r32_8"]},
        {"id":"r16_5","team1":"BRA","team2":"NOR","score1":None,"score2":None,"date":"Jul 5","time":"3:00pm ET","venue":"East Rutherford","status":"upcoming","from":["r32_9","r32_10"]},
        {"id":"r16_6","team1":"MEX","team2":"W80","score1":None,"score2":None,"date":"Jul 6","time":"8:00pm ET","venue":"Mexico City","status":"waiting","from":["r32_11","r32_12"]},
        {"id":"r16_7","team1":"W86","team2":"W88","score1":None,"score2":None,"date":"Jul 7","time":"5:00pm ET","venue":"Atlanta","status":"waiting","from":["r32_13","r32_16"]},
        {"id":"r16_8","team1":"W85","team2":"W87","score1":None,"score2":None,"date":"Jul 7","time":"9:00pm ET","venue":"Vancouver","status":"waiting","from":["r32_14","r32_15"]}
    ],
    "quarterfinals": [
        {"id":"qf1","team1":"W89","team2":"W90","score1":None,"score2":None,"date":"Jul 9","venue":"Foxborough","status":"waiting","from":["r16_1","r16_2"]},
        {"id":"qf2","team1":"W93","team2":"W94","score1":None,"score2":None,"date":"Jul 10","venue":"Inglewood","status":"waiting","from":["r16_3","r16_4"]},
        {"id":"qf3","team1":"W91","team2":"W92","score1":None,"score2":None,"date":"Jul 11","venue":"Miami Gardens","status":"waiting","from":["r16_5","r16_6"]},
        {"id":"qf4","team1":"W95","team2":"W96","score1":None,"score2":None,"date":"Jul 11","venue":"Kansas City","status":"waiting","from":["r16_7","r16_8"]}
    ],
    "semifinals": [
        {"id":"sf1","team1":"W97","team2":"W98","score1":None,"score2":None,"date":"Jul 14","venue":"Arlington","status":"waiting","from":["qf1","qf2"]},
        {"id":"sf2","team1":"W99","team2":"W100","score1":None,"score2":None,"date":"Jul 15","venue":"Atlanta","status":"waiting","from":["qf3","qf4"]}
    ],
    "final": [
        {"id":"final","team1":"W101","team2":"W102","score1":None,"score2":None,"date":"Jul 19","venue":"East Rutherford","status":"waiting","from":["sf1","sf2"]},
        {"id":"third","team1":"L101","team2":"L102","score1":None,"score2":None,"date":"Jul 18","venue":"Miami Gardens","status":"waiting","from":["sf1","sf2"]}
    ]
}

DEFAULT_GOALSCORERS = [
    ("Lionel Messi", "ARG", 6),
    ("Kylian Mbappé", "FRA", 6),
    ("Erling Haaland", "NOR", 5),
    ("Vinícius Júnior", "BRA", 4),
    ("Ousmane Dembélé", "FRA", 4),
    ("Cristiano Ronaldo", "POR", 4),
    ("Brian Brobbey", "NED", 3),
    ("Deniz Undav", "GER", 3),
    ("Elijah Just", "NZL", 3),
    ("Ismael Saibari", "MAR", 3),
    ("Ismaïla Sarr", "SEN", 3),
    ("Matheus Cunha", "BRA", 3),
    ("Jonathan David", "CAN", 3),
    ("Harry Kane", "ENG", 3),
    ("Kai Havertz", "GER", 3),
    ("Cody Gakpo", "NED", 3),
    ("Yoane Wissa", "COD", 3),
    ("Johan Manzambi", "SUI", 3),
    ("Luis Díaz", "COL", 3),
    ("Riyad Mahrez", "ALG", 2),
    ("Marko Arnautović", "AUT", 2),
    ("Leandro Trossard", "BEL", 2),
    ("Ermin Mahmić", "BIH", 2),
    ("Daniel Muñoz", "COL", 2),
    ("Cyle Larin", "CAN", 2),
    ("Jude Bellingham", "ENG", 2),
    ("Daichi Kamada", "JPN", 2),
    ("Ayase Ueda", "JPN", 2),
    ("Julián Quiñones", "MEX", 2),
    ("Crysencio Summerville", "NED", 2),
    ("Mikel Oyarzabal", "ESP", 2),
    ("Anthony Elanga", "SWE", 2),
    ("Rubén Vargas", "SUI", 2),
    ("Pape Gueye", "SEN", 2),
    ("Nicolas Pépé", "CIV", 2),
    ("Folarin Balogun", "USA", 2),
    ("Alejandro Garnacho", "ARG", 1),
    ("Bruno Fernandes", "POR", 1),
    ("Bukayo Saka", "ENG", 2),
    ("Jamal Musiala", "GER", 1),
    ("Lautaro Martínez", "ARG", 1),
    ("Giovani Lo Celso", "ARG", 1),
]

DEFAULT_CARDS = {
    "MEX": {"y": 8, "r": 1}, "RSA": {"y": 6, "r": 2}, "KOR": {"y": 4, "r": 0},
    "CZE": {"y": 5, "r": 0}, "SUI": {"y": 4, "r": 0}, "CAN": {"y": 5, "r": 0},
    "BIH": {"y": 7, "r": 1}, "QAT": {"y": 9, "r": 1}, "BRA": {"y": 3, "r": 0},
    "MAR": {"y": 6, "r": 0}, "SCO": {"y": 4, "r": 0}, "HAI": {"y": 5, "r": 0},
    "USA": {"y": 5, "r": 0}, "AUS": {"y": 6, "r": 1}, "PAR": {"y": 8, "r": 0},
    "TUR": {"y": 7, "r": 1}, "GER": {"y": 4, "r": 1}, "CIV": {"y": 5, "r": 0},
    "ECU": {"y": 6, "r": 0}, "CUW": {"y": 4, "r": 0}, "NED": {"y": 4, "r": 0},
    "JPN": {"y": 3, "r": 0}, "SWE": {"y": 5, "r": 0}, "TUN": {"y": 6, "r": 0},
    "BEL": {"y": 4, "r": 0}, "EGY": {"y": 5, "r": 0}, "IRN": {"y": 7, "r": 0},
    "NZL": {"y": 8, "r": 0}, "ESP": {"y": 3, "r": 0}, "CPV": {"y": 5, "r": 0},
    "URU": {"y": 6, "r": 0}, "KSA": {"y": 7, "r": 0}, "FRA": {"y": 4, "r": 0},
    "NOR": {"y": 5, "r": 0}, "SEN": {"y": 6, "r": 0}, "IRQ": {"y": 8, "r": 1},
    "ARG": {"y": 3, "r": 0}, "AUT": {"y": 5, "r": 0}, "ALG": {"y": 6, "r": 0},
    "JOR": {"y": 7, "r": 0}, "COL": {"y": 5, "r": 0}, "POR": {"y": 4, "r": 1},
    "COD": {"y": 6, "r": 0}, "UZB": {"y": 7, "r": 0}, "ENG": {"y": 3, "r": 0},
    "CRO": {"y": 5, "r": 0}, "GHA": {"y": 6, "r": 0}, "PAN": {"y": 8, "r": 0},
}

# ── Load/Save Data ──────────────────────────────────────────────────────────

def load_data():
    # Try loading from env var first (Render env variable fallback)
    backup_b64 = os.environ.get('DATA_BACKUP', '')
    if backup_b64:
        try:
            import base64
            decoded = base64.b64decode(backup_b64).decode()
            saved = json.loads(decoded)
            groups = saved.get('groups', DEFAULT_GROUPS)
            bracket = saved.get('bracket', DEFAULT_BRACKET)
            goalscorers = saved.get('goalscorers', DEFAULT_GOALSCORERS)
            cards = saved.get('cards', DEFAULT_CARDS)
            goalscorers = [tuple(g) for g in goalscorers]
            # Also write to file for subsequent loads
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(saved, f, ensure_ascii=False, indent=2)
            return groups, bracket, goalscorers, cards
        except Exception:
            pass

    # Try local file
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            groups = saved.get('groups', DEFAULT_GROUPS)
            bracket = saved.get('bracket', DEFAULT_BRACKET)
            goalscorers = saved.get('goalscorers', DEFAULT_GOALSCORERS)
            cards = saved.get('cards', DEFAULT_CARDS)
            goalscorers = [tuple(g) for g in goalscorers]
            return groups, bracket, goalscorers, cards
        except (json.JSONDecodeError, KeyError):
            pass
    return DEFAULT_GROUPS, DEFAULT_BRACKET, DEFAULT_GOALSCORERS, DEFAULT_CARDS

def save_data():
    global GROUPS, BRACKET, GOALSCORERS, CARDS
    data = {
        'groups': GROUPS,
        'bracket': BRACKET,
        'goalscorers': GOALSCORERS,
        'cards': CARDS,
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Initialize ──────────────────────────────────────────────────────────────

GROUPS, BRACKET, GOALSCORERS, CARDS = load_data()

# ── Static Data ──────────────────────────────────────────────────────────────

TEAM_NAMES = {
    "MEX":"México","RSA":"Sudáfrica","KOR":"Corea del Sur","CZE":"Rep.Checa",
    "SUI":"Suiza","CAN":"Canadá","BIH":"Bosnia","QAT":"Qatar",
    "BRA":"Brasil","MAR":"Marruecos","SCO":"Escocia","HAI":"Haití",
    "USA":"EE.UU.","AUS":"Australia","PAR":"Paraguay","TUR":"Turquía",
    "GER":"Alemania","CIV":"Costa de Marfil","ECU":"Ecuador","CUW":"Curazao",
    "NED":"Países Bajos","JPN":"Japón","SWE":"Suecia","TUN":"Túnez",
    "BEL":"Bélgica","EGY":"Egipto","IRN":"Irán","NZL":"N.Zelanda",
    "ESP":"España","CPV":"Cabo Verde","URU":"Uruguay","KSA":"Arabia Saudí",
    "FRA":"Francia","NOR":"Noruega","SEN":"Senegal","IRQ":"Irak",
    "ARG":"Argentina","AUT":"Austria","ALG":"Argelia","JOR":"Jordania",
    "COL":"Colombia","POR":"Portugal","COD":"R.D.Congo","UZB":"Uzbekistán",
    "ENG":"Inglaterra","CRO":"Croacia","GHA":"Ghana","PAN":"Panamá"
}

TEAM_FLAGS = {
    "MEX":"🇲🇽","RSA":"🇿🇦","KOR":"🇰🇷","CZE":"🇨🇿",
    "SUI":"🇨🇭","CAN":"🇨🇦","BIH":"🇧🇦","QAT":"🇶🇦",
    "BRA":"🇧🇷","MAR":"🇲🇦","SCO":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","HAI":"🇭🇹",
    "USA":"🇺🇸","AUS":"🇦🇺","PAR":"🇵🇾","TUR":"🇹🇷",
    "GER":"🇩🇪","CIV":"🇨🇮","ECU":"🇪🇨","CUW":"🇨🇼",
    "NED":"🇳🇱","JPN":"🇯🇵","SWE":"🇸🇪","TUN":"🇹🇳",
    "BEL":"🇧🇪","EGY":"🇪🇬","IRN":"🇮🇷","NZL":"🇳🇿",
    "ESP":"🇪🇸","CPV":"🇨🇻","URU":"🇺🇾","KSA":"🇸🇦",
    "FRA":"🇫🇷","NOR":"🇳🇴","SEN":"🇸🇳","IRQ":"🇮🇶",
    "ARG":"🇦🇷","AUT":"🇦🇹","ALG":"🇩🇿","JOR":"🇯🇴",
    "COL":"🇨🇴","POR":"🇵🇹","COD":"🇨🇩","UZB":"🇺🇿",
    "ENG":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","CRO":"🇭🇷","GHA":"🇬🇭","PAN":"🇵🇦"
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_winner(match):
    if match.get("status") == "done":
        s1 = match.get("score1")
        s2 = match.get("score2")
        p1 = match.get("pens1")
        p2 = match.get("pens2")
        if s1 is not None and s2 is not None:
            if s1 == s2 and p1 is not None and p2 is not None:
                return match["team1"] if p1 > p2 else match["team2"]
            elif s1 > s2:
                return match["team1"]
            elif s2 > s1:
                return match["team2"]
    return None

def update_bracket():
    winner_map = {}
    loser_map = {}
    for round_name in ["round_of_32", "round_of_16", "quarterfinals", "semifinals", "final"]:
        for match in BRACKET[round_name]:
            mid = match["id"]
            w = get_winner(match)
            if w:
                winner_map[mid] = w
                loser_map[mid] = match["team2"] if match["team1"] == w else match["team1"]
    for round_name in ["round_of_16", "quarterfinals", "semifinals", "final"]:
        for match in BRACKET[round_name]:
            if "from" in match and len(match["from"]) == 2:
                src1, src2 = match["from"]
                w1, w2 = winner_map.get(src1), winner_map.get(src2)
                l1, l2 = loser_map.get(src1), loser_map.get(src2)
                refs = ["W77","W78","W79","W80","W81","W82","W83","W84",
                        "W85","W86","W87","W88","W89","W90","W91","W92",
                        "W93","W94","W95","W96","W97","W98","W99","W100",
                        "W101","W102","L101","L102","TBD","TBD2"]
                if match["team1"] in refs:
                    if match["team1"].startswith("W") and w1:
                        match["team1"] = w1
                    elif match["team1"].startswith("L") and l1:
                        match["team1"] = l1
                if match["team2"] in refs:
                    if match["team2"].startswith("W") and w2:
                        match["team2"] = w2
                    elif match["team2"].startswith("L") and l2:
                        match["team2"] = l2

def sort_group_teams(group):
    teams = group['teams']
    def sort_key(code):
        r = group['results'][code]
        pts = r['w']*3 + r['d']
        gd = r['gf'] - r['ga']
        return (-pts, -gd, -r['gf'])
    return sorted(teams, key=sort_key)

def compute_clean_sheets():
    clean = {}
    for letter, group in GROUPS.items():
        for code in group['teams']:
            r = group['results'][code]
            clean[code] = r['ga'] == 0
    return clean

# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/api/auth', methods=['POST'])
def admin_auth():
    data = request.json
    if data.get('password') == ADMIN_PASSWORD:
        session['admin'] = True
        session.permanent = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Contraseña incorrecta'}), 401

@app.route('/api/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return jsonify({'success': True})

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    sorted_groups = {}
    for letter, group in GROUPS.items():
        sorted_groups[letter] = dict(group)
        sorted_groups[letter]['sorted_teams'] = sort_group_teams(group)
    sorted_gs = sorted(GOALSCORERS, key=lambda x: -x[2])
    return render_template('index.html', groups=GROUPS, sorted_groups=sorted_groups,
                         goalscorers=sorted_gs, teams=TEAM_NAMES, flags=TEAM_FLAGS,
                         is_admin=session.get('admin', False))

@app.route('/groups')
def groups():
    sorted_groups = {}
    for letter, group in GROUPS.items():
        sorted_groups[letter] = dict(group)
        sorted_groups[letter]['sorted_teams'] = sort_group_teams(group)
    return render_template('groups.html', groups=GROUPS, sorted_groups=sorted_groups,
                         teams=TEAM_NAMES, flags=TEAM_FLAGS,
                         is_admin=session.get('admin', False))

@app.route('/bracket')
def bracket():
    update_bracket()
    return render_template('bracket.html', bracket=BRACKET, teams=TEAM_NAMES, flags=TEAM_FLAGS,
                         is_admin=session.get('admin', False))

@app.route('/stats')
def stats():
    sorted_groups_stats = {}
    for letter, group in GROUPS.items():
        sorted_groups_stats[letter] = dict(group)
        sorted_groups_stats[letter]['sorted_teams'] = sort_group_teams(group)
    sorted_gs = sorted(GOALSCORERS, key=lambda x: -x[2])
    gs_by_team = {}
    for name, team, goals in GOALSCORERS:
        if team not in gs_by_team:
            gs_by_team[team] = []
        gs_by_team[team].append((name, goals))
    clean_sheets = compute_clean_sheets()
    return render_template('stats.html',
                         goalscorers=sorted_gs,
                         gs_by_team=gs_by_team,
                         cards=CARDS,
                         clean_sheets=clean_sheets,
                         groups=GROUPS,
                         sorted_groups=sorted_groups_stats,
                         teams=TEAM_NAMES,
                         flags=TEAM_FLAGS,
                         is_admin=session.get('admin', False))

# ── API: Update Bracket Scores ──────────────────────────────────────────────

@app.route('/api/update_score', methods=['POST'])
def update_score():
    if not session.get('admin'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    data = request.json
    round_name = data.get('round')
    match_id = data.get('match_id')
    score1 = data.get('score1')
    score2 = data.get('score2')
    pens1 = data.get('pens1')
    pens2 = data.get('pens2')
    if round_name in BRACKET:
        for match in BRACKET[round_name]:
            if match['id'] == match_id:
                match['score1'] = score1
                match['score2'] = score2
                match['pens1'] = pens1
                match['pens2'] = pens2
                if score1 is not None and score2 is not None:
                    match['status'] = 'done'
                save_data()
                # Return the full bracket so frontend can save to localStorage
                return jsonify({'success': True, 'bracket': BRACKET})
    return jsonify({'success': False, 'error': 'Match not found'}), 404

@app.route('/api/reset_match', methods=['POST'])
def reset_match():
    if not session.get('admin'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    data = request.json
    round_name = data.get('round')
    match_id = data.get('match_id')
    if round_name in BRACKET:
        for match in BRACKET[round_name]:
            if match['id'] == match_id:
                match['score1'] = None
                match['score2'] = None
                match['pens1'] = None
                match['pens2'] = None
                match['status'] = 'upcoming' if 'r32' in match_id else 'waiting'
                save_data()
                return jsonify({'success': True, 'bracket': BRACKET})
    return jsonify({'success': False, 'error': 'Match not found'}), 404

# ── API: Update Group Results ──────────────────────────────────────────────

@app.route('/api/update_group', methods=['POST'])
def update_group():
    if not session.get('admin'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    data = request.json
    group_letter = data.get('group')
    team_code = data.get('team')
    field = data.get('field')
    value = data.get('value')
    if group_letter in GROUPS and team_code in GROUPS[group_letter]['results']:
        if field in ('w', 'd', 'l', 'gf', 'ga'):
            GROUPS[group_letter]['results'][team_code][field] = int(value)
            save_data()
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid data'}), 400

# ── API: Export / Import ────────────────────────────────────────────────────

@app.route('/api/export')
def export_data():
    """Returns all data as downloadable JSON file."""
    data = {
        'groups': GROUPS,
        'bracket': BRACKET,
        'goalscorers': GOALSCORERS,
        'cards': CARDS,
        'exported_at': __import__('datetime').datetime.now().isoformat()
    }
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return Response(
        json_str,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=mundial2026_backup.json'}
    )

@app.route('/api/import', methods=['POST'])
def import_data():
    if not session.get('admin'):
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    global GROUPS, BRACKET, GOALSCORERS, CARDS
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    GROUPS = data.get('groups', GROUPS)
    BRACKET = data.get('bracket', BRACKET)
    gs = data.get('goalscorers', GOALSCORERS)
    GOALSCORERS = [tuple(g) if isinstance(g, list) else g for g in gs]
    CARDS = data.get('cards', CARDS)
    save_data()
    return jsonify({'success': True, 'message': f'Datos importados correctamente'})

@app.route('/api/current_bracket')
def current_bracket():
    """Returns current bracket data for localStorage sync."""
    update_bracket()
    return jsonify({'bracket': BRACKET})

# ── Admin Status ──────────────────────────────────────────────────────────

@app.route('/api/admin_status')
def admin_status():
    return jsonify({'admin': session.get('admin', False)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
