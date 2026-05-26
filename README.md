<div align="center">
  <img src="images%20and%20vids/logo.png" alt="AI Job Recommender Logo" width="400" />
</div>

An intelligent, autonomous job recommendation agent that parses your resume and searches **LinkedIn**, **Indeed**, and **Google Jobs** for the perfect matching open roles — powered by LangGraph, Gemini, and [JobSpy](https://github.com/speedyapply/JobSpy).

### 🎥 Video Demo

https://github.com/Aryan-Pardeshi/Job-Recommendation-LangChain/raw/main/images%20and%20vids/2026-03-19%2013-47-19.mp4

---

## ✨ Features

### Core
- **Resume Parsing Engine** — Upload your PDF resume directly into the app.
- **Agentic Analysis** — Uses Google's Gemini inside LangGraph to analyze your career history and determine your optimal seniority, work type, and job title.
- **Multi-Platform Search** — Searches **LinkedIn**, **Indeed**, and **Google Jobs** simultaneously via [JobSpy](https://github.com/speedyapply/JobSpy) (free, no API key).
- **Smart Location Detection** — Automatically detects your IP and pulls nearby jobs via the free `ip-api.com` service.
- **Manual Preference Overrides** — Override AI detections with dropdowns for Work Type, Experience Level, Location, and Job Boards.
- **Broader Second Pass** — The AI automatically performs a second broader search to find more opportunities.
- **Application Tips** — Dynamically generates actionable interview and application tips tailored to your resume.

### UI/UX
- **Job Result Cards** — Clean card-based layout with company, location, salary, and source badges.
- **Source Badges** — Color-coded badges for LinkedIn (blue), Indeed, and Google.
- **Salary Display** — Formatted salary ranges with currency and interval.
- **Expandable Descriptions** — View full job descriptions inline.
- **Stats Dashboard** — See total jobs, remote count, salary ranges, and top companies at a glance.
- **CSV Export** — Download all results as a CSV file.
- **Raw Results Tab** — Browse unfiltered results alongside AI recommendations.
- **Session State** — Preserves results across UI interactions.
- **Sidebar Info Panel** — Quick access to how it works and what's powering the app.

### Architecture
- **MCP Server Ecosystem** — Decoupled [Model Context Protocol](https://modelcontextprotocol.io) server (`mcp_server.py`) exposes job search tools. The LangChain agent connects via `MultiServerMCPClient`.
- **Three MCP Tools** — `search_jobs_tool` (filtered), `search_jobs_broad_tool` (unfiltered), `list_supported_sites`.
- **Zero Cloud Dependencies** — Everything runs locally. No paid APIs for scraping.

---

## 🚀 How to Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Job-Recommendation-LangChain
```

### 2. Install Dependencies
This project uses `uv` for fast package and virtual environment management.
```bash
# First, install uv globally if you haven't already
pip install uv

# Sync and install the project environment
uv sync
```

### 3. Install JobSpy
JobSpy's numpy pin conflicts with Python 3.13, so install it manually:
```bash
pip install python-jobspy --no-deps
pip install beautifulsoup4 markdownify regex tls-client
```

### 4. API Setup & Configuration
You only need one API key (for the LLM):

1. Copy the example `.env` file:
   ```bash
   cp .env.example .env
   ```

2. **Google API Key** — We use Gemini as our intelligent LangGraph Agent.
   - Go to [Google AI Studio](https://aistudio.google.com/api-keys) and generate an API key.
   - Add it to your `.env` file.

### 5. Run the Application
```bash
uv run streamlit run main.py
```
Open your browser to `http://localhost:8501`, upload your resume, and click **Find Matching Jobs**!

---

## 🏗️ Project Structure

```
├── main.py                 # Streamlit UI (entry point)
├── mcp_server.py           # FastMCP server with 3 job-search tools
├── pyproject.toml          # Project metadata and dependencies
├── .env                    # Environment variables (GOOGLE_API_KEY, OPENCODE_ZEN_API_KEY)
├── README.md               # This file
│
├── src/
│   ├── agent.py            # LangGraph agent (LLM orchestration)
│   ├── job_api.py          # JobSpy wrapper (search, stats, mappings)
│   └── fetch_location.py   # IP geolocation via ip-api.com
│
└── images and vids/
    ├── logo.png            # App logo
    └── 2026-03-19 13-47-19.mp4  # Demo video
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **AI Agent** | LangGraph + Google Gemini or OpenCode Zen (free models) |
| **Job Scraper** | JobSpy (LinkedIn, Indeed, Google Jobs) |
| **Tool Protocol** | MCP (Model Context Protocol) via FastMCP |
| **Resume Parser** | PyPDFLoader (LangChain) |
| **Location** | ip-api.com (free) |
| **Package Manager** | uv |

## 📊 JobSpy Data Schema

Each job result includes:
- `title`, `company`, `site` (source platform)
- `job_url`, `location`, `description`
- `is_remote`, `job_type` (fulltime, parttime, contract, internship)
- `min_amount`, `max_amount`, `currency`, `interval` (salary)
- `date_posted`, `company_url`, `emails`
