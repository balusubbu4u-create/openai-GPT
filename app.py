import streamlit as st
from openai import OpenAI
import pdfplumber
from PIL import Image
import base64

st.set_page_config(page_title="AI Document Assistant", page_icon="📄")

st.title("📄 AI Document Assistant (PDF & Images)")

# Secrets నుండి API Key తీసుకుంటుంది
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ఫైల్ అప్‌లోడర్
uploaded_file = st.file_uploader(
    "PDF లేదా ఇమేజ్ (JPG/PNG) ఫైల్‌ని అప్‌లోడ్ చేయండి:", 
    type=["pdf", "png", "jpg", "jpeg"]
)

extracted_text = ""
base64_image = None
file_type = None

if uploaded_file is not None:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    
    # 1. PDF అయితే టెక్స్ట్ తీయడం
    if file_ext == "pdf":
        file_type = "pdf"
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        if extracted_text.strip():
            st.success("✅ PDF విజయవంతంగా చదవబడింది!")
        else:
            st.warning("⚠️ PDF లో టెక్స్ట్ లభించలేదు (ఇది స్కాన్ చేసిన ఇమేజ్ కావచ్చు).")
            
    # 2. JPG/PNG ఇమేజ్ అయితే
    elif file_ext in ["png", "jpg", "jpeg"]:
        file_type = "image"
        image = Image.open(uploaded_file)
        st.image(image, caption="అప్‌లోడ్ చేసిన ఇమేజ్", use_container_width=True)
        # ఇమేజ్‌ని Base64 లోకి మార్చడం (OpenAI Vision కోసం)
        uploaded_file.seek(0)
        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
        st.success("✅ ఇమేజ్ విజయవంతంగా అప్‌లోడ్ అయ్యింది!")

# యూజర్ ప్రశ్న (ఐచ్ఛికం - Optional)
user_query = st.text_area(
    "ఈ డాక్యుమెంట్‌పై మీ ప్రశ్న ఏమిటి? (ఏమీ టైప్ చేయకపోతే పూర్తి సారాంశం ఇస్తుంది):", 
    height=80
)

if st.button("విశ్లేషించండి / సమాధానం ఇవ్వండి"):
    # యూజర్ ఏమీ టైప్ చేయకపోతే డీఫాల్ట్ ప్రాంప్ట్ తీసుకోవడం
    actual_query = user_query.strip() if user_query.strip() else "దయచేసి ఈ డాక్యుమెంట్/ఇమేజ్ లోని పూర్తి వివరాలను క్షుణ్ణంగా పరిశీలించి ముఖ్యమైన సారాంశాన్ని తెలుగులో వివరించండి."

    if uploaded_file is None and not user_query.strip():
        st.warning("దయచేసి ఒక ఫైల్ అప్‌లోడ్ చేయండి లేదా ఏదైనా ప్రశ్న టైప్ చేయండి.")
    else:
        with st.spinner("AI పరిశీలిస్తోంది... సమాధానం సిద్ధమవుతోంది..."):
            try:
                # కేస్ 1: ఇమేజ్ ఫైల్ అయితే OpenAI Vision మోడల్ వాడటం
                if file_type == "image" and base64_image:
                    mime_type = "image/png" if file_ext == "png" else "image/jpeg"
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": actual_query},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                # కేస్ 2: PDF లేదా కేవలం టెక్స్ట్ ప్రశ్న అయితే
                else:
                    content_text = f"డాక్యుమెంట్ టెక్స్ట్:\n{extracted_text}\n\nప్రశ్న/టాస్క్: {actual_query}" if extracted_text else actual_query
                    messages = [
                        {"role": "system", "content": "మీరు డాక్యుమెంట్లను క్షుణ్ణంగా చదివి విశ్లేషించే నిపుణులైన AI అసిస్టెంట్."},
                        {"role": "user", "content": content_text}
                    ]

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                st.markdown("### 🤖 సమాధానం / ఫలితం:")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"ఎర్రర్ వచ్చింది: {e}")
