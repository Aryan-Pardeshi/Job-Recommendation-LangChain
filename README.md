<div align="center">
  <img src="images%20and%20vids/logo.png" alt="AI Job Recommender Logo" width="400" />
</div>

An intelligent, autonomous job recommendation agent that parses your resume and searches LinkedIn for the perfect matching open roles using LangGraph, Gemini, and Apify.

### 🎥 Video Demo

> Watch the agent in action below as it parses a resume, figures out the best location/roles, and executes tool scrape requests:
> 
> <video src="images%20and%20vids/2026-03-19%2013-47-19.mp4" controls="controls" style="max-width: 730px;">
> </video>

---

## ✨ Features

- **Resume Parsing Engine:** Upload your PDF resume directly into the app.
- **Agentic Analysis:** Uses Google's Gemini models inside LangGraph to analyze your career history and determine your optimal seniority, work type, and job title limits.
- **Smart Location Detection:** Automatically detects your IP and pulls nearby jobs via the free `ip-api.com` service if no location is specified.
- **Manual Preference Overrides:** Don't want the AI to guess? Override its detections with manual drop-downs for Work Type, Experience Level, and Location fields.
- **MCP Server Ecosystem:** Uses FastMCP and LangChain's `MultiServerMCPClient` to fetch real-time LinkedIn listings via a decoupled `mcp_server.py`.
- **Application Tips:** Dynamically gives you actionable interview and application tips tailored uniquely to the match between your resume properties and the scraped job descriptions.

---

## 🚀 How to Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Job-Recommendation-LangChain
```

### 2. Install Dependencies
This project uses `uv` for blistering fast package and virtual environment management.
```bash
# First, install uv globally if you haven't already
pip install uv

# Sync and install the project environment
uv sync
```

### 3. API Setup & Configuration
You will need keys for two free services to power the LLM and the Scraper context.

1. Copy the example `.env` file to set up your environment:
   ```bash
   cp .env.example .env
   ```

2. **Apify Token:** This app uses Apify's LinkedIn Scraper to fetch live job postings.
   - Go to [Apify Actor page](https://console.apify.com/actors/BHzefUZlZRKWxkTck/input).
   - Once logged in, navigate to Settings / Integrations to find your API Token.
   - Look at the configuration payload expectations below:
   
   ![Apify Scraper Config](images%20and%20vids/Linkedin-Scraper.png)

3. **Google API Key:** We use Gemini as our intelligent LangGraph Agent.
   - Go to [Google AI Studio](https://aistudio.google.com/api-keys) and generate an API key.

Paste both of those keys directly into your newly created `.env` file.

### 4. Run the Application
Finally, start the Streamlit front-end using `uv`:
```bash
uv run streamlit run main.py
```
Open up your browser to `http://localhost:8501`, upload your resume, and click **Find Matching Jobs**!
