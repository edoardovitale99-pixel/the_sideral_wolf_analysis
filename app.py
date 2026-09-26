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
        top_n = st.number_input(
            "Top N squadre",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="Quante squadre mostrare in classifica",
        )
        submitted = st.form_submit_button("🔍 Analizza", use_container_width=True)


# ── Funzione cached ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_analysis(api_key, tournament_id, site, gsheet_url, top_n):
    return team_analysis(api_key, tournament_id, site, gsheet_url, top_n)


# ── Risultati ─────────────────────────────────────────────────────────────────
if submitted:
    if not tournament_id.strip():
        st.warning("⚠️ Inserisci un Tournament ID valido.")
        st.stop()

    with st.spinner("⏳ Download dati in corso, attendere..."):
        try:
            classifica, giocatori, rounds_df = run_analysis(
                api_key, tournament_id, site, gsheet_url, top_n
            )
        except Exception as e:
            st.error(f"❌ Errore durante il download: {e}")
            st.caption("Verifica che il Tournament ID sia corretto e che il Google Sheet sia pubblico.")
            st.stop()

    st.success("✅ Analisi completata!")

    # ── Classifica squadre ────────────────────────────────────────────────────
    st.subheader("🥇 Classifica Squadre")

    classifica_display = classifica.reset_index()
    classifica_display.index = classifica_display.index + 1  # posizione da 1
    classifica_display.columns = ["Squadra", "Punti (top 3 giocatori)"]
    st.dataframe(classifica_display, use_container_width=True)

    csv_classifica = classifica_display.to_csv(index=True).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Scarica classifica squadre (CSV)",
        data=csv_classifica,
        file_name=f"classifica_squadre_{tournament_id}.csv",
        mime="text/csv",
    )

    st.divider()

    # ── Giocatori top squadre ─────────────────────────────────────────────────
    st.subheader(f"👥 Giocatori delle top {top_n} squadre")
    giocatori_display = giocatori.reset_index(drop=True)
    giocatori_display.index = giocatori_display.index + 1
    st.dataframe(giocatori_display, use_container_width=True)

    csv_giocatori = giocatori_display.to_csv(index=True).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Scarica lista giocatori (CSV)",
        data=csv_giocatori,
        file_name=f"giocatori_top_{tournament_id}.csv",
        mime="text/csv",
    )

    st.divider()

    # ── Round (opzionale, collassato) ─────────────────────────────────────────
    with st.expander("📋 Dettaglio round (dati grezzi)"):
        st.dataframe(rounds_df, use_container_width=True)
        csv_rounds = rounds_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Scarica round (CSV)",
            data=csv_rounds,
            file_name=f"rounds_{tournament_id}.csv",
            mime="text/csv",
        )
