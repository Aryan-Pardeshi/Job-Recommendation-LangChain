import streamlit as st
import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from src.agent import run_agent, PROVIDER_CONFIG
from src.fetch_location import get_location_by_ip
from src.job_api import SUPPORTED_SITES

st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helpers ──

def load_env():
    from dotenv import load_dotenv
    load_dotenv()

def save_env_key(key_name: str, value: str):
    path = ".env"
    lines = []
    found = False
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if line.startswith(f"{key_name}="):
                    lines.append(f'{key_name}="{value}"\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'{key_name}="{value}"\n')
    with open(path, "w") as f:
        f.writelines(lines)
    load_env()


load_env()

# ── Sidebar ──
with st.sidebar:
    st.image("images and vids/logo.png", width=250)
    st.markdown("### About")
    st.markdown(
        "Upload your resume and get AI-powered job recommendations "
        "scraped from **LinkedIn**, **Indeed**, and **Google Jobs**."
    )
    st.markdown("---")
    st.markdown("#### How it works")
    st.markdown(
        "1. Upload your PDF resume\n"
        "2. AI analyzes your profile\n"
        "3. Jobs are scraped in real-time\n"
        "4. Get tailored recommendations"
    )
    st.markdown("---")
    st.markdown(f"**Scraping:** {', '.join(s.title() for s in SUPPORTED_SITES[:3])}")
    st.markdown(f"**Scraper:** JobSpy (free, open-source)")

# ── Main Content ──
st.title("📄 AI Job Recommender")
st.markdown("Upload your resume and get job recommendations based on your skills and experience.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    st.success(f"✅ Uploaded: **{uploaded_file.name}**")

    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    resume_text = "\n".join(doc.page_content for doc in docs)
    st.info(f"📄 Parsed {len(docs)} page(s) from your resume.")

    with st.spinner("Detecting your location..."):
        user_location = get_location_by_ip()
    st.info(f"📍 Detected Location: **{user_location}**")

    # ── Job Preferences ──
    st.markdown("### Job Search Preferences")
    col1, col2, col3 = st.columns(3)

    with col1:
        work_type = st.selectbox(
            "Work Type",
            options=["Detect Automatically", "1=On-site", "2=Remote", "3=Hybrid"],
        )
    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            options=[
                "Detect Automatically",
                "1=Internship",
                "2=Entry level",
                "3=Associate",
                "4=Mid-Senior level",
                "5=Director",
            ],
        )
    with col3:
        location_pref = st.text_input(
            "Preferred Location",
            value="",
            placeholder="e.g. New York, NY (leave blank to auto-detect)",
        )

    # ── Provider Selection ──
    st.markdown("### 🤖 AI Model Provider")
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        provider = st.selectbox(
            "Provider",
            options=["google", "opencode_zen"],
            format_func=lambda x: {"google": "Google Gemini", "opencode_zen": "OpenCode Zen (Free)"}[x],
        )

    cfg = PROVIDER_CONFIG[provider]
    available_models = cfg["models"]

    with col_p2:
        model = st.selectbox("Model", options=available_models, index=0)

    # ── API Key Handling ──
    env_key_name = cfg["env_key"]
    existing_key = os.getenv(env_key_name, "")

    if not existing_key:
        st.warning(f"⚠️ No **{env_key_name}** found in .env")

        if provider == "google":
            st.markdown("Get a key: [Google AI Studio](https://aistudio.google.com/api-keys)")
        elif provider == "opencode_zen":
            st.markdown("Get a key: [OpenCode Zen Auth](https://opencode.ai/auth)")

        key_input = st.text_input(
            f"Enter your {env_key_name}",
            type="password",
            key=f"key_input_{provider}",
        )
        if key_input and st.button("💾 Save API Key", key=f"save_btn_{provider}"):
            save_env_key(env_key_name, key_input)
            st.success(f"✅ {env_key_name} saved to .env! Reloading...")
            st.rerun()

    # ── Search ──
    if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
        api_key = os.getenv(env_key_name, "")

        if not api_key:
            st.error(f"❌ {env_key_name} is not set. Enter it above or add it to your .env file.")
            st.stop()

        preferences = {
            "work_type": work_type,
            "experience_level": experience_level,
            "location": location_pref.strip() if location_pref.strip() else "Detect Automatically",
        }

        with st.spinner(f"🤖 AI ({provider}) is analyzing your resume and searching jobs..."):
            try:
                result = run_agent(
                    resume_text=resume_text,
                    user_location=user_location,
                    preferences=preferences,
                    llm_provider=provider,
                    llm_model=model,
                    api_key=api_key,
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        st.subheader("🎯 Job Recommendations")
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and item.get("type") == "text":
                    st.markdown(item.get("text"))
        else:
            st.markdown(result)

else:
    st.info("👆 Upload your resume (PDF) to get started.")
    st.markdown("""
    ### What you get:
    - 🎯 **Personalized job matches** based on your resume
    - 📊 **Salary insights** from job listings
    - 💡 **Application tips** tailored to your profile
    """)
