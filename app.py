import os
import gradio as gr
import pandas as pd
import google.generativeai as genai
from utils.prompts import build_analysis_prompt
from utils.parser import parse_gemini_output

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def analyze(policy_file, comm_file):
    policy_text = policy_file.read().decode("utf-8")
    df = pd.read_csv(comm_file.name)

    results = []

    for _, row in df.iterrows():
        message = str(row.iloc[0])

        prompt = build_analysis_prompt(policy_text, message)
        response = model.generate_content(prompt).text

        parsed = parse_gemini_output(response)

        results.append([
            message,
            parsed["violation_type"],
            parsed["severity"],
            parsed["confidence"],
            parsed["explanation"]
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