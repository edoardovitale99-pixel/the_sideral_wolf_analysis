"""
TopDeck.gg - Esportatore classifica in CSV.

Uso:
    csv_str = download_standings(api_key, tournament_id, site)

Requisiti:
    pip install requests

Dati forniti da TopDeck.gg (https://topdeck.gg)
"""

import csv
import io

import requests


COLUMNS = {
    "standing":        "Posizione",
    "name":            "Nome giocatore",
    "id":              "ID giocatore",
    "points":          "Punti",
    "wins":            "Vittorie",
    "winsSwiss":       "Vittorie Swiss",
    "winsBracket":     "Vittorie Bracket",
    "losses":          "Sconfitte",
    "lossesSwiss":     "Sconfitte Swiss",
    "lossesBracket":   "Sconfitte Bracket",
    "draws":           "Pareggi",
    "winRate":         "Win Rate %",
    "winRateSwiss":    "Win Rate Swiss %",
    "winRateBracket":  "Win Rate Bracket %",
    "opponentWinRate": "Opp. Win Rate %",
    "byes":            "Bye",
    "decklist":        "Decklist",
}

WIN_RATE_FIELDS = {"winRate", "winRateSwiss", "winRateBracket", "opponentWinRate"}


def download_standings(api_key: str, tournament_id: str, site: str) -> str:
    """
    Scarica la classifica di un torneo e restituisce il contenuto CSV come stringa.

    Args:
        api_key:       chiave API TopDeck (https://topdeck.gg/developers)
        tournament_id: ID del torneo (es. "thesideralwolf-tournament-series3")
        site:          URL base del sito (es. "https://topdeck.gg")

    Returns:
        Stringa in formato CSV con un giocatore per riga.
    """
    base = site.rstrip("/") + "/api/v2"
    session = requests.Session()
    session.headers.update({"Authorization": api_key})

    standings = _fetch(session, base, f"tournaments/{tournament_id}/standings")

    if not isinstance(standings, list) or not standings:
        raise ValueError("Nessun dato di classifica trovato.")

    return _build_csv(standings)


def _fetch(session, base: str, endpoint: str):
    r = session.get(f"{base}/{endpoint}", timeout=30)
    r.raise_for_status()
    return r.json()


def _build_csv(standings) -> str:
    columns = [key for key in COLUMNS if any(row.get(key) is not None for row in standings)]

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([COLUMNS[c] for c in columns])
    for row in standings:
        writer.writerow([_fmt(c, row.get(c)) for c in columns])
    return buf.getvalue()


def _fmt(key, val):
    if val is None:
        return ""
    if key in WIN_RATE_FIELDS:
        try:
            return f"{float(val) * 100:.2f}%"
        except (ValueError, TypeError):
            pass
    return str(val)
