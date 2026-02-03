import streamlit as st
import google.generativeai as genai
import json
import os
import pandas as pd
from io import BytesIO
import time
import re
from collections import Counter

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
        "instagram": {"name": "Instagram", "icon": "📸", "max_chars": 2200, "style": "Warm, emoji-rich"},
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
    
    # --- PAGE NAVIGATION ---
    page = st.radio(
        "📄 Select Page:",
        options=["🔍 Single Analysis", "📊 Batch Analysis"],
        index=0
    )
    
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
    st.info(f"Model: {selected_model.split('/')[-1]} ⚡")


# --- AI ANALYSIS FUNCTION ---
def get_ai_response(comment, persona, key, platform_name, platform_info, model_name, simplified=False):
    if not key:
        return "⚠️ Please enter your API Key."
    
    try:
        genai.configure(api_key=key)
        
        model = genai.GenerativeModel(model_name)
        
        # Build platform guidelines string
        guidelines = platform_info.get('guidelines', [])
        guidelines_str = "\n           ".join([f"- {g}" for g in guidelines])
        
        if simplified:
            # Simplified prompt for batch processing
            prompt = f"""
            Analyze this customer message briefly:
            Message: {comment}
            Brand: {persona}
            Platform: {platform_name}
            
            Return ONLY a JSON object (no markdown, no explanation):
            {{
                "language": "detected language",
                "priority": "Critical/High/Medium/Low",
                "urgency_score": 1-10,
                "root_cause": "brief explanation",
                "response_soft": "soft response in detected language",
                "response_balanced": "balanced response in detected language",
                "response_firm": "firm response in detected language",
                "recommended": "A/B/C"
            }}
            """
        else:
            # Full prompt for single analysis
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
            
            ### 📊 1. SITUATION ASSESSMENT
            * **Priority Level:** [Critical / High / Medium / Low]
            * **Urgency Score:** [1-10] - where 10 requires immediate attention
            * **Root Cause:** [Briefly explain the core issue and customer sentiment]
            * **Platform Impact:** [Specifically for {platform_name}, what is the potential reach/impact?]
            
            ### 🛠️ 2. OPERATIONAL SOLUTION
            List 3 concrete, actionable steps the business owner must take.
            1. [Step 1]
            2. [Step 2]
            3. [Step 3]
            
            ### 💬 3. RESPONSE OPTIONS FOR {platform_name.upper()}
            Provide THREE different response options with different tones. Each response must:
            - Be written in the DETECTED LANGUAGE from Section 0
            - Sign as "[Company Name]" or "[Brand Team]". NEVER sign as DexApt.
            - Stay under {platform_info.get('max_chars', 280)} characters
            - Follow {platform_name} platform culture
            
            #### 🟢 OPTION A: SOFT (Apologetic & Empathetic)
            Maximum empathy, deep apology, customer-first approach. Use warm language.
            
            [Write the soft response here in detected language]
            
            ---
            
            #### 🟡 OPTION B: BALANCED (Professional & Neutral)
            Professional acknowledgment, balanced tone, solution-focused.
            
            [Write the balanced response here in detected language]
            
            ---
            
            #### 🔴 OPTION C: FIRM (Assertive but Respectful)
            Confident stance, references policies if needed, maintains professionalism.
            
            [Write the firm response here in detected language]
            
            ---
            
            ### 📏 4. RESPONSE CHARACTERISTICS
            | Option | Tone | Character Count | Best For |
            |--------|------|-----------------|----------|
            | 🟢 A | Soft | [count] | High anger, loyal customers |
            | 🟡 B | Balanced | [count] | Most situations |
            | 🔴 C | Firm | [count] | Unreasonable demands, policy issues |
            
            * **Recommended Option:** [A/B/C] - [Brief reason why]
            """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error occurred: {str(e)}"


def parse_json_response(text):
    """Parse JSON from AI response"""
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None


def extract_word_frequency(messages):
    """Extract word frequency from messages"""
    all_words = []
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                  'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
                  'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                  'from', 'as', 'into', 'through', 'during', 'before', 'after',
                  'above', 'below', 'between', 'under', 'again', 'further', 'then',
                  'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                  'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                  'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't',
                  'just', 'don', 'now', 've', 'll', 'amp', 'bu', 'bir', 've', 'de',
                  'da', 'için', 'ile', 'ben', 'sen', 'o', 'biz', 'siz', 'onlar', 'i', 'and', 'but', 'or'}
    
    for msg in messages:
        if isinstance(msg, str):
            words = re.findall(r'\b[a-zA-ZğüşıöçĞÜŞİÖÇ]{3,}\b', msg.lower())
            all_words.extend([w for w in words if w not in stop_words])
    
    return Counter(all_words).most_common(30)


def create_excel_report(df, stats, word_freq):
    """Create Excel report with multiple sheets"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: All Analyses
        df.to_excel(writer, sheet_name='Analyses', index=False)
        
        # Sheet 2: Statistics
        stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        # Sheet 3: Word Frequency
        word_df = pd.DataFrame(word_freq, columns=['Word', 'Count'])
        word_df.to_excel(writer, sheet_name='Word Frequency', index=False)
    
    output.seek(0)
    return output


# ==========================================
# PAGE: SINGLE ANALYSIS
# ==========================================
if page == "🔍 Single Analysis":
    st.title("🛡️ DexApt: Social Media Crisis Analyst")
    st.markdown("Analyzes customer messages, determines **priority level** and provides **operational solution plan**.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📡 Incoming Data (Customer Complaint)")
        default_text = "I purchased your service but for 6 hours you haven't answered my calls or replied to my messages. This is disgraceful! I will report you to the highest authority and make you regret this!"
        user_comment = st.text_area("Analyze Message:", value=default_text, height=200)
        
        analyze_btn = st.button("START RISK & STRATEGY ANALYSIS", type="primary")
    
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


# ==========================================
# PAGE: BATCH ANALYSIS
# ==========================================
elif page == "📊 Batch Analysis":
    st.title("📊 Batch Analysis - Bulk Message Processing")
    st.markdown("Upload a CSV/Excel file with customer messages, analyze all at once, and export results with statistics.")
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload CSV or Excel file",
        type=['csv', 'xlsx'],
        help="File should contain a column named 'message' with customer complaints"
    )
    
    if uploaded_file:
        # Read file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File loaded: {len(df)} rows")
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10))
            
            # Column selection
            message_col = st.selectbox(
                "Select message column:",
                options=df.columns.tolist(),
                index=0 if 'message' not in df.columns else df.columns.tolist().index('message') if 'message' in df.columns else 0
            )
            
            # Rate limit setting
            delay_seconds = st.slider("⏱️ Delay between requests (seconds):", 1, 10, 3)
            
            # Start analysis button
            if st.button("🚀 START BATCH ANALYSIS", type="primary"):
                if not api_key:
                    st.error("⚠️ API Key is missing!")
                else:
                    results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total = len(df)
                    success_count = 0
                    error_count = 0
                    
                    for idx, row in df.iterrows():
                        message = str(row[message_col])
                        status_text.text(f"Analyzing {idx + 1}/{total}...")
                        
                        # Get AI response (simplified for batch)
                        response = get_ai_response(
                            message, brand_persona, api_key, 
                            selected_platform_name, platform_info, 
                            selected_model, simplified=True
                        )
                        
                        # Parse response
                        parsed = parse_json_response(response)
                        
                        if parsed:
                            results.append({
                                'Original Message': message,
                                'Language': parsed.get('language', 'Unknown'),
                                'Priority': parsed.get('priority', 'Unknown'),
                                'Urgency Score': parsed.get('urgency_score', 0),
                                'Root Cause': parsed.get('root_cause', ''),
                                'Response (Soft)': parsed.get('response_soft', ''),
                                'Response (Balanced)': parsed.get('response_balanced', ''),
                                'Response (Firm)': parsed.get('response_firm', ''),
                                'Recommended': parsed.get('recommended', 'B')
                            })
                            success_count += 1
                        else:
                            results.append({
                                'Original Message': message,
                                'Language': 'Error',
                                'Priority': 'Error',
                                'Urgency Score': 0,
                                'Root Cause': response[:200] if response else 'No response',
                                'Response (Soft)': '',
                                'Response (Balanced)': '',
                                'Response (Firm)': '',
                                'Recommended': ''
                            })
                            error_count += 1
                        
                        progress_bar.progress((idx + 1) / total)
                        
                        # Rate limiting
                        if idx < total - 1:
                            time.sleep(delay_seconds)
                    
                    status_text.text("✅ Analysis complete!")
                    
                    # Create results dataframe
                    results_df = pd.DataFrame(results)
                    
                    # Calculate statistics
                    stats = {
                        'Total Messages': total,
                        'Successfully Analyzed': success_count,
                        'Errors': error_count,
                        'Average Urgency Score': round(results_df['Urgency Score'].mean(), 2),
                        'Critical Count': len(results_df[results_df['Priority'] == 'Critical']),
                        'High Count': len(results_df[results_df['Priority'] == 'High']),
                        'Medium Count': len(results_df[results_df['Priority'] == 'Medium']),
                        'Low Count': len(results_df[results_df['Priority'] == 'Low'])
                    }
                    
                    # Word frequency
                    word_freq = extract_word_frequency(df[message_col].tolist())
                    
                    # Display results
                    st.markdown("---")
                    st.subheader("📈 Analysis Results")
                    
                    # Stats cards
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", stats['Total Messages'])
                    with col2:
                        st.metric("Avg Urgency", stats['Average Urgency Score'])
                    with col3:
                        st.metric("Critical", stats['Critical Count'], delta_color="inverse")
                    with col4:
                        st.metric("Errors", stats['Errors'], delta_color="inverse")
                    
                    # Results table
                    st.dataframe(results_df)
                    
                    # Word frequency chart
                    if word_freq:
                        st.subheader("🔤 Most Common Words")
                        word_df = pd.DataFrame(word_freq[:10], columns=['Word', 'Count'])
                        st.bar_chart(word_df.set_index('Word'))
                    
                    # Export button
                    st.markdown("---")
                    excel_file = create_excel_report(results_df, stats, word_freq)
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_file,
                        file_name="dexapt_batch_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    
    else:
        # Show sample format
        st.info("📝 **Expected file format:**")
        st.markdown("""
        Your CSV/Excel should have at least a column with customer messages:
        
        | message |
        |---------|
        | Your service is terrible! |
        | Great experience, thank you! |
        | I've been waiting for 3 days... |
        """)
        
        # Download sample file
        sample_df = pd.DataFrame({
            'message': [
                "Your service is terrible! I've been waiting for hours.",
                "Great product, but delivery was late.",
                "I want a refund immediately!",
                "The staff was very helpful, thank you!"
            ]
        })
        
        sample_csv = sample_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sample CSV",
            data=sample_csv,
            file_name="sample_messages.csv",
            mime="text/csv"
        )

st.markdown("---")
st.caption("📁 Configuration files loaded from: config/personas.json, config/platforms.json")