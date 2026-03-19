import streamlit as st
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from src.agent import run_agent
from src.fetch_location import get_location_by_ip

st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄 AI Job Recommender")
st.markdown("Upload your resume and get job recommendations based on your skills and experience.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    # Save in-memory upload to disk so PyPDFLoader can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    st.success(f"✅ Uploaded: **{uploaded_file.name}**")

    # Parse all pages into a single text block
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
            options=["Detect Automatically", "1=On-site", "2=Remote", "3=Hybrid"]
        )
    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            options=["Detect Automatically", "1=Internship", "2=Entry level", "3=Associate", "4=Mid-Senior level", "5=Director"]
        )
    with col3:
        location_pref = st.text_input("Preferred Location", value="", placeholder="e.g. New York, NY (leave blank to detect automatically)")
    
    if st.button("🔍 Find Matching Jobs"):
        with st.spinner("Searching LinkedIn via Apify..."):
            preferences = {
                "work_type": work_type,
                "experience_level": experience_level,
                "location": location_pref.strip() if location_pref.strip() else "Detect Automatically"
            }
            result = run_agent(resume_text, user_location, preferences)
        st.subheader("🎯 Job Recommendations")
        #to print the output in markdown properly
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and item.get("type") == "text":
                    st.markdown(item.get("text"))
        else:
            st.markdown(result)