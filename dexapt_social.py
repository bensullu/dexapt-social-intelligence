import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="DexApt | Crisis Intelligence", page_icon="🛡️", layout="wide")

# --- YAN MENÜ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=80) 
    st.title("DexApt Intelligence")
    st.markdown("### Google Gemini Power 🚀")
    
    # API Key Girişi
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
    default_text = "Sipariş vereli 2 saat oldu! Yemek buz gibi geldi, kuryeniz de suratıma bakıp gitti. Bu ne rezillik? Paramı hemen iade edin yoksa sizi her yere şikayet edeceğim! 😡"
    user_comment = st.text_area("Mesajı Analiz Et:", value=default_text, height=200)
    
    analyze_btn = st.button("RİSK VE STRATEJİ ANALİZİ BAŞLAT", type="primary")

# --- GELİŞMİŞ AI FONKSİYONU ---
def get_ai_response(comment, persona, key):
    if not key:
        return "⚠️ Lütfen sol menüden API Anahtarınızı giriniz."
    
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=key, temperature=0.5)
    
    # PROMPT DEĞİŞTİ: Artık analiz ve plan istiyoruz
    template = """
    Sen DexApt tarafından geliştirilmiş üst düzey bir Kriz Yönetimi Uzmanısın.
    
    GÖREV:
    Aşağıdaki müşteri şikayetini analiz et ve işletme sahibine rapor sun.
    
    BAĞLAM:
    Marka Tipi: {persona}
    Müşteri Şikayeti: {comment}
    
    İSTENEN RAPOR FORMATI (Markdown Kullan):
    
    ### 📊 1. RİSK ANALİZİ
    * **Öfke Skoru:** [1'den 10'a kadar bir sayı ver] / 10
    * **Tespit:** [Müşterinin asıl derdi ne? Kısaca yaz]
    * **Potansiyel Tehlike:** [Bu yorum viral olur mu? Markaya zarar verir mi?]
    
    ### 🛠️ 2. OPERASYONEL ÇÖZÜM PLANI (Yönetici İçin)
    İşletmenin bu sorunu kökten çözmesi için yapması gereken 3 somut adımı maddeler halinde yaz. (Örn: "Kurye ile görüş", "Kamera kaydına bak" vb.)
    1. ...
    2. ...
    3. ...
    
    ### 💬 3. ÖNERİLEN YANIT TASLAĞI
    Markanın diline ({persona}) uygun, müşteriyi sakinleştiren ve çözüme yönlendiren nihai cevap metni.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"persona": persona, "comment": comment})

# --- SONUÇ EKRANI ---
with col2:
    st.subheader("📈 DexApt Raporu")
    
    if analyze_btn:
        if not api_key:
            st.error("⚠️ Sol tarafa API Key girilmeli!")
        else:
            with st.spinner('Öfke seviyesi ölçülüyor ve aksiyon planı hazırlanıyor...'):
                try:
                    result = get_ai_response(user_comment, brand_persona, api_key)
                    st.markdown(result)
                    st.success("Rapor başarıyla oluşturuldu.")
                except Exception as e:
                    st.error(f"Hata: {e}")

st.markdown("---")