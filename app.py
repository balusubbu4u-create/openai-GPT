import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="OpenAI Assistant", page_icon="🤖")

st.title("🤖 OpenAI Assistant")

# Streamlit Secrets నుండి API Key ని తీసుకుంటుంది
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# యూజర్ నుండి ఇన్పుట్
prompt = st.text_area("మీ ప్రశ్న ఇక్కడ అడగండి:", height=100)

if st.button("సమాధానం ఇవ్వండి"):
    if prompt.strip():
        with st.spinner("సమాధానం సిద్ధమవుతోంది..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful and clear assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.markdown("### సమాధానం:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"ఎర్రర్ వచ్చింది: {e}")
    else:
        st.warning("దయచేసి ఏదైనా ప్రశ్నను టైప్ చేయండి.")
