import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def validate_output_with_gpt(output_text: str) -> str:
    validation_prompt = f"""
You are validating a Brightspace-compatible multiple-choice quiz file.

Check:
- Starts with required headers
- Has all required fields in correct order
- Tabs separate fields
- Each question includes one Option marked 100

Respond with:
✅ VALID FILE
or
❌ INVALID FILE: <list issues>

Here is the content to validate:
""" + output_text

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in Brightspace quiz formatting."},
            {"role": "user", "content": validation_prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def attempt_fix_with_gpt(raw_text: str) -> str:
    repair_prompt = f"""
The previous file failed Brightspace validation.

Please reformat this quiz content into proper Brightspace format using tab-delimited fields. Ensure:
- Correct answer marked 100
- Headers present
- All fields tab-separated

Raw quiz text:
---
{raw_text}
---
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You convert raw quiz text to valid Brightspace tab-delimited format."},
            {"role": "user", "content": repair_prompt}
        ]
    )

    return response['choices'][0]['message']['content']
