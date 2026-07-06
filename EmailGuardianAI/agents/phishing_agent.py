from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define what the JSON output must look like
class PhishingAnalysis(BaseModel):
    indicators_found: list[str] = Field(description="Specific triggers found like OTP requests, login details, or bank verifications")
    severity: str = Field(description="Low, Medium, or High threat evaluation")
    confidence_score: float = Field(description="Confidence score from 0.0 to 1.0")

def analyze_phishing(client: genai.Client, email_text: str) -> PhishingAnalysis:
    prompt = f"""
    Analyze the following email text specifically for phishing indicators:
    - Requests for sensitive data (passwords, OTPs, logins).
    - Administrative actions (account suspension, bank verification, urgent updates).
    - Financial requests (gift cards, unexpected wire transfers).
    
    Email Text:
    \"\"\"{email_text}\"\"\"
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PhishingAnalysis,
            temperature=0.1  # Kept low for deterministic, analytical results
        ),
    )
    return PhishingAnalysis.model_validate_json(response.text)