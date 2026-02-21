import os
import gradio as gr
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
from utils.prompts import build_analysis_prompt
from utils.parser import parse_gemini_output

# Use environment variable for the API key; don't hardcode secrets
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    # Allow Gradio app to start but surface a helpful error if used without a key
    genai.configure(api_key=None)

model = genai.GenerativeModel("gemini-pro")

def analyze(policy_file, comm_file):
    # support text or PDF policy files
    try:
        if hasattr(policy_file, 'name') and policy_file.name.lower().endswith('.pdf'):
            policy_file.seek(0)
            reader = PdfReader(policy_file)
            policy_text = "\n".join([p.extract_text() or "" for p in reader.pages])
        else:
            policy_text = policy_file.read().decode("utf-8")
    except Exception:
        policy_text = ""
    df = pd.read_csv(comm_file.name)

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

    return pd.DataFrame(
        results,
        columns=["Message", "Violation Type", "Severity", "Confidence", "Explanation"]
    )

demo = gr.Interface(
    fn=analyze,
    inputs=[
        gr.File(label="Upload Policy (txt)"),
        gr.File(label="Upload Communications CSV")
    ],
    outputs=gr.Dataframe(),
    title="AI Compliance & Policy Monitoring Agent"
)

demo.launch()