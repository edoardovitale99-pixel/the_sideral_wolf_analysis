# Analisi Squadre — TopDeck.gg

Tool Streamlit per analizzare la classifica squadre di un torneo su TopDeck.gg.

## Struttura del progetto

```
├── app.py                    ← interfaccia web
├── teamanalysis.py           ← logica principale
├── downloadround.py          ← scarica i round via API
├── downloadstandings.py      ← scarica la classifica via API
├── readgsheet.py             ← legge il Google Sheet squadre
├── requirements.txt          ← dipendenze Python
├── .gitignore
└── .streamlit/
    └── secrets.toml          ← API key (solo in locale, NON su GitHub)
```

## Deploy su Streamlit Cloud (gratuito)

1. **Crea un repository GitHub** e carica tutti i file (escluso `.streamlit/secrets.toml`).

2. **Vai su [share.streamlit.io](https://share.streamlit.io)** e accedi con GitHub.

3. **Crea una nuova app** → seleziona il tuo repo → file principale: `app.py`.

4. **Configura il segreto API key:**
   - Nella pagina dell'app, vai su **Settings → Secrets**
   - Incolla il seguente testo e sostituisci con la tua chiave:
     ```toml
     api_key = "LA_TUA_API_KEY_QUI"
     ```

5. **Clicca Deploy** — dopo qualche secondo il link è pronto da condividere.

## Uso in locale

```bash
pip install -r requirements.txt

# Crea il file segreti
mkdir -p .streamlit
echo 'api_key = "LA_TUA_API_KEY"' > .streamlit/secrets.toml

streamlit run app.py
```

## Note

- Il Google Sheet con i dati squadre deve essere **pubblico** (Condividi → Chiunque abbia il link può visualizzare).
- La cache dei risultati dura finché l'app è aperta. Per forzare un nuovo download, ricarica la pagina del browser.
