import os
import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
from utils.prompts import build_analysis_prompt
from utils.parser import parse_gemini_output

st.set_page_config(page_title="AI Compliance & Policy Monitoring Agent")

st.title("AI Compliance & Policy Monitoring Agent")

def _get_api_key():
    # Prefer environment variables; fall back to Streamlit secrets if present.
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
    if key:
        return key
    try:
        # Accessing st.secrets when no secrets.toml exists can raise StreamlitSecretNotFoundError.
        secret_key = None
        try:
            # st.secrets behaves like a mapping; use get if available, else index
            secret_key = st.secrets.get("GOOGLE_API_KEY") if hasattr(st.secrets, 'get') else st.secrets["GOOGLE_API_KEY"]
        except Exception:
            secret_key = None
        return secret_key
    except Exception:
        # In rare cases accessing st.secrets itself may fail during import; ignore and return None
        return None


api_key = _get_api_key()
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("No Google Generative API key found. Set `GOOGLE_API_KEY` in Streamlit secrets or as an environment variable.")

# Allow configuring model via env var; default to latest 'gemini-2.5-flash'
MODEL_NAME = os.getenv("MODEL_NAME") or "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

policy_file = st.file_uploader("Upload policy (txt or pdf)", type=["txt", "pdf"]) 
comm_file = st.file_uploader("Upload communications CSV", type=["csv"]) 

def extract_text_from_pdf(file_obj) -> str:
    try:
        file_obj.seek(0)
        reader = PdfReader(file_obj)
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)
    except Exception:
        return ""


def analyze(policy_text, df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for _, row in df.iterrows():
        message = str(row.iloc[0])
        prompt = build_analysis_prompt(policy_text, message)
        try:
            response = model.generate_content(prompt).text
            parsed = parse_gemini_output(response)
        except Exception as e:
            # Provide a clear parsed structure so the UI shows the API error per-row
            parsed = {
                "violation_type": "API Error",
                "severity": "N/A",
                "confidence": "0%",
                "explanation": str(e)
            }

        results.append([
            message,
            parsed.get("violation_type", ""),
            parsed.get("severity", ""),
            parsed.get("confidence", ""),
            parsed.get("explanation", "")
        ])

    return pd.DataFrame(results, columns=["Message", "Violation Type", "Severity", "Confidence", "Explanation"])

if st.button("Analyze"):
    if not policy_file or not comm_file:
        st.error("Please upload both a policy file and a communications CSV before analyzing.")
    else:
        # Read policy text from txt or pdf
        if policy_file.name.lower().endswith('.pdf'):
            policy_text = extract_text_from_pdf(policy_file)
        else:
            policy_text = policy_file.read().decode("utf-8")
        try:
            df = pd.read_csv(comm_file)
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
        else:
            with st.spinner("Analyzing messages..."):
                result_df = analyze(policy_text, df)

            # Show which model was used
            st.info(f"Model used: {MODEL_NAME}")

            # If there are API errors (e.g. model not found), surface a prominent message
            api_errors = result_df[ result_df['Violation Type'].str.contains('API Error', na=False) ]
            if not api_errors.empty:
                st.error(
                    "API errors detected while calling the model. Check your API key, model name, and quota.\n"
                    "Common cause: '404 models/gemini-pro is not found' — either the API key lacks access to that model or the model name is invalid.\n"
                    "Recommendation: verify `GOOGLE_API_KEY` and consider switching to the supported `google.genai` client and a valid model name."
                )

            st.success("Analysis complete")
            st.dataframe(result_df)
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download results CSV", data=csv, file_name="analysis_results.csv", mime="text/csv")

# Quick API model test
if st.button("Test API / Model"):
    if not api_key:
        st.error("No API key configured. Set GOOGLE_API_KEY in environment or Streamlit secrets.")
    else:
        test_prompt = "Say 'hello'"
        try:
            resp = model.generate_content(test_prompt).text
            st.success("API test successful — model responded")
            st.write(resp)
        except Exception as e:
            st.error(f"API test failed: {e}")
            st.info(f"Model attempted: {MODEL_NAME}")
