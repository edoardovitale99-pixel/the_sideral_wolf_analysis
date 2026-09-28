"""
Analisi classifica squadre da torneo TopDeck.gg + foglio squadre Google Sheets.

Uso:
    from teamanalysis import team_analysis
    classifica_squadre, giocatori_top3, merged_df, rounds_df = team_analysis(api_key, tournament_id, site, gsheet_url)
"""

import io

import pandas as pd

from downloadround import download_rounds
from downloadstandings import download_standings
from readgsheet import read_gsheet

TOP_N = 3


def team_analysis(
    api_key: str,
    tournament_id: str,
    site: str,
    gsheet_url: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Scarica rounds, standings e dati squadre, restituisce classifica e giocatori delle top 3 squadre.

    Args:
        api_key:       chiave API TopDeck
        tournament_id: ID torneo (es. "thesideralwolf-tournament-series3")
        site:          URL base del sito (es. "https://topdeck.gg")
        gsheet_url:    link al foglio Google Sheets con i dati squadre

    Returns:
        classifica_squadre: DataFrame con le top 3 squadre e la somma dei punti top-3 giocatori
        giocatori_top3:     DataFrame con Nominativo, Squadra e Punti dei giocatori di quelle squadre
        merged_df:          DataFrame completo standings + squadre (tutti i giocatori)
        rounds_df:          DataFrame con i dati dei round del torneo
    """
    rounds_df = pd.read_csv(io.StringIO(download_rounds(api_key, tournament_id, site)))

    csv_str = download_standings(api_key, tournament_id, site)
    standings = pd.read_csv(io.StringIO(csv_str))

    team_df = read_gsheet(gsheet_url)
    team_df["Nominativo"] = team_df["Nominativo"].str.strip()
    standings["Nome giocatore"] = standings["Nome giocatore"].str.strip()

    merged_df = pd.merge(
        standings,
        team_df,
        left_on="Nome giocatore",
        right_on="Nominativo",
        how="outer",
    )

    classifica_squadre = (
        merged_df
        .sort_values(by="Punti", ascending=False)
        .groupby("Squadra").head(3)
        .groupby("Squadra").agg(tot_punti=("Punti", "sum"))
        .sort_values(by="tot_punti", ascending=False)
        .head(TOP_N)
    )

    giocatori_top3 = (
        merged_df
        .loc[merged_df["Squadra"].isin(classifica_squadre.index), ["Nominativo", "Squadra", "Punti"]]
        .sort_values(by=["Squadra", "Punti"], ascending=[True, False])
        .reset_index(drop=True)
    )

    return classifica_squadre, giocatori_top3, merged_df, rounds_df
