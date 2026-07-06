import re
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define the structured output for our domain risk assessment
class LinkAnalysis(BaseModel):
    extracted_urls: list[str] = Field(description="List of all raw URLs found in the text")
    suspicious_urls: list[str] = Field(description="URLs matching deceptive patterns, brand spoofs, or suspicious domains")
    risk_level: str = Field(description="Low, Medium, or High depending on link safety profile")

def analyze_links(client: genai.Client, email_text: str) -> LinkAnalysis:
    # Tool: Use Python regex to pull out URLs first
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    urls = re.findall(url_pattern, email_text)
    
    # If there are no links in the email, return a clean, safe schema immediately
    if not urls:
        return LinkAnalysis(extracted_urls=[], suspicious_urls=[], risk_level="Low")
        
    prompt = f"""
    You are the Link Analysis Agent. Review these URLs extracted from a suspicious email body.
    Identify if any use brand-spoofing tactics (like 'secure-paypal'), deceptive top-level domains (.xyz, .top, .cc), 
    or random numbers and characters to look like authentic login sites.
    
    URLs to inspect: {urls}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LinkAnalysis,
            temperature=0.1
        ),
    )
    return LinkAnalysis.model_validate_json(response.text)