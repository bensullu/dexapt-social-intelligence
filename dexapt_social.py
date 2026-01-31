import streamlit as st
import google.generativeai as genai
import json
import os

# --- LOAD CONFIGURATION FILES ---
def load_config():
    """Load personas and platforms from config files"""
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    
    # Load personas
    personas_path = os.path.join(config_dir, 'personas.json')
    try:
        with open(personas_path, 'r', encoding='utf-8') as f:
            personas = json.load(f)
    except FileNotFoundError:
        personas = get_default_personas()
    
    # Load platforms
    platforms_path = os.path.join(config_dir, 'platforms.json')
    try:
        with open(platforms_path, 'r', encoding='utf-8') as f:
            platforms = json.load(f)
    except FileNotFoundError:
        platforms = get_default_platforms()
    
    # Load prompt rules
    rules_path = os.path.join(config_dir, 'prompt_rules.md')
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            prompt_rules = f.read()
    except FileNotFoundError:
        prompt_rules = ""
    
    return personas, platforms, prompt_rules

def get_default_personas():
    """Fallback personas if config file not found"""
    return {
        "chain_restaurant": {
            "name_en": "Chain Restaurant (Corporate but Friendly)",
            "description": "Corporate but Friendly, Welcoming, Sincere"
        },
        "luxury_fashion": {
            "name_en": "Luxury Fashion Brand (Exclusive & Elite)",
            "description": "High-end, Exclusive, Professional, Distant and Elite"
        },
        "tech_saas": {
            "name_en": "Tech/SaaS Company (Solution-Oriented)",
            "description": "Solution Oriented, Technical, Analytical, Professional"
        },
        "airline": {
            "name_en": "Airline Company (Authoritative & Trustworthy)",
            "description": "Authoritative, Trustworthy, Formal, Serious and Safe"
        }
    }

def get_default_platforms():
    """Fallback platforms if config file not found"""
    return {
        "twitter": {"name": "Twitter/X", "icon": "🐦", "max_chars": 280, "style": "Concise, punchy"},
        "instagram": {"name": "Instagram", "icon": "�", "max_chars": 2200, "style": "Warm, emoji-rich"},
        "facebook": {"name": "Facebook", "icon": "👥", "max_chars": 8000, "style": "Detailed, community-focused"},
        "linkedin": {"name": "LinkedIn", "icon": "💼", "max_chars": 3000, "style": "Professional, corporate"},
        "google_reviews": {"name": "Google Reviews", "icon": "⭐", "max_chars": 4000, "style": "Polite, SEO-friendly"}
    }

# Load configurations
PERSONAS, PLATFORMS, PROMPT_RULES = load_config()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DexApt | Crisis Intelligence", page_icon="pp.png", layout="wide")

st.markdown(
    """
    <style>
    /* Sidebar Background: Modern Dark Anthracite */
    [data-testid="stSidebar"] {
        background-color: #1A1C24;
        border-right: 1px solid #2D2F3B;
    }
    /* Sidebar Text Colors */
    [data-testid="stSidebar"] .css-1d391kg {
        color: #E0E0E0;
    }
    /* Make Headings More Readable */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("pp.png", width=120) 
    except:
        st.warning("Logo Not Found")
    st.title("DexApt Intelligence")
    st.markdown("### Google Gemini Power 🚀")
    
    # API Key Management
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ System Connected (Auto)")
    else:
        api_key = st.text_input("Google API Key:", type="password", placeholder="AIzaSy...")
    
    # --- MODEL SELECTION ---
    available_models = [
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-2.0-flash-lite",
        "models/gemini-flash-latest",
        "models/gemini-pro-latest"
    ]
    
    selected_model = st.selectbox(
        "🤖 AI Model:",
        options=available_models,
        index=0
    )
    
    # List models button (debug)
    if api_key and st.button("🔍 List Available Models"):
        try:
            genai.configure(api_key=api_key)
            models = genai.list_models()
            model_names = [m.name for m in models if 'generateContent' in str(m.supported_generation_methods)]
            st.code("\n".join(model_names))
        except Exception as e:
            st.error(f"Error: {e}")
        
    st.markdown("---")
    
    # --- PERSONA SELECTION (from config) ---
    persona_options = {p["name_en"]: p["description"] for p in PERSONAS.values()}
    
    selected_persona_name = st.selectbox(
        "Brand Sector & Tone:",
        options=list(persona_options.keys())
    )
    
    brand_persona = persona_options[selected_persona_name]
    
    st.markdown("---")
    
    # --- PLATFORM SELECTION (from config) ---
    platform_options = {p["name"]: key for key, p in PLATFORMS.items()}
    
    selected_platform_name = st.selectbox(
        "📱 Target Platform:",
        options=list(platform_options.keys()),
        format_func=lambda x: f"{PLATFORMS[platform_options[x]]['icon']} {x}"
    )
    
    platform_key = platform_options[selected_platform_name]
    platform_info = PLATFORMS[platform_key]
    
    st.caption(f"📏 Max Characters: **{platform_info['max_chars']}**")
    st.caption(f"🎯 Tone: {platform_info.get('tone_en', platform_info.get('style', ''))}")
    
    st.markdown("---")
    st.info(f"Model: Gemini Flash Latest ⚡")

# --- MAIN SCREEN ---
st.title("🛡️ DexApt: Social Media Crisis Analyst")
st.markdown("Analyzes customer messages, determines **risk score** and provides **operational solution plan**.")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📡 Incoming Data (Customer Complaint)")
    default_text = "I purchased your service but for 6 hours you haven't answered my calls or replied to my messages. This is disgraceful! I will report you to the highest authority and make you regret this!"
    user_comment = st.text_area("Analyze Message:", value=default_text, height=200)
    
    analyze_btn = st.button("START RISK & STRATEGY ANALYSIS", type="primary")

# --- GOOGLE AI FUNCTION ---
def get_ai_response(comment, persona, key, platform_name, platform_info, model_name):
    if not key:
        return "⚠️ Please enter your API Key."
    
    try:
        genai.configure(api_key=key)
        
        model = genai.GenerativeModel(model_name)
        
        # Build platform guidelines string
        guidelines = platform_info.get('guidelines', [])
        guidelines_str = "\n           ".join([f"- {g}" for g in guidelines])
        
        # PROMPT: PLATFORM-BASED + AUTO LANGUAGE DETECTION
        prompt = f"""
        You are a Senior Crisis Management Expert developed by DexApt.
        
        INPUT DATA:
        - Brand Persona: {persona}
        - Customer Message: {comment}
        - Target Platform: {platform_name}
        - Platform Style: {platform_info.get('style', '')}
        - Max Characters for Response: {platform_info.get('max_chars', 280)}
        - Platform Guidelines:
           {guidelines_str}
        
        MISSION:
        1. DETECT the language of the customer message.
        2. Analyze the message and generate a strategic report.
        3. Write the recommended response IN THE SAME LANGUAGE as the message.
        
        CRITICAL RULES:
        1. AUTOMATIC LANGUAGE DETECTION (MOST IMPORTANT RULE):
           - First, detect the language of the customer message (complaint, review, or feedback).
           - The recommended response in Section 3 MUST be written ENTIRELY in the DETECTED language.
           - THIS IS MANDATORY - DO NOT write the response in any other language.
           - Examples:
             * If message is in Polish → response MUST be in Polish
             * If message is in Turkish → response MUST be in Turkish
             * If message is in English → response MUST be in English
             * If message is in German → response MUST be in German
             * If message is in French → response MUST be in French
             * If message is in Spanish → response MUST be in Spanish
             * And so on for ANY language detected.
           - NEVER translate the response to a different language.
        
        2. IDENTITY SEPARATION:
           - In Section 1 and 2, you are DexApt (The Analyst), talking to the business owner.
           - In Section 3, you are acting AS THE BRAND ITSELF ({persona}). 
           - DO NOT MENTION 'DexApt' IN SECTION 3. You are the company answering the customer.
        
        3. PLATFORM-SPECIFIC RESPONSE:
           The response in Section 3 MUST be tailored for {platform_name}:
           - Style: {platform_info.get('style', '')}
           - Character Limit: Stay under {platform_info.get('max_chars', 280)} characters
           - Follow platform guidelines strictly
        
        4. NO ABBREVIATIONS:
           - Do not use obscure acronyms without explanation.
        
        OUTPUT FORMAT (Use Markdown):
        
        ### 🌍 0. LANGUAGE DETECTION
        * **Detected Language:** [Language name]
        * **Confidence:** [High/Medium/Low]
        
        ### 📊 1. RISK ANALYSIS
        * **Anger Score:** [Score between 1-10] / 10
        * **Detection:** [Briefly explain the root cause and sentiment]
        * **Risk Status:** [High/Medium/Low]
        * **Platform Risk Note:** [Specifically for {platform_name}, what is the risk?]
        
        ### 🛠️ 2. OPERATIONAL SOLUTION
        List 3 concrete, actionable steps the business owner must take.
        1. [Step 1]
        2. [Step 2]
        3. [Step 3]
        
        ### 💬 3. RECOMMENDED RESPONSE FOR {platform_name.upper()}
        Write a response specifically formatted for {platform_name}.
        - CRITICAL: Write this response in the DETECTED LANGUAGE from Section 0.
        - Sign as "[Company Name]" or "[Brand Team]". NEVER sign as DexApt.
        - Tone: Must match the '{persona}' AND {platform_name} platform culture.
        - Max Length: {platform_info.get('max_chars', 280)} characters
        
        ### 📏 4. RESPONSE CHARACTERISTICS
        * **Response Language:** [Same as detected language]
        * **Character Count:** [Exact character count]
        * **Platform Compliance:** [Yes/No with brief explanation]
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error occurred: {str(e)}"

# --- RESULT SCREEN ---
with col2:
    st.subheader("📈 DexApt Report")
    
    if analyze_btn:
        if not api_key:
            st.error("⚠️ API Key is missing!")
        else:
            with st.spinner('DexApt connecting to servers...'):
                result = get_ai_response(user_comment, brand_persona, api_key, selected_platform_name, platform_info, selected_model)
                if "Error occurred" in result:
                    st.error(result)
                else:
                    st.markdown(result)
                    st.success("Report completed.")

st.markdown("---")

# --- FOOTER ---
st.caption("📁 Configuration files loaded from: config/personas.json, config/platforms.json")