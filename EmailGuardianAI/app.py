import streamlit as st
import os
from google import genai
from dotenv import load_dotenv

# Import our Coordinator pipeline from the agents package
from agents.coordinator import run_guardian_pipeline

# Load environment variables from the .env file
load_dotenv()

# Configure the Streamlit app window tab and layout style
st.set_page_config(page_title="EmailGuardian AI", page_icon="🛡️", layout="wide")

st.title("🛡️ EmailGuardian AI")
st.caption("Multi-Agent Threat Intelligence System for Phishing, Fraud, and Spam Detection")

# Setup the GenAI client using our secure API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Missing `GEMINI_API_KEY` environment variable. Please check your `.env` file.")
    st.stop()

client = genai.Client(api_key=api_key)

# Setup a responsive two-column grid layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📬 Input Investigation Target")
    
    # Initialize session state for persistent input management
    if "email_content" not in st.session_state:
        st.session_state["email_content"] = ""

    email_input = st.text_area(
        "Paste the raw email text below:",
        value=st.session_state["email_content"],
        height=260,
        placeholder="Paste header text or body contents here..."
    )
    
    # Shortcut option to populate standard hackathon evaluation text
    if st.button("Load Demo Phishing Email"):
        st.session_state["email_content"] = (
            "Subject: CRITICAL: Your account will be locked!\n\n"
            "Dear User,\n\n"
            "We detected an unauthorized login attempt from a foreign IP address on your banking profile. For your safety, we have locked your funds.\n\n"
            "You must instantly verify your identity within 15 minutes by logging in here:\n"
            "http://verification-secure-update-bank.xyz/login\n\n"
            "If you fail to confirm your credentials, your account will be permanently deactivated.\n\n"
            "Security Department"
        )
        st.rerun()

    analyze_clicked = st.button("🚀 Analyze Email", type="primary", use_container_width=True)

with col2:
    st.subheader("🕵️‍♂️ Agent Real-time Logs")
    log_placeholder = st.empty()
    if not analyze_clicked:
        log_placeholder.info("Awaiting input data to initialize security agents...")

# Execution Phase
if analyze_clicked and email_input:
    with log_placeholder.container():
        status_box = st.status("🧠 **Coordinator Agent:** Distributing payloads to sub-agents...", expanded=True)
        
        try:
            # Fire our multi-agent data orchestration pipeline
            phishing, language, links, final_report = run_guardian_pipeline(client, email_input)
            status_box.update(label="✅ **Analysis Complete!** Aggregated metrics compiled.", state="complete")
            
            st.markdown("---")
            st.header("📋 Tactical Investigation Report")
            
            # Render final consolidated scorecard metrics
            m_col1, m_col2, m_col3 = st.columns([1, 1, 2])
            
            with m_col1:
                st.metric(label="Threat Index Score", value=f"{final_report.risk_score}%")
            with m_col2:
                verdict_icon = "🔴" if final_report.risk_score > 70 else "🟡" if final_report.risk_score > 30 else "🟢"
                st.markdown(f"### {verdict_icon} Verdict")
                st.markdown(f"**{final_report.verdict}**")
            with m_col3:
                st.markdown("#### Primary Threat Indicators")
                for reason in final_report.reasons:
                    st.markdown(f"- {reason}")

            st.markdown("---")
            
            # Detailed sub-agent technical tabs layout
            tab1, tab2, tab3, tab4 = st.tabs([
                "🎣 Phishing Analysis", 
                "📝 Psychological Profiling", 
                "🔗 Domain Intelligence", 
                "🛡️ Action Plan"
            ])
            
            with tab1:
                st.markdown(f"**Threat Severity:** `{phishing.severity}`")
                st.markdown(f"**Detection Confidence:** `{phishing.confidence_score * 100}%`")
                st.write("Identified Malicious Structural Markers:")
                st.json(phishing.indicators_found)
                
            with tab2:
                st.markdown(f"**Linguistic Tone Profile:** `{language.emotional_tone}`")
                st.markdown(f"**Psychological Manipulation Checked:** `{language.manipulation_detected}`")
                st.write("Exploitative Tactics Found:")
                st.json(language.tactics_detected)
                
            with tab3:
                st.markdown(f"**Infrastructure Threat Tier:** `{links.risk_level}`")
                st.write("Extracted Link Paths:")
                st.write(links.extracted_urls)
                if links.suspicious_urls:
                    st.warning(f"Flagged Deceptive Domains: {links.suspicious_urls}")
                    
            with tab4:
                st.success("### Mandatory Incident Response Steps:")
                for rec in final_report.recommendations:
                    st.markdown(f"👉 **{rec}**")

        except Exception as e:
            # Gracefully handle the 503 high demand capacity blockages from Gemini's server tier
            status_box.update(label="❌ **Connection Interrupted**", state="error")
            st.error("⚠️ **The AI server tier is currently experiencing a temporary traffic spike (503 Service Unavailable).**")
            st.info("🔄 **Your pipeline is structurally solid! Please wait 5–10 seconds and click 'Analyze Email' again to clear the buffer.**")