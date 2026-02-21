def parse_gemini_output(text):
    lines = text.split("\n")

    data = {
        "violation_type": "None",
        "severity": "Low",
        "confidence": "0%",
        "explanation": text.strip()
    }

    for line in lines:
        if "Violation Type:" in line:
            data["violation_type"] = line.split("Violation Type:")[-1].strip()

        elif "Severity:" in line:
            data["severity"] = line.split("Severity:")[-1].strip()

        elif "Confidence:" in line:
            data["confidence"] = line.split("Confidence:")[-1].strip()

        elif "Explanation:" in line:
            data["explanation"] = line.split("Explanation:")[-1].strip()

    return data