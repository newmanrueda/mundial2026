#!/usr/bin/env python3
"""
Tribuna 10 Sport — Auto-Updater via ESPN API
Se ejecuta cada 3 horas desde cron de Hermes.
No necesita Playwright ni navegador.
"""

import json, os, re, sys, urllib.request, base64
from datetime import datetime, timezone

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data.json')

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; Tribuna10Bot/1.0)'}

TEAM_MAP = {
    "MEX":"MEX","RSA":"RSA","KOR":"KOR","CZE":"CZE","SUI":"SUI",
    "CAN":"CAN","BIH":"BIH","QAT":"QAT","BRA":"BRA","MAR":"MAR",
    "SCO":"SCO","HAI":"HAI","USA":"USA","AUS":"AUS","PAR":"PAR",
    "TUR":"TUR","GER":"GER","CIV":"CIV","ECU":"ECU","CUW":"CUW",
    "NED":"NED","JPN":"JPN","SWE":"SWE","TUN":"TUN","BEL":"BEL",
    "EGY":"EGY","IRN":"IRN","NZL":"NZL","ESP":"ESP","CPV":"CPV",
    "URU":"URU","KSA":"KSA","FRA":"FRA","NOR":"NOR","SEN":"SEN",
    "IRQ":"IRQ","ARG":"ARG","AUT":"AUT","ALG":"ALG","JOR":"JOR",
    "COL":"COL","POR":"POR","COD":"COD","UZB":"UZB","ENG":"ENG",
    "CRO":"CRO","GHA":"GHA","PAN":"PAN",
}

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ⚠ {e}")
        return None

def get_team_code(abbr):
    """Map ESPN abbreviation to our code."""
    abbr_upper = abbr.upper().strip()
    # ESPN sometimes uses different abbreviations
    espn_map = {
        "RSA":"RSA","KOR":"KOR","MEX":"MEX","CZE":"CZE",
        "SUI":"SUI","CAN":"CAN","BIH":"BIH","QAT":"QAT",
        "BRA":"BRA","MAR":"MAR","SCO":"SCO","HAI":"HAI",
        "USA":"USA","AUS":"AUS","PAR":"PAR","TUR":"TUR",
        "GER":"GER","CIV":"CIV","ECU":"ECU","CUW":"CUW",
        "NED":"NED","JPN":"JPN","SWE":"SWE","TUN":"TUN",
        "BEL":"BEL","EGY":"EGY","IRN":"IRN","NZL":"NZL",
        "ESP":"ESP","CPV":"CPV","URU":"URU","KSA":"KSA",
        "FRA":"FRA","NOR":"NOR","SEN":"SEN","IRQ":"IRQ",
        "ARG":"ARG","AUT":"AUT","ALG":"ALG","JOR":"JOR",
        "COL":"COL","POR":"POR","COD":"COD","UZB":"UZB",
        "ENG":"ENG","CRO":"CRO","GHA":"GHA","PAN":"PAN",
    }
    return espn_map.get(abbr_upper, abbr_upper)

def fetch_scoreboard(date_str):
    """Fetch matches from ESPN API for a given date."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/FIFA.WORLD/scoreboard?dates={date_str}"
    return fetch_json(url)

def fetch_scorers():
    """Fetch top scorers from ESPN API."""
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/FIFA.WORLD/scoreboard?view=scoring"
    data = fetch_json(url)
    if not data:
        return None
    # ESPN doesn't have a simple scorers endpoint in this API
    # We'll get scorers from match data instead
    return None

def main():
    print(f"🔍 Tribuna 10 Auto-Updater")
    print(f"   {datetime.now().isoformat()}")
    print()
    
    # Load current data
    current = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            current = json.load(f)
    
    changed = False
    
    # Fetch last few days of matches
    from datetime import timedelta
    today = datetime.now(timezone.utc)
    
    for days_ago in range(7):
        d = today - timedelta(days=days_ago)
        date_str = d.strftime("%Y%m%d")
        print(f"📅 Fetching {date_str}...")
        
        data = fetch_scoreboard(date_str)
        if not data or 'events' not in data:
            continue
        
        events = data['events']
        if not events:
            continue
        
        for event in events:
            comps = event.get('competitions', [{}])[0]
            status = comps.get('status', {}).get('type', {}).get('name', '')
            
            if status not in ['STATUS_FINAL', 'STATUS_IN_PROGRESS']:
                continue
            
            competitors = comps.get('competitors', [])
            if len(competitors) < 2:
                continue
            
            home_team = competitors[0]
            away_team = competitors[1]
            
            home_code = get_team_code(home_team.get('team', {}).get('abbreviation', ''))
            away_code = get_team_code(away_team.get('team', {}).get('abbreviation', ''))
            
            home_score = home_team.get('score', '?')
            away_score = away_team.get('score', '?')
            
            print(f"  {home_code} {home_score}-{away_score} {away_code}")
            
            # Update bracket if match found
            bracket = current.get('bracket', {})
            r32 = bracket.get('round_of_32', [])
            for match in r32:
                if match['team1'] == home_code and match['team2'] == away_code:
                    old_s1, old_s2 = match.get('score1'), match.get('score2')
                    try:
                        s1 = int(home_score) if home_score not in ('?', '') else None
                        s2 = int(away_score) if away_score not in ('?', '') else None
                    except ValueError:
                        s1, s2 = None, None
                    
                    if s1 is not None and s2 is not None:
                        if old_s1 != s1 or old_s2 != s2:
                            match['score1'] = s1
                            match['score2'] = s2
                            match['status'] = 'done'
                            print(f"    ↪ BRACKET UPDATED: {s1}-{s2}")
                            changed = True
                    break
            
            # Extract cards data
            details = comps.get('details', [])
            home_id = home_team.get('id', '')
            
            yh, ya, rh, ra = 0, 0, 0, 0
            for d in details:
                d_type = d.get('type', {})
                if isinstance(d_type, dict):
                    t = d_type.get('text', '').lower()
                else:
                    t = str(d_type).lower()
                team_id = d.get('team', {}).get('id', '')
                is_home = team_id == home_id
                if 'yellow' in t:
                    if is_home: yh += 1
                    else: ya += 1
                elif 'red' in t:
                    if is_home: rh += 1
                    else: ra += 1
            
            if yh or ya or rh or ra:
                cards = current.get('cards', {})
                # Update cards - for now just track R32 additions
                # Group stage cards are embedded in defaults
                if home_code not in cards:
                    cards[home_code] = {"y": 0, "r": 0}
                if away_code not in cards:
                    cards[away_code] = {"y": 0, "r": 0}
                
                # Only add if new data > existing (handles incremental updates)
                old_h = cards[home_code]
                old_a = cards[away_code]
                
                # Track per-match additions separately
                r32_cards = current.get('r32_cards', {})
                match_key = f"{home_code}_{away_code}"
                
                new_rh = max(0, rh - old_h.get('r', 0))
                new_ra = max(0, ra - old_a.get('r', 0))
                
                if rh > old_h.get('r', 0) or ra > old_a.get('r', 0) or yh > 0 or ya > 0:
                    if match_key not in r32_cards.get(home_code, {}):
                        cards[home_code] = {"y": old_h.get('y', 0) + yh, "r": old_h.get('r', 0) + rh}
                        cards[away_code] = {"y": old_a.get('y', 0) + ya, "r": old_a.get('r', 0) + ra}
                        print(f"    ↪ CARDS: {home_code}+{yh}Y/{rh}R, {away_code}+{ya}Y/{ra}R")
                        changed = True
                        # Mark as processed
                        if 'r32_cards' not in current:
                            current['r32_cards'] = {}
                        if home_code not in current['r32_cards']:
                            current['r32_cards'][home_code] = {}
                        current['r32_cards'][home_code][match_key] = True
                        if away_code not in current['r32_cards']:
                            current['r32_cards'][away_code] = {}
                        current['r32_cards'][away_code][match_key] = True
    
    if changed:
        current['last_updated'] = datetime.now().isoformat()
        with open(DATA_FILE, 'w') as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Data updated! Changes detected.")
        # Git commit and push
        repo_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(repo_dir)
        os.system("git add data.json && git diff --cached --quiet || (git commit -m '🤖 Auto-update $(date -u +\"%Y-%m-%d %H:%M UTC\")' && git push)")
        return 0
    else:
        print(f"\n📡 No changes.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
