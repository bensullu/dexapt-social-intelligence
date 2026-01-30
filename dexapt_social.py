import streamlit as st
import google.generativeai as genai
import os

LOGO_URL = ""
# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DexApt | Crisis Intelligence", page_icon="pp.png", layout="wide")

st.markdown(
    """
    <style>
    /* Sidebar Background: Modern Dark Anthracite */
    [data-testid="stSidebar"] {
        background-color: #1A1C24;
        border-right: 1px solid #2D2F3B; /* Subtle separator line */
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
        
    st.markdown("---")
    
    # --- SMART PERSONA SYSTEM ---
    persona_map = {
        "Chain Restaurant (Corporate but Friendly)": "Chain Restaurant (Corporate but Friendly, Welcoming, Sincere)",
        "Luxury Fashion Brand (Exclusive & Elite)": "Luxury Fashion Brand (High-end, Exclusive, Professional, Distant and Elite)",
        "Tech/SaaS Company (Solution-Oriented)": "Tech/SaaS Company (Solution Oriented, Technical, Analytical, Professional)",
        "Airline Company (Authoritative & Trustworthy)": "Airline Company (Authoritative, Trustworthy, Formal, Serious and Safe)"
    }
    
    selected_option = st.selectbox(
        "Brand Sector & Tone:",
        options=list(persona_map.keys())
    )
    
    brand_persona = persona_map[selected_option]
    
    st.markdown("---")
    
    # --- PLATFORM-BASED RESPONSE SYSTEM ---
    platform_map = {
        "Twitter/X": {
            "icon": "🐦",
            "max_chars": 280,
            "tone": "Short, concise and direct. Hashtags allowed. Emoji-friendly.",
            "style": "Concise, punchy, use 1-2 relevant hashtags, max 280 chars, emoji-friendly"
        },
        "Instagram": {
            "icon": "📸",
            "max_chars": 2200,
            "tone": "Warm, friendly and visual-focused. Heavy emoji usage.",
            "style": "Warm, friendly, emoji-rich, visually descriptive, can be longer and more personal"
        },
        "Facebook": {
            "icon": "👥",
            "max_chars": 8000,
            "tone": "Detailed, explanatory and community-focused. Formal yet warm.",
            "style": "Detailed, explanatory, community-focused, formal yet warm, can include full context"
        },
        "LinkedIn": {
            "icon": "💼",
            "max_chars": 3000,
            "tone": "Professional, corporate and solution-oriented. Business language.",
            "style": "Professional, corporate, solution-oriented, business language, thought-leadership tone"
        },
        "Google Reviews": {
            "icon": "⭐",
            "max_chars": 4000,
            "tone": "Polite, solution-offering and SEO-friendly. May include keywords.",
            "style": "Polite, solution-offering, SEO-friendly, keyword-aware, reputation-focused"
        }
    }
    
    selected_platform = st.selectbox(
        "📱 Target Platform:",
        options=list(platform_map.keys()),
        format_func=lambda x: f"{platform_map[x]['icon']} {x}"
    )
    
    platform_info = platform_map[selected_platform]
    
    st.caption(f"📏 Max Characters: **{platform_info['max_chars']}**")
    st.caption(f"🎯 Tone: {platform_info['tone']}")
    
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
def get_ai_response(comment, persona, key, platform_name, platform_info):
    if not key:
        return "⚠️ Please enter your API Key."
    
    try:
        genai.configure(api_key=key)
        
        model = genai.GenerativeModel('models/gemini-flash-latest')
        
        # PROMPT: PLATFORM-BASED + AUTO LANGUAGE DETECTION
        prompt = f"""
        You are a Senior Crisis Management Expert developed by DexApt.
        
        INPUT DATA:
        - Brand Persona: {persona}
        - Customer Complaint: {comment}
        - Target Platform: {platform_name}
        - Platform Style: {platform_info['style']}
        - Max Characters for Response: {platform_info['max_chars']}
        
        MISSION:
        1. DETECT the language of the customer complaint.
        2. Analyze the complaint and generate a strategic report.
        3. Write the recommended response IN THE SAME LANGUAGE as the complaint.
        
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
             * If message is in Czech → response MUST be in Czech
             * If message is in Arabic → response MUST be in Arabic
             * And so on for ANY language detected.
           - NEVER translate the response to a different language. Keep it in the original message language.
        
        2. IDENTITY SEPARATION:
           - In Section 1 and 2, you are DexApt (The Analyst), talking to the business owner (always in English).
           - In Section 3, you are acting AS THE BRAND ITSELF ({persona}). 
           - DO NOT MENTION 'DexApt' IN SECTION 3. You are the company answering the customer.
        
        3. PLATFORM-SPECIFIC RESPONSE:
           The response in Section 3 MUST be tailored for {platform_name}:
           - Style: {platform_info['style']}
           - Character Limit: Stay under {platform_info['max_chars']} characters
           - Twitter/X: Use 1-2 hashtags, keep it punchy and concise
           - Instagram: Use emojis generously, be warm and personal
           - LinkedIn: Be professional, corporate, and thought-leadership focused
           - Facebook: Be detailed, explanatory, and community-focused
           - Google Reviews: Be polite, solution-focused, and reputation-aware
        
        4. NO ABBREVIATIONS:
           - Do not use obscure acronyms like MTTR/SLA without explanation.
        
        OUTPUT FORMAT (Use Markdown):
        
        ### 🌍 0. LANGUAGE DETECTION
        * **Detected Language:** [Language name, e.g., Turkish, English, German, French, etc.]
        * **Confidence:** [High/Medium/Low]
        
        ### 📊 1. RISK ANALYSIS
        * **Anger Score:** [Score between 1-10] / 10
        * **Detection:** [Briefly explain the root cause and the customer's sentiment]
        * **Risk Status:** [Is this a viral risk? High/Medium/Low?]
        * **Platform Risk Note:** [Specifically for {platform_name}, what is the viral/reputation risk?]
        
        ### 🛠️ 2. OPERATIONAL SOLUTION
        List 3 concrete, actionable steps the business owner must take internally.
        1. [Step 1]
        2. [Step 2]
        3. [Step 3]
        
        ### 💬 3. RECOMMENDED RESPONSE FOR {platform_name.upper()}
        Write a response specifically formatted for {platform_name}.
        - CRITICAL: Write this response in the DETECTED LANGUAGE from Section 0.
        - Sign as "[Company Name]" or "[Brand Team]". NEVER sign as DexApt.
        - Tone: Must match both the '{persona}' AND the {platform_name} platform culture.
        - Style: {platform_info['style']}
        - Max Length: {platform_info['max_chars']} characters
        - Content: Apologetic but professional, solution-oriented.
        
        ### 📏 4. RESPONSE CHARACTERISTICS
        * **Response Language:** [Same as detected language]
        * **Character Count:** [Exact character count of the response in Section 3]
        * **Platform Compliance:** [Is the response appropriate for {platform_name}? Yes/No with brief explanation]
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
                result = get_ai_response(user_comment, brand_persona, api_key, selected_platform, platform_info)
                if "Error occurred" in result:
                    st.error(result)
                else:
                    st.markdown(result)
                    st.success("Report completed.")

st.markdown("---")