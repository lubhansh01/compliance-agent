import os
import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
from utils.prompts import build_analysis_prompt
from utils.parser import parse_gemini_output

st.set_page_config(page_title="AI Compliance & Policy Monitoring Agent")

st.title("AI Compliance & Policy Monitoring Agent")

# Resolve API key from environment or Streamlit secrets
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("No Google Generative API key found. Set `GOOGLE_API_KEY` in Streamlit secrets.")

model = genai.GenerativeModel("gemini-pro")

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
        except Exception as e:
            response = str(e)
        parsed = parse_gemini_output(response)
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
            st.success("Analysis complete")
            st.dataframe(result_df)
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download results CSV", data=csv, file_name="analysis_results.csv", mime="text/csv")
