import sys
import io
import streamlit as st

sys.path.insert(0, ".")
from teamanalysis import team_analysis

st.set_page_config(page_title="Analisi Squadre", page_icon="🏆", layout="centered")

st.title("🏆 Analisi Squadre — TopDeck.gg")
st.caption("Inserisci i parametri del torneo e clicca **Analizza** per ottenere il report.")

# API key da Streamlit Secrets (non visibile nel codice)
api_key = st.secrets["api_key"]

# ── Parametri ────────────────────────────────────────────────────────────────
with st.expander("⚙️ Parametri", expanded=True):
    with st.form("params"):
        tournament_id = st.text_input(
            "Tournament ID",
            value="thesideralwolf-tournament-series3",
            help="L'ID del torneo su TopDeck.gg (es. thesideralwolf-tournament-series3)",
        )
        site = st.text_input(
            "Sito",
            value="https://topdeck.gg",
            help="URL base del sito (di solito non va modificato)",
        )
        gsheet_url = st.text_input(
            "Google Sheet URL",
            value="https://docs.google.com/spreadsheets/u/0/d/1fkwHoruSU_9-YqRYv_qvcBe52bc0VVgfMx38WNBvjjY/htmlview#gid=1101659693",
            help="Link al foglio Google Sheets con i dati delle squadre (deve essere pubblico)",
        )
        submitted = st.form_submit_button("🔍 Analizza", use_container_width=True)


# ── Funzione cached ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_analysis(api_key, tournament_id, site, gsheet_url):
    return team_analysis(api_key, tournament_id, site, gsheet_url)


def df_to_excel_bytes(df):
    import pandas as pd
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return buf.getvalue()


# ── Risultati ─────────────────────────────────────────────────────────────────
if submitted:
    if not tournament_id.strip():
        st.warning("⚠️ Inserisci un Tournament ID valido.")
        st.stop()

    with st.spinner("⏳ Download dati in corso, attendere..."):
        try:
            classifica, giocatori, merged_df, rounds_df = run_analysis(
                api_key, tournament_id, site, gsheet_url
            )
        except Exception as e:
            st.error(f"❌ Errore durante il download: {e}")
            st.caption("Verifica che il Tournament ID sia corretto e che il Google Sheet sia pubblico.")
            st.stop()

    st.success("✅ Analisi completata!")
    st.divider()

    # ── Podio Top 3 Squadre ───────────────────────────────────────────────────
    st.subheader("🥇 Top 3 Squadre")

    medaglie = ["🥇", "🥈", "🥉"]
    squadre_ordinate = classifica.reset_index()  # colonne: Squadra, tot_punti

    cols = st.columns(3)
    for i, (col, (_, row)) in enumerate(zip(cols, squadre_ordinate.iterrows())):
        with col:
            st.metric(
                label=f"{medaglie[i]} {row['Squadra']}",
                value=f"{int(row['tot_punti'])} pt",
            )

    st.divider()

    # ── Dettaglio giocatori per squadra ──────────────────────────────────────
    st.subheader("👥 Giocatori delle Top 3 Squadre")

    for i, (_, row) in enumerate(squadre_ordinate.iterrows()):
        nome_squadra = row["Squadra"]
        gioc_squadra = (
            giocatori[giocatori["Squadra"] == nome_squadra]
            [["Nominativo", "Punti"]]
            .reset_index(drop=True)
        )
        gioc_squadra.index = gioc_squadra.index + 1

        with st.expander(f"{medaglie[i]} {nome_squadra} — {int(row['tot_punti'])} punti totali", expanded=True):
            st.dataframe(gioc_squadra, use_container_width=True)

    st.divider()

    # ── Tabella completa standings + squadre ──────────────────────────────────
    st.subheader("📋 Tabella completa (Standings + Squadre)")
    st.dataframe(merged_df, use_container_width=True)

    excel_merged = df_to_excel_bytes(merged_df)
    st.download_button(
        label="⬇️ Scarica tabella completa (Excel)",
        data=excel_merged,
        file_name=f"standings_squadre_{tournament_id}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.divider()

    # ── Round (collassato) ────────────────────────────────────────────────────
    with st.expander("📋 Dettaglio round (dati grezzi)"):
        st.dataframe(rounds_df, use_container_width=True)
        csv_rounds = rounds_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Scarica round (CSV)",
            data=csv_rounds,
            file_name=f"rounds_{tournament_id}.csv",
            mime="text/csv",
        )
