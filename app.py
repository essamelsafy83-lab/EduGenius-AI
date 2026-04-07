import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
import json
import random
import re
from gtts import gTTS
import base64
from io import BytesIO

genai.configure(api_key="AIzaSyAk5vJhLzF98iU3bMroWhxRVSitTpV1DcE")

def get_direction(text):
    if re.search(r'[\u0600-\u06FF]', str(text)):
        return "rtl"
    return "ltr"

def text_to_speech_html(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    
    audio_html = f"""
        <audio id="audio-player" controls style="width: 100%; margin-top: 10px;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById('audio-player');
            var card = audio.previousElementSibling;
            audio.onplay = function() {{
                card.style.backgroundColor = '#fff9c4'; // اللون الأصفر عند التشغيل
            }};
            audio.onpause = function() {{
                card.style.backgroundColor = 'white';
            }};
            audio.onended = function() {{
                card.style.backgroundColor = 'white';
            }};
        </script>
    """
    return audio_html

def resolve_model():
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']:
            if preferred in available:
                return preferred
        return available[0]
    except:
        return 'models/gemini-1.5-flash'

selected_model = resolve_model()
model = genai.GenerativeModel(selected_model)

st.set_page_config(page_title="EduGenius AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=Cairo:wght@400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #f8fafc, #e2e8f0, #f1f5f9, #ffffff);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Plus Jakarta Sans', 'Cairo', sans-serif;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stTabs [data-baseweb="tab-list"] {
        width: 100% !important;
        display: flex !important;
        justify-content: space-around !important;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 10px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1 !important;
        transition: 0.4s;
        border-radius: 12px;
        font-weight: 800;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background: #2563eb !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
        color: white !important;
    }

    .explanation-card {
        background: white;
        padding: 35px;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        border-left: 8px solid #2563eb;
        margin-bottom: 25px;
        line-height: 2.2;
        font-size: 18px;
        color: #1e293b;
        white-space: pre-wrap;
        transition: background-color 0.3s ease;
    }

    .stButton>button {
        background: #1e293b;
        color: white;
        border-radius: 15px;
        padding: 20px;
        font-weight: 700;
        border: none;
        width: 100%;
        transition: 0.3s all;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        background: #2563eb;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
    }

    .stMarkdown table {
        width: 100% !important;
        border-radius: 15px;
        overflow: hidden;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    th { background-color: #0f172a !important; color: white !important; padding: 18px !important; }
    td { background-color: white !important; padding: 15px !important; border-bottom: 1px solid #f1f5f9 !important; }
    
    .rtl-container { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 EduGenius AI")
st.caption("🚀 The secret to getting ahead is getting started. Believe in yourself!")

file = st.file_uploader("Upload PDF", type="pdf")

if file:
    pdf = PdfReader(file)
    text = "".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    st.success("Your PDF has been successfully uploaded!")

    t1, t2, t3, t4, t5 = st.tabs(["📝 Summary", "📊 Table", "🎧 Podcast Script", "🧠 Quiz", "💬 Ask Gemini"])

    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Summary"):
            with st.spinner("Synthesizing..."):
                try:
                    res = model.generate_content(f"Provide a deep academic summary in the same language as the text. Break down the content into clear, separate points. Start each new idea on a new line. No # or *: \n\n {text[:15000]}")
                    dir = get_direction(res.text)
                    st.markdown(f'<div class="explanation-card" style="direction: {dir}; text-align: {"right" if dir=="rtl" else "left"};">{res.text}</div>', unsafe_allow_html=True)
                except Exception:
                    st.warning("⚠️ Daily limit reached.")

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Extract Table"):
            with st.spinner("Structuring..."):
                try:
                    res = model.generate_content(f"Act as a data architect. Extract all major concepts into a Markdown table with three columns: (Concept | Detailed Explanation | Practical Application). Ensure the information is dense and accurate. STRICTLY use the SAME language as the source text. Do not translate headers or content: \n\n {text[:15000]}")
                    dir = get_direction(res.text)
                    st.markdown(f'<div class="{"rtl-container" if dir=="rtl" else ""}">', unsafe_allow_html=True)
                    st.markdown(res.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except:
                    st.warning("⚠️ Daily limit reached.")

    with t3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Podcast Script"):
            with st.spinner("Writing Script..."):
                try:
                    res = model.generate_content(f"Convert this text into an engaging podcast script between two experts discussing the main ideas. Use a conversational, easy-to-follow tone. STRICTLY use the SAME language as the source text: \n\n {text[:10000]}")
                    dir = get_direction(res.text)
                    st.markdown(f'<div class="explanation-card" style="direction: {dir}; text-align: {"right" if dir=="rtl" else "left"}; background: white;">{res.text}</div>', unsafe_allow_html=True)
                    lang = 'ar' if dir == 'rtl' else 'en'
                    st.markdown(text_to_speech_html(res.text, lang=lang), unsafe_allow_html=True)
                except:
                    st.warning("⚠️ Error generating script.")

    with t4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Quiz"):
            with st.spinner("Designing..."):
                try:
                    st.session_state.qid = random.randint(1, 9999)
                    prompt = f"Act as an expert examiner. Create 10 high-level Multiple Choice Questions (MCQs) that test critical thinking and inference, not just memorization. Format as JSON ONLY: [{{'question': '...', 'options': ['...', '...'], 'answer': '...'}}]. STRICTLY use the SAME language as the source text: \n\n {text[:10000]}"
                    res = model.generate_content(prompt)
                    raw = res.text.replace('```json', '').replace('```', '').strip()
                    st.session_state.quiz = json.loads(raw)
                except:
                    st.warning("⚠️ Daily limit reached.")

        if 'quiz' in st.session_state:
            for i, q in enumerate(st.session_state.quiz):
                dir = get_direction(q['question'])
                st.markdown(f"<div class='explanation-card' style='direction: {dir}; text-align: {'right' if dir=='rtl' else 'left'};'>", unsafe_allow_html=True)
                st.markdown(f"**Q{i+1}: {q['question']}**")
                choice = st.radio("Select Option:", q['options'], key=f"q_{i}_{st.session_state.qid}", index=None)
                if st.button(f"Verify Q{i+1}", key=f"v_{i}"):
                    if choice == q['answer']: st.success("Correct")
                    else: st.error(f"Answer: {q['answer']}")
                st.markdown("</div>", unsafe_allow_html=True)

    with t5:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🤖 Ask anything about the PDF")
        user_query = st.text_input("Enter your question:")
        if st.button("Send Question"):
            if user_query:
                with st.spinner("Thinking..."):
                    try:
                        res = model.generate_content(f"Act as a personal tutor. Answer the user's question based strictly on the provided context. you can explain with any language: \n\n Context: {text[:10000]} \n\n Question: {user_query}")
                        dir = get_direction(res.text)
                        st.markdown(f'<div class="explanation-card" style="direction: {dir}; text-align: {"right" if dir=="rtl" else "left"}; background: white;">{res.text}</div>', unsafe_allow_html=True)
                        lang = 'ar' if dir == 'rtl' else 'en'
                        st.markdown(text_to_speech_html(res.text, lang=lang), unsafe_allow_html=True)
                    except:
                        st.error("Connection error.")