# AI Compliance & Policy Monitoring Agent

AI-powered prototype that analyzes enterprise communications against organizational policies using Google Gemini.

## Features
- Policy ingestion
- Semantic violation detection
- Severity & confidence scoring
- Explainable outputs

## Run Locally

Set API key (preferred: environment variable):

```bash
export GOOGLE_API_KEY=your_key_here
```

Or create a local Streamlit secrets file at `.streamlit/secrets.toml` using the format in `.streamlit/secrets.example.toml`.

Install deps:

```bash
pip install -r requirements.txt
```

Run (Gradio):

```bash
python app.py
```

Run (Streamlit):

```bash
streamlit run streamlit_app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. In Streamlit Cloud, create a new app and connect your GitHub repo and branch.
3. In the app's Settings → Secrets, add a secret named `GOOGLE_API_KEY` with your Gemini API key.
4. Set the app's main file to `streamlit_app.py` and deploy. The app reads the key from `st.secrets` or the environment.

Note: For security, do NOT commit the real API key into the repository. Use Streamlit Cloud Secrets or environment variables.