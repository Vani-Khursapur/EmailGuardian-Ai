from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Import the specialized analytics agents we built in Steps 2 & 3
from .phishing_agent import analyze_phishing, PhishingAnalysis
from .language_agent import analyze_language, LanguageAnalysis
from .link_agent import analyze_links, LinkAnalysis

# Schema for the internal Risk Scoring Agent
class RiskAssessment(BaseModel):
    overall_risk_score: int = Field(description="Calculated final security threat score from 0 to 100")
    key_reasons: list[str] = Field(description="Primary threat indicators extracted from the combined telemetry")

# Schema for the final user-facing Recommendation Agent report
class FinalReport(BaseModel):
    verdict: str = Field(description="Clear absolute threat state: 'Likely Safe', 'Suspicious', or 'High Risk Phishing'")
    risk_score: int
    reasons: list[str]
    recommendations: list[str] = Field(description="List of exact actionable steps for the user (e.g., 'Do NOT click links', 'Report sender')")

def run_guardian_pipeline(client: genai.Client, email_text: str) -> tuple[PhishingAnalysis, LanguageAnalysis, LinkAnalysis, FinalReport]:
    """
    Orchestrates the entire execution chain, routing data through analysis sub-agents 
    and consolidating results into a structured threat report.
    """
    # Step A: Run individual feature-extraction agents
    phishing_res = analyze_phishing(client, email_text)
    language_res = analyze_language(client, email_text)
    link_res = analyze_links(client, email_text)
    
    # Step B: Pass compiled metrics directly to the Risk Score Synthesis Agent
    risk_prompt = f"""
    You are the Risk Score Agent. Evaluate the compiled metadata vectors from our specialized agents 
    and calculate a unified, data-backed numerical threat percentage (0 to 100).
    
    Phishing Metrics: {phishing_res.model_dump_json()}
    Language Metrics: {language_res.model_dump_json()}
    Link Metrics: {link_res.model_dump_json()}
    """
    
    risk_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=risk_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RiskAssessment,
            temperature=0.1
        ),
    )
    risk_res = RiskAssessment.model_validate_json(risk_response.text)
    
    # Step C: Pipe the synthesized risk score into the final Recommendation Agent
    rec_prompt = f"""
    You are the Recommendation Agent. Generate a definitive, human-readable investigation dossier 
    and explicit actionable safety tasks based on this risk assessment context:
    
    Threat Risk Level: {risk_res.overall_risk_score}%
    Flagged Threat Triggers: {risk_res.key_reasons}
    """
    
    rec_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=rec_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FinalReport,
            temperature=0.2
        ),
    )
    final_report = FinalReport.model_validate_json(rec_response.text)
    
    return phishing_res, language_res, link_res, final_report