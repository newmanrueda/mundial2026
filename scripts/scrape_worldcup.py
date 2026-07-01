#!/usr/bin/env python3
"""
Tribuna 10 Sport — Scraper del Mundial 2026 (Playwright)
Se ejecuta en GitHub Actions con navegador headless.
Extrae goleadores y resultados desde BBC Sport.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json')

# ── Team name aliases ───────────────────────────────────────────────────────
TEAM_ALIASES = {
    "mexico": "MEX", "south africa": "RSA", "south korea": "KOR",
    "czech republic": "CZE", "czechia": "CZE",
    "switzerland": "SUI", "canada": "CAN",
    "bosnia and herzegovina": "BIH", "bosnia": "BIH",
    "qatar": "QAT",
    "brazil": "BRA", "morocco": "MAR",
    "scotland": "SCO", "haiti": "HAI",
    "usa": "USA", "united states": "USA",
    "australia": "AUS", "paraguay": "PAR", "turkey": "TUR",
    "germany": "GER", "ivory coast": "CIV", "côte d'ivoire": "CIV",
    "ecuador": "ECU", "curacao": "CUW", "curaçao": "CUW",
    "netherlands": "NED", "holland": "NED",
    "japan": "JPN", "sweden": "SWE", "tunisia": "TUN",
    "belgium": "BEL", "egypt": "EGY", "iran": "IRN",
    "new zealand": "NZL",
    "spain": "ESP", "cape verde": "CPV",
    "uruguay": "URU", "saudi arabia": "KSA",
    "france": "FRA", "norway": "NOR", "senegal": "SEN", "iraq": "IRQ",
    "argentina": "ARG", "austria": "AUT", "algeria": "ALG", "jordan": "JOR",
    "colombia": "COL", "portugal": "POR",
    "congo dr": "COD", "dr congo": "COD", "rd congo": "COD",
    "uzbekistan": "UZB",
    "england": "ENG", "croatia": "CRO", "ghana": "GHA", "panama": "PAN",
}

# Our 3-letter codes for all 48 teams
ALL_TEAMS = [
    "MEX","RSA","KOR","CZE","SUI","CAN","BIH","QAT","BRA","MAR","SCO","HAI",
    "USA","AUS","PAR","TUR","GER","CIV","ECU","CUW","NED","JPN","SWE","TUN",
    "BEL","EGY","IRN","NZL","ESP","CPV","URU","KSA","FRA","NOR","SEN","IRQ",
    "ARG","AUT","ALG","JOR","COL","POR","COD","UZB","ENG","CRO","GHA","PAN"
]


def match_team_code(team_name):
    """Match a team name to our 3-letter code, with fuzzy matching."""
    key = re.sub(r'[^a-z0-9]', '', team_name.strip().lower())
    if not key:
        return None
    # Direct match
    for alias, code in TEAM_ALIASES.items():
        ak = re.sub(r'[^a-z0-9]', '', alias)
        if ak == key:
            return code
    # Substring match
    for alias, code in TEAM_ALIASES.items():
        ak = re.sub(r'[^a-z0-9]', '', alias)
        if key in ak or ak in key:
            return code
    return None


def load_current():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_scorers_from_html(html):
    """Extract goalscorers from BBC rendered HTML."""
    scorers = []
    
    # BBC Sport uses a table with class containing 'gs-o-table'
    # Find all rows with scorer data
    # Pattern: <tr ...> <td>player</td> <td>team</td> <td>goals</td>
    
    # Try extracting from JSON within script tags
    scripts = re.findall(
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    if not scripts:
        scripts = re.findall(
            r'<script[^>]*id="__SPORT_DATA__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
    
    if scripts:
        try:
            data = json.loads(scripts[0])
            # Navigate the data structure
            # BBC data varies, let's search recursively
            def find_tables(obj, depth=0):
                if depth > 10:
                    return []
                results = []
                if isinstance(obj, dict):
                    if any(k in obj for k in ['rows', 'items', 'data']):
                        results.append(obj)
                    for v in obj.values():
                        results.extend(find_tables(v, depth+1))
                elif isinstance(obj, list):
                    for item in obj:
                        results.extend(find_tables(item, depth+1))
                return results
            
            tables = find_tables(data)
            for table in tables:
                rows = table.get('rows', table.get('items', table.get('data', [])))
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict):
                            cells = row.get('cells', row.get('columns', []))
                            if len(cells) >= 3:
                                player = None
                                team = None
                                goals = None
                                for cell in cells:
                                    if isinstance(cell, dict):
                                        val = cell.get('value', cell.get('text', ''))
                                        if isinstance(val, str):
                                            if player is None:
                                                player = val
                                            elif team is None and match_team_code(val):
                                                team = match_team_code(val)
                                            elif goals is None:
                                                try:
                                                    goals = int(val)
                                                except (ValueError, TypeError):
                                                    pass
                                if player and team and goals is not None:
                                    scorers.append((player.strip(), team, goals))
        except json.JSONDecodeError:
            pass
    
    return scorers


def scrape_bbc_scorers_playwright():
    """Scrape BBC top scorers using Playwright."""
    from playwright.sync_api import sync_playwright
    
    print("  🎭 Launching Playwright...", file=sys.stderr)
    scorers = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Fetch top scorers page
        print("  📊 Navigating to BBC Top Scorers...", file=sys.stderr)
        page.goto("https://www.bbc.com/sport/football/world-cup/top-scorers", wait_until="networkidle", timeout=30000)
        
        # Wait for table to load
        page.wait_for_timeout(3000)
        
        # Get full HTML
        html = page.content()
        
        # Try to extract from JSON data first
        scorers = extract_scorers_from_html(html)
        
        if not scorers:
            # Try extracting table data directly from DOM
            print("  🔍 Trying DOM extraction...", file=sys.stderr)
            rows = page.query_selector_all('table tr, [class*="gs-o-table__row"]')
            
            if not rows:
                # Try broader selectors
                rows = page.query_selector_all('[class*="table__row"], [class*="TableRow"], tr')
            
            if rows:
                for row in rows:
                    cells = row.query_selector_all('td, [class*="cell"]')
                    if len(cells) >= 3:
                        texts = [cell.inner_text().strip() for cell in cells]
                        # Check if any cell is a number (goals)
                        for i, t in enumerate(texts):
                            try:
                                goals = int(t)
                                # Found a goals column. Player is before, team is somewhere
                                player = texts[0] if i > 0 else "Unknown"
                                # Try to find team code
                                team_code = None
                                for t2 in texts:
                                    code = match_team_code(t2)
                                    if code:
                                        team_code = code
                                        break
                                if team_code:
                                    scorers.append((player, team_code, goals))
                                break
                            except ValueError:
                                pass
        
        # If DOM parsing fails, try evaluating JS in the page
        if not scorers:
            print("  🔍 Trying JavaScript extraction...", file=sys.stderr)
            # Try to get data from window.__INITIAL_STATE__ or similar
            data = page.evaluate("""() => {
                // Try various data containers
                for (const key of ['__INITIAL_STATE__', '__NEXT_DATA__', '__SPORT_DATA__', '__DATA__']) {
                    if (window[key]) return {source: key, data: JSON.stringify(window[key])};
                }
                // Try to find data in the DOM
                const scripts = document.querySelectorAll('script[type="application/json"]');
                for (const s of scripts) {
                    try {
                        const d = JSON.parse(s.textContent);
                        return {source: 'script', data: JSON.stringify(d)};
                    } catch(e) {}
                }
                return null;
            }""")
            
            if data:
                print(f"  📦 Found data in {data['source']}", file=sys.stderr)
                try:
                    parsed = json.loads(data['data'])
                    scorers = extract_scorers_from_html(json.dumps(parsed))
                    if not scorers:
                        # Try flattened search
                        text = json.dumps(parsed)
                        # Look for patterns like: {"name":"Player","team":"Team","goals":5}
                        matches = re.findall(
                            r'"(?:name|player|fullName)"\s*:\s*"([^"]+)"[^}]*'
                            r'"(?:team|teamName|teamAbbr)"\s*:\s*"([^"]+)"[^}]*'
                            r'"(?:goals|goalCount|stat)"\s*:\s*(\d+)',
                            text
                        )
                        for player, team_name, goals in matches:
                            code = match_team_code(team_name)
                            if code:
                                scorers.append((player, code, int(goals)))
                except json.JSONDecodeError:
                    pass
        
        # Last resort: try JSON API endpoints
        if not scorers:
            print("  🔍 Trying BBC API endpoints...", file=sys.stderr)
            for endpoint in [
                "https://push.api.bbci.co.uk/b?t=%2Fdata%2Fsport%2Ffootball%2Fworld-cup%2Ftop-scorers.json&v=1",
                "https://push.api.bbci.co.uk/b?t=%2Fdata%2Fsport%2Ffootball%2Fworld-cup%2Ftop-scorers.json",
            ]:
                try:
                    resp = page.evaluate(f"fetch('{endpoint}').then(r => r.text())")
                    if resp and len(resp) > 100:
                        try:
                            data = json.loads(resp)
                            text = json.dumps(data)
                            matches = re.findall(
                                r'"(?:name|player)"\s*:\s*"([^"]+)"[^}]*'
                                r'"(?:team|teamAbbr)"\s*:\s*"([^"]+)"[^}]*'
                                r'"(?:goals|value)"\s*:\s*(\d+)',
                                text
                            )
                            for player, team_name, goals in matches:
                                code = match_team_code(team_name)
                                if code:
                                    scorers.append((player, code, int(goals)))
                            if scorers:
                                break
                        except json.JSONDecodeError:
                            pass
                except Exception as e:
                    print(f"  ⚠ API error: {e}", file=sys.stderr)
        
        browser.close()
    
    return scorers


def scrape_matches_playwright():
    """Scrape match results from BBC scores & fixtures."""
    from playwright.sync_api import sync_playwright
    
    matches = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        for month in [6, 7]:
            url = f"https://www.bbc.com/sport/football/world-cup/scores-fixtures/2026-{month:02d}"
            print(f"  📅 Fetching {url}...", file=sys.stderr)
            
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                
                # Get rendered HTML
                html = page.content()
                
                # Extract fixtures - look for score spans
                fixtures_result = page.evaluate("""() => {
                    const results = [];
                    const fixtures = document.querySelectorAll('[class*="fixture"], [class*="Fixture"]');
                    fixtures.forEach(f => {
                        const team1 = f.querySelector('[class*="team-name"], [class*="TeamName"]');
                        const team2 = f.querySelectorAll('[class*="team-name"], [class*="TeamName"]')[1];
                        const scores = f.querySelectorAll('[class*="number"], [class*="Number"], [class*="score"], [class*="Score"]');
                        if (team1 && team2 && scores.length >= 2) {
                            results.push({
                                team1: team1.textContent.trim(),
                                team2: team2.textContent.trim(),
                                score1: scores[0].textContent.trim(),
                                score2: scores[1].textContent.trim()
                            });
                        }
                    });
                    return JSON.stringify(results);
                }""")
                
                if fixtures_result:
                    try:
                        data = json.loads(fixtures_result)
                        for f in data:
                            if not f.get('score1') or not f.get('score2'):
                                continue
                            try:
                                s1 = int(f['score1'])
                                s2 = int(f['score2'])
                                code1 = match_team_code(f['team1'])
                                code2 = match_team_code(f['team2'])
                                if code1 and code2:
                                    matches.append((code1, code2, s1, s2))
                            except (ValueError, TypeError):
                                pass
                    except json.JSONDecodeError:
                        pass
                
            except Exception as e:
                print(f"  ⚠ Error fetching {url}: {e}", file=sys.stderr)
        
        browser.close()
    
    return matches


def update_goalscorers(current, new_scorers):
    """Merge new scorers into current data."""
    if not new_scorers:
        return False
    
    old = current.get('goalscorers', [])
    old_map = {}
    for item in old:
        if isinstance(item, (list, tuple)):
            name = item[0]
        elif isinstance(item, dict):
            name = item.get('name', '')
        else:
            continue
        key = re.sub(r'[^a-z0-9]', '', name.strip().lower())
        old_map[key] = list(item) if isinstance(item, (list, tuple)) else [item['name'], item['team'], item['goals']]
    
    changed = False
    seen_keys = set()
    
    for player, code, goals in new_scorers:
        key = re.sub(r'[^a-z0-9]', '', player.strip().lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)
        
        if key in old_map:
            old_goals = old_map[key][2]
            if old_goals != goals:
                print(f"  🔄 {player} ({code}): {old_goals} → {goals}", file=sys.stderr)
                old_map[key] = [player, code, goals]
                changed = True
        else:
            print(f"  ➕ {player} ({code}): {goals}⚽", file=sys.stderr)
            old_map[key] = [player, code, goals]
            changed = True
    
    if changed:
        # Sort by goals descending
        sorted_scorers = sorted(old_map.values(), key=lambda x: -x[2])
        current['goalscorers'] = sorted_scorers
    
    return changed


def update_bracket(current, matches):
    """Update bracket match results."""
    if not matches:
        return False
    
    bracket = current.get('bracket', {})
    r32 = bracket.get('round_of_32', [])
    if not r32:
        return False
    
    changed = False
    for code1, code2, s1, s2 in matches:
        for match in r32:
            if match['team1'] == code1 and match['team2'] == code2:
                if match.get('score1') != s1 or match.get('score2') != s2:
                    match['score1'] = s1
                    match['score2'] = s2
                    match['status'] = 'done'
                    print(f"  📊 {code1} {s1}-{s2} {code2} ✓", file=sys.stderr)
                    changed = True
                break
    
    return changed


def main():
    print(f"🔍 Tribuna 10 Sport — Scraper Automático", file=sys.stderr)
    print(f"   {datetime.now().isoformat()}", file=sys.stderr)
    print(file=sys.stderr)
    
    current = load_current()
    any_change = False
    
    # Try Playwright-based scraping
    print("🎭 Stage 1: Goleadores", file=sys.stderr)
    try:
        scorers = scrape_bbc_scorers_playwright()
        if scorers:
            print(f"\n  ✅ {len(scorers)} goleadores encontrados", file=sys.stderr)
            if update_goalscorers(current, scorers):
                any_change = True
        else:
            print("  ⚠ No se encontraron goleadores", file=sys.stderr)
    except Exception as e:
        print(f"  ❌ Error: {e}", file=sys.stderr)
    
    print(file=sys.stderr)
    print("🎭 Stage 2: Resultados", file=sys.stderr)
    try:
        matches = scrape_matches_playwright()
        if matches:
            print(f"\n  ✅ {len(matches)} partidos encontrados", file=sys.stderr)
            if update_bracket(current, matches):
                any_change = True
        else:
            print("  ⚠ No se encontraron partidos", file=sys.stderr)
    except Exception as e:
        print(f"  ❌ Error: {e}", file=sys.stderr)
    
    if any_change:
        current['last_updated'] = datetime.now().isoformat()
        save_data(current)
        print(file=sys.stderr)
        print("✅ DATOS ACTUALIZADOS — cambios detectados", file=sys.stderr)
    else:
        print(file=sys.stderr)
        print("📡 Sin cambios — datos al día", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
