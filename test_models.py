#!/usr/bin/env python3
"""List available models accessible with the configured API key."""
import os
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY") or "AIzaSyB3BRyHXFOSMoPv13V9jt_dHVgVKEqtL68"
genai.configure(api_key=api_key)

print("Available models for your API key:")
print("-" * 80)
try:
    models_list = list(genai.list_models())
    print(f"Total models found: {len(models_list)}\n")
    for model in models_list:
        print(f"Name: {model.name}")
        if hasattr(model, 'display_name'):
            print(f"  Display: {model.display_name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Supported methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error listing models: {e}\n")

print("\nTesting specific models for generateContent support:")
print("-" * 80)
test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro",
    "gemini-pro",
    "models/gemini-1.5-flash",
    "models/gemini-pro",
]

for model_name in test_models:
    try:
        m = genai.GenerativeModel(model_name)
        # Try a simple generation
        resp = m.generate_content("Say 'ok'")
        print(f"✓ {model_name} works for generateContent")
    except Exception as e:
        print(f"✗ {model_name}: {str(e)[:100]}")
