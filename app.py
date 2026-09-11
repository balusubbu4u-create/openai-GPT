import streamlit as st
from openai import OpenAI
import pdfplumber
from PIL import Image

st.set_page_config(page_title="AI Document Assistant", page_icon="📄")

st.title("📄 AI Document & Assistant (PDF, JPG, PNG)")

# Streamlit Secrets నుండి API Key తీసుకుంటుంది
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# డాక్యుమెంట్ అప్‌లోడ్ చేయడానికి ట్యాబ్ లేదా ఫైల్ అప్లోడర్
uploaded_file = st.file_uploader(
    "ఒక PDF లేదా ఇమేజ్ (JPG/PNG) ఫైల్‌ని అప్‌లోడ్ చేయండి:", 
    type=["pdf", "png", "jpg", "jpeg"]
)

extracted_text = ""

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    # 1. PDF ఫైల్ అయితే రీడ్ చేయడం
    if file_extension == "pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        st.success("PDF విజయవంతంగా రీడ్ చేయబడింది!")
        
    # 2. Image (JPG/PNG) ఫైల్ అయితే ప్రివ్యూ చూపించడం
    elif file_extension in ["png", "jpg", "jpeg"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="అప్‌లోడ్ చేసిన ఇమేజ్", use_container_width=True)
        extracted_text = "[ఇది ఒక ఇమేజ్ ఫైల్. దీనికి సంబంధించిన ప్రశ్నలకు తగినట్లు సమాధానం ఇవ్వు.]"

# యూజర్ ప్రశ్న అడగడానికి టెక్స్ట్ బాక్స్
user_query = st.text_area("ఈ డాక్యుమెంట్‌కి సంబంధించి మీ ప్రశ్న ఏమిటి?", height=100)

if st.button("సమాధానం పొందండి"):
    if user_query.strip():
        with st.spinner("AI విశ్లేషిస్తోంది..."):
            try:
                # ప్రాంప్ట్ తయారీ
                full_prompt = f"డాక్యుమెంట్ సమాచారం:\n{extracted_text}\n\nప్రశ్న: {user_query}"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "మీరు ఒక అసిస్టెంట్, అప్‌లోడ్ చేసిన డాక్యుమెంట్ ఆధారంగా యూజర్ అడిగిన ప్రశ్నలకు సమాధానం ఇవ్వండి."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                st.markdown("### 🤖 సమాధానం:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"ఎర్రర్ వచ్చింది: {e}")
    else:
        st.warning("దయచేసి ప్రశ్నను టైప్ చేయండి.")
