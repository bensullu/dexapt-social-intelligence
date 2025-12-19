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
    
    brand_persona = st.selectbox(
        "Marka Sektörü & Dili:",
        (
            "Zincir Restoran (Kurumsal ama Samimi)",
            "Lüks Giyim Markası (Mesafeli ve Seçkin)",
            "Teknoloji/SaaS Firması (Çözüm Odaklı & Teknik)",
            "Hava Yolu Şirketi (Otoriter & Güven Verici)"
        )
    )

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
    
    # 1. Google'ı Yapılandır
    try:
        genai.configure(api_key=key)
        # Model olarak 'gemini-pro' veya 'gemini-1.5-flash' kullanabilirsin. 
        # Pro en kararlısıdır.
        model = genai.GenerativeModel('gemini-pro')
        
        # 2. Prompt Hazırla
        prompt = f"""
        Sen DexApt Kriz Yönetimi Uzmanısın.
        
        DURUM:
        Marka Tipi: {persona}
        Müşteri Şikayeti: {comment}
        
        GÖREV:
        Aşağıdaki formatta bir rapor hazırla (Markdown kullan):
        
        ### 📊 1. RİSK ANALİZİ
        * **Öfke Skoru:** [1-10 Arası Puan] / 10
        * **Tespit:** [Kısa durum özeti]
        
        ### 🛠️ 2. OPERASYONEL ÇÖZÜM (Yöneticiye)
        İşletme sahibinin yapması gereken 3 adım:
        1. ...
        2. ...
        3. ...
        
        ### 💬 3. ÖNERİLEN YANIT (Müşteriye)
        Marka diline ({persona}) uygun, nazik ve çözüm odaklı yanıt metni.
        """
        
        # 3. İsteği Gönder
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
                
                # Eğer hata mesajı geldiyse kırmızı göster
                if "Hata oluştu" in result:
                    st.error(result)
                else:
                    st.markdown(result)
                    st.success("Rapor tamamlandı.")

st.markdown("---")