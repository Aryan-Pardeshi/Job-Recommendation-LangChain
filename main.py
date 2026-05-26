import streamlit as st
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from src.agent import run_agent
from src.fetch_location import get_location_by_ip
from src.job_api import SUPPORTED_SITES

st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    st.markdown("**LLM:** Gemini 3.1 Flash Lite")
    st.markdown("**Scraper:** JobSpy (free, open-source)")

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

    if st.button("🔍 Find Matching Jobs", type="primary", use_container_width=True):
        preferences = {
            "work_type": work_type,
            "experience_level": experience_level,
            "location": location_pref.strip() if location_pref.strip() else "Detect Automatically",
        }

        with st.spinner("🤖 AI is analyzing your resume and searching jobs..."):
            try:
                result = run_agent(resume_text, user_location, preferences)
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
