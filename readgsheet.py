"""
Lettura di un foglio Google Sheets pubblico come DataFrame pandas.

Uso:
    df = read_gsheet(url)

Requisiti:
    pip install pandas requests
"""

import re
import pandas as pd


def read_gsheet(url: str) -> pd.DataFrame:
    """
    Legge un foglio Google Sheets pubblico e restituisce un DataFrame.

    Args:
        url: link al foglio (htmlview, edit, ecc.), con o senza #gid=...

    Returns:
        DataFrame con i dati del foglio.
    """
    sheet_id, gid = _parse_url(url)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)


def _parse_url(url: str):
    m = re.search(r"/spreadsheets(?:/u/\d+)?/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        raise ValueError(f"Impossibile estrarre lo sheet ID da: {url}")
    sheet_id = m.group(1)

    gid_match = re.search(r"gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    return sheet_id, gid
