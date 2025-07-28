import openai
from flask import current_app

def analyze_risk(description):
    openai.api_key = current_app.config['OPENAI_API_KEY']

    prompt = f"""
    You are an expert audit risk analyst.
    Analyze the following checklist description and generate a 2-3 sentence summary highlighting potential risks, non-compliance issues, or areas of concern.

    Checklist Description:
    \"\"\"{description}\"\"\"

    Return clear and concise points.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=250
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI summarization failed: {str(e)}"
