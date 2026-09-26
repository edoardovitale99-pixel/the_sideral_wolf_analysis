"""
TopDeck.gg - Scarica i round di un torneo e restituisce il CSV.

Uso:
    csv_str = download_rounds(api_key, tournament_id, site)

Requisiti:
    pip install requests

Dati forniti da TopDeck.gg (https://topdeck.gg)
"""

import csv
import io
import time

import requests


CAMPI = ["round", "tavolo", "status", "n_giocatori",
         "giocatore_1", "id_1", "giocatore_2", "id_2",
         "winner", "winner_id", "winner_games", "loser_games", "esito"]


def download_rounds(api_key: str, tournament_id: str, site: str) -> str:
    """
    Scarica i round di un torneo e restituisce il contenuto CSV come stringa.

    Args:
        api_key:       chiave API TopDeck (https://topdeck.gg/developers)
        tournament_id: ID del torneo (es. "thesideralwolf-tournament-series3")
        site:          URL base del sito (es. "https://topdeck.gg")

    Returns:
        Stringa in formato CSV (UTF-8-sig) con un tavolo per riga.
    """
    base = site.rstrip("/") + "/api/v2"
    rounds = _get(base, api_key, f"tournaments/{tournament_id}/rounds")
    return _build_csv(rounds)


def _get(base: str, api_key: str, endpoint: str, max_retries: int = 3):
    url = f"{base}/{endpoint}"
    for _ in range(max_retries):
        r = requests.get(url, headers={"Authorization": api_key}, timeout=30)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 5)))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"rate limit persistente su {endpoint}")


def _build_csv(rounds) -> str:
    righe = []
    for r in rounds:
        for t in (r.get("tables") or []):
            giocatori = t.get("players") or []
            p1 = giocatori[0] if len(giocatori) > 0 else {}
            p2 = giocatori[1] if len(giocatori) > 1 else {}

            w = t.get("winner_id")
            if w == "Draw":
                esito = "pareggio"
            elif w is None:
                esito = "non concluso"
            elif w == p1.get("id"):
                esito = "vince_1"
            elif w == p2.get("id"):
                esito = "vince_2"
            else:
                esito = "vincitore non fra i players"

            righe.append({
                "round":        r.get("round"),
                "tavolo":       t.get("table"),
                "status":       t.get("status"),
                "n_giocatori":  len(giocatori),
                "giocatore_1":  p1.get("name", ""),
                "id_1":         p1.get("id", ""),
                "giocatore_2":  p2.get("name", ""),
                "id_2":         p2.get("id", ""),
                "winner":       t.get("winner") or "",
                "winner_id":    w if w is not None else "",
                "winner_games": t.get("winner_games") if t.get("winner_games") is not None else "",
                "loser_games":  t.get("loser_games") if t.get("loser_games") is not None else "",
                "esito":        esito,
            })

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CAMPI, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(righe)
    return buf.getvalue()
