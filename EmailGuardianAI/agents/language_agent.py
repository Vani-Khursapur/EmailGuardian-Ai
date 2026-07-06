from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define the linguistic output profile
class LanguageAnalysis(BaseModel):
    tactics_detected: list[str] = Field(description="Psychological triggers used like Urgency, Fear, Threat, or Artificial Reward")
    emotional_tone: str = Field(description="The primary tone of the text, e.g., Professional, Panicked, Hostile, or Direct")
    manipulation_detected: bool = Field(description="True if deceptive psychological tactics are found")

def analyze_language(client: genai.Client, email_text: str) -> LanguageAnalysis:
    prompt = f"""
    Analyze the linguistic and psychological patterns of this email text:
    - Look for artificial timelines or scarcity (e.g., 'Act within 30 minutes').
    - Look for high-pressure fear tactics ('Your assets will be locked permanently').
    - Spot emotional manipulation patterns meant to bypass logical thinking.
    
    Email Text:
    \"\"\"{email_text}\"\"\"
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LanguageAnalysis,
            temperature=0.1
        ),
    )
    return LanguageAnalysis.model_validate_json(response.text)