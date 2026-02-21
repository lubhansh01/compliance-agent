def build_analysis_prompt(policy_text, message):
    return f"""
You are an enterprise compliance monitoring agent.

Policy Document:
{policy_text}

Message:
{message}

Analyze the message against the policy.

Respond STRICTLY in this format:

Violation Type:
Severity:
Confidence:
Explanation:
"""