import streamlit as st
import google.generativeai as genai
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="DexApt | Crisis Intelligence", page_icon="🛡️", layout="wide")

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=80) 
    st.title("DexApt Intelligence")
    st.markdown("### Google Gemini Power 🚀")
    
    # API Anahtarı Yönetimi
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Sistem Bağlı (Auto)")
    else:
        api_key = st.text_input("Google API Key:", type="password", placeholder="AIzaSy...")
        
    st.markdown("---")
    
    # --- AKILLI PERSONA SİSTEMİ (VİTRİN TÜRKÇE, DEPO İNGİLİZCE) ---
    # GÜNCELLEME: "Geeky" ifadesini kaldırdık, "Professional" ekledik.
    persona_map = {
        "Zincir Restoran (Kurumsal ama Samimi)": "Chain Restaurant (Corporate but Friendly, Welcoming, sincere)",
        "Lüks Giyim Markası (Mesafeli ve Seçkin)": "Luxury Fashion Brand (High-end, Exclusive, Professional, Distant and Elite)",
        "Teknoloji/SaaS Firması (Çözüm Odaklı & Teknik)": "Tech/SaaS Company (Solution Oriented, Technical, Analytical, Professional)",
        "Hava Yolu Şirketi (Otoriter & Güven Verici)": "Airline Company (Authoritative, Trustworthy, Formal, Serious and Safe)"
    }
    
    selected_option = st.selectbox(
        "Marka Sektörü & Dili:",
        options=list(persona_map.keys())
    )
    
    brand_persona = persona_map[selected_option]
    
    st.info(f"Model: Gemini Flash Latest ⚡")

# --- ANA EKRAN ---
st.title("🛡️ DexApt: Sosyal Medya Kriz Analisti")
st.markdown("Müşteri mesajını analiz eder, **risk skorunu** belirler ve **operasyonel çözüm planı** sunar.")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📡 Gelen Veri (Müşteri Şikayeti)")
    default_text = "Hizmetinizi satın aldım ancak 6 saattir ne telefonumu açıyorsunuz ne mesajıma dönüyorsunuz bu ne rezillik sizi en üst makama şikayet edip sürüm sürüm süründüreceğim"
    user_comment = st.text_area("Mesajı Analiz Et:", value=default_text, height=200)
    
    analyze_btn = st.button("RİSK VE STRATEJİ ANALİZİ BAŞLAT", type="primary")

# --- SAFKAN GOOGLE AI FONKSİYONU ---
def get_ai_response(comment, persona, key):
    if not key:
        return "⚠️ Lütfen API Anahtarı giriniz."
    
    try:
        genai.configure(api_key=key)
        
        model = genai.GenerativeModel('models/gemini-flash-latest')
        
        # PROMPT GÜNCELLEMESİ: Plaza Dili Yasağı Eklendi
        prompt = f"""
        You are a Senior Crisis Management Expert developed by DexApt.
        
        INPUT DATA:
        - Brand Persona: {persona}
        - Customer Complaint: {comment}
        
        MISSION:
        Analyze the complaint and generate a strategic report for the business owner.
        
        CRITICAL RULES: 
        1. **THE FINAL OUTPUT MUST BE STRICTLY IN TURKISH.**
        2. **NO 'PLAZA LANGUAGE':** Do not mix English words into Turkish sentences (e.g., do NOT use words like 'Latency', 'Bottleneck', 'Uplink', 'Post-purchase' inside the Turkish text). Translate technical terms into professional Turkish (e.g., use 'Gecikme' instead of 'Latency').
        
        OUTPUT FORMAT (Use Markdown):
        
        ### 📊 1. RİSK ANALİZİ (RISK ANALYSIS)
        * **Öfke Skoru (Anger Score):** [Score between 1-10] / 10
        * **Tespit (Detection):** [Briefly explain the root cause and the customer's sentiment in Turkish]
        * **Risk Durumu:** [Is this a viral risk? High/Medium/Low?]
        
        ### 🛠️ 2. OPERASYONEL ÇÖZÜM (OPERATIONAL PLAN)
        List 3 concrete, actionable steps the business owner must take internally.
        1. [Step 1 in Turkish - Use technical concepts but Turkish names]
        2. [Step 2 in Turkish]
        3. [Step 3 in Turkish]
        
        ### 💬 3. ÖNERİLEN YANIT (DRAFT RESPONSE)
        Write a reply to the customer.
        - Tone: Must match the '{persona}' strictly.
        - Content: Apologetic but professional, solution-oriented.
        - Language: Pure, Professional Turkish (No English jargon).
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

# --- SONUÇ EKRANI ---
with col2:
    st.subheader("📈 DexApt Raporu")
    
    if analyze_btn:
        if not api_key:
            st.error("⚠️ API Key eksik!")
        else:
            with st.spinner('DexApt sunuculara bağlanıyor...'):
                result = get_ai_response(user_comment, brand_persona, api_key)
                if "Hata oluştu" in result:
                    st.error(result)
                else:
                    st.markdown(result)
                    st.success("Rapor tamamlandı.")

st.markdown("---")