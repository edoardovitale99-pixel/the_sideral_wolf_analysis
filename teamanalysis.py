"""
Analisi classifica squadre da torneo TopDeck.gg + foglio squadre Google Sheets.

Uso:
    from teamanalysis import team_analysis
    classifica_squadre, giocatori_top3, standings = team_analysis(api_key, tournament_id, site, gsheet_url)
"""

import io
import pandas as pd

from downloadround import download_rounds
from downloadstandings import download_standings
from readgsheet import read_gsheet


def team_analysis(
    api_key: str,
    tournament_id: str,
    site: str,
    gsheet_url: str,
    top_n: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Scarica rounds, standings e dati squadre, restituisce classifica e giocatori delle top squadre.

    Args:
        api_key:       chiave API TopDeck
        tournament_id: ID torneo (es. "thesideralwolf-tournament-series3")
        site:          URL base del sito (es. "https://topdeck.gg")
        gsheet_url:    link al foglio Google Sheets con i dati squadre
        top_n:         numero di squadre da restituire in classifica (default 3)

    Returns:
        classifica_squadre: DataFrame con le top_n squadre e la somma dei punti top-3 giocatori
        giocatori_top3:     DataFrame con Nominativo e Squadra dei giocatori di quelle squadre
        standings:          DataFrame completo con i dati della classifica filtrata
    """
    # 1. Download e lettura dei dati dai vari moduli
    rounds_df = pd.read_csv(io.StringIO(download_rounds(api_key, tournament_id, site)))
    csv_str = download_standings(api_key, tournament_id, site)
    standings = pd.read_csv(io.StringIO(csv_str))
    team_df = read_gsheet(gsheet_url)

    # 2. Pulizia stringhe (rimozione spazi bianchi superflui prima/dopo il testo)
    team_df["Nominativo"] = team_df["Nominativo"].str.strip()
    standings["Nome giocatore"] = standings["Nome giocatore"].str.strip()

    # 3. Merge dei dati. Usiamo 'left' se vogliamo solo chi è su TopDeck, 
    # o 'outer' se vuoi tracciare anche chi non ha ancora aggiornato i dati.
    merged_df = pd.merge(
        standings,
        team_df,
        left_on="Nome giocatore",
        right_on="Nominativo",
        how="outer",
    )

    # CORREZIONE CRITICA PER TORNEI IN CORSO: 
    # Se il torneo è parziale o un giocatore non ha dati, i suoi punti saranno NaN. Li convertiamo a 0.
    merged_df["Punti"] = merged_df["Punti"].fillna(0).astype(int)
    
    # Se il nome manca dalle standings di TopDeck ma c'è nel foglio squadre, riallineiamo il campo Nominativo
    merged_df["Nominativo"] = merged_df["Nominativo"].fillna(merged_df["Nome giocatore"])
    
    # Rimuoviamo eventuali righe dove non è specificata la squadra per evitare il gruppo "NaN"
    merged_df = merged_df.dropna(subset=["Squadra"])

    # 4. Calcolo della classifica delle squadre (somma dei punti dei migliori 3 giocatori per squadra)
    classifica_squadre = (
        merged_df
        .sort_values(by="Punti", ascending=False)
        .groupby("Squadra").head(3)
        .groupby("Squadra").agg(tot_punti=("Punti", "sum"))
        .sort_values(by="tot_punti", ascending=False)
        .head(top_n)
    )

    # 5. Estrazione dei giocatori appartenenti alle top squadre individuate
    giocatori_top3 = (
        merged_df
        .loc[merged_df["Squadra"].isin(classifica_squadre.index), ["Nominativo", "Squadra", "Punti"]]
        .sort_values(by=["Squadra", "Punti"], ascending=[True, False])
    )

    return classifica_squadre, giocatori_top3, standings
