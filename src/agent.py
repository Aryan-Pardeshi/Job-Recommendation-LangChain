import asyncio
import os
import logging
from dotenv import load_dotenv
load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("agent")

SYSTEM_PROMPT = """You are an expert career advisor and job placement specialist.

The user will provide their resume text. Your job is to:

1. **Analyse the resume** to extract:
   - Primary job title / role (e.g. "Data Scientist", "Software Engineer")
   - Related/broader job titles for a second search
   - Location preference (default to detected location if unclear)
   - Experience level → map to: 1=Internship, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director
   - Work type → map to: 1=On-site, 2=Remote, 3=Hybrid (default 2=Remote if unclear)
   - **CRITICAL**: If Work Type is "2" (Remote), pass empty string `""` for location

2. **Search for jobs** by calling `job_recommender__search_jobs_tool` with extracted params.
   Then call `job_recommender__search_jobs_broad_tool` with a broader/related title.

3. **Present results** in a clean format:
   🏢 **Job Title** at **Company**
   📍 Location | 💼 Work Type | 💰 Salary (if available)
   🔗 **[Apply Here](url)**
   🎯 Short match reason

4. **Provide 2-3 application tips** tailored to the candidate's resume.

Be concise and ensure every job has a clickable apply link.
"""

PROVIDER_CONFIG = {
    "google": {
        "models": ["gemini-3.1-flash-lite-preview", "gemini-2.5-flash-preview", "gemini-2.0-flash"],
        "env_key": "GOOGLE_API_KEY",
        "default_model": "gemini-3.1-flash-lite-preview",
    },
    "opencode_zen": {
        "models": ["big-pickle", "mimo-v2-pro-free", "mimo-v2-omni-free", "minimax-m2.5-free", "nemotron-3-super-free"],
        "env_key": "OPENCODE_ZEN_API_KEY",
        "default_model": "big-pickle",
        "api_base": "https://opencode.ai/zen/v1",
    },
}


def get_llm(provider: str, model: str = None, api_key: str = None):
    cfg = PROVIDER_CONFIG.get(provider)
    if not cfg:
        raise ValueError(f"Unknown provider: {provider}")

    model = model or cfg["default_model"]
    api_key = api_key or os.getenv(cfg["env_key"])

    if not api_key:
        raise ValueError(f"API key for {provider} not found. Set {cfg['env_key']} in .env or provide it.")

    if provider == "google":
        logger.info(f"Using Google Gemini: {model}")
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)

    if provider == "opencode_zen":
        logger.info(f"Using OpenCode Zen: {model}")
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=cfg["api_base"],
        )

    raise ValueError(f"Unsupported provider: {provider}")


async def _run_agent_async(
    resume_text: str,
    user_location: str,
    preferences: dict = None,
    llm_provider: str = "google",
    llm_model: str = None,
    api_key: str = None,
) -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    client = MultiServerMCPClient(
        {
            "job_recommender": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
                "cwd": project_root,
            }
        }
    )
    try:
        tools = await client.get_tools()
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        return f"Error: Could not start the job search service. {e}"

    try:
        llm = get_llm(llm_provider, llm_model, api_key)
    except ValueError as e:
        return f"Error: {e}"

    agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)

    input_text = f"USER'S DETECTED IP LOCATION: {user_location}\n"
    if preferences:
        if "Remote" in preferences.get("work_type", ""):
            preferences["location"] = '""'
        input_text += (
            "\n--- MANUAL USER PREFERENCES (OVERRIDE RESUME IF NOT 'Detect Automatically') ---\n"
            f"- Preferred Work Type: {preferences['work_type']}\n"
            f"- Preferred Experience Level: {preferences['experience_level']}\n"
            f"- Preferred Location: {preferences['location']}\n"
        )
    input_text += f"\nRESUME TEXT:\n{resume_text}"

    try:
        result = await agent.ainvoke({"messages": [("human", input_text)]})
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return f"Error: Failed to generate recommendations. {e}"


def run_agent(
    resume_text: str,
    user_location: str,
    preferences: dict = None,
    llm_provider: str = "google",
    llm_model: str = None,
    api_key: str = None,
) -> str:
    return asyncio.run(
        _run_agent_async(resume_text, user_location, preferences, llm_provider, llm_model, api_key)
    )
