import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent


SYSTEM_PROMPT = """You are an expert career advisor and job placement specialist.

The user will provide their resume text. Your job is to:

1. **Analyse the resume** to extract:
   - Their primary job title / role (e.g. "Data Scientist", "Software Engineer")
   - Their location preference (if not explicitly mentioned, default to the user's detected location)
   - Experience level → map to: 1=Internship, 2=Entry level, 3=Associate, 4=Mid-Senior level, 5=Director
   - Work type preference → map to: 1=On-site, 2=Remote, 3=Hybrid (default to 2=Remote if unclear)
   - **CRITICAL RULE**: If the Work Type is "2" (Remote), you MUST pass an empty string `""` for the location parameter when calling the tool.

2. **Search for jobs** by calling the `job_recommender__fetchlinkedin` tool with the extracted parameters.
   - Also try a second search with a related/broader job title for more results.

3. **Present the top results** in a clean, structured format:
   - 🏢 **Job Title** at **Company**
   - 📍 Location | 💼 Work Type | 💰 Salary (if available)
   - 🔗 **[Apply Here](url)**
   - 🎯 A short 1-line description of why this matches the candidate's profile.

4. **Provide Application Tips**: At the bottom of the recommendations, provide 2-3 specific, actionable tips on how they should tailor their application or interview approach based on the skills highlighted in their resume.

Be concise, helpful, and ensure every job has a clickable apply link if the URL is provided.
"""


async def _run_agent_async(resume_text: str, user_location: str, preferences: dict = None) -> str:

    # Project root — needed so `mcp_server.py` can resolve `src.job_api`
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    client = MultiServerMCPClient(
        {
            "job_recommender": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
                "cwd": project_root, #fixes errors for mcp
            }
        }
    )
    tools = await client.get_tools()

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    agent = create_agent(
        llm,
        tools,
        system_prompt=SYSTEM_PROMPT,
    )

    # Inject user settings or let the LLM do it
    input_text = f"USER'S DETECTED IP LOCATION: {user_location}\n"
    if preferences:
        # Enforce blank location if they manually chose Remote
        if "Remote" in preferences.get("work_type", ""):
            preferences["location"] = '""'
            
        input_text += "\n--- MANUAL USER PREFERENCES (OVERRIDE RESUME IF NOT 'Detect Automatically') ---\n"
        input_text += f"- Preferred Work Type: {preferences['work_type']}\n"
        input_text += f"- Preferred Experience Level: {preferences['experience_level']}\n"
        input_text += f"- Preferred Location: {preferences['location']}\n"
        
    input_text += f"\nRESUME TEXT:\n{resume_text}"
    
    result = await agent.ainvoke(
        {"messages": [("human", input_text)]}
    )
    # Last message in the list is the final AI response (could be raw list of dicts)
    return result["messages"][-1].content


def run_agent(resume_text: str, user_location: str, preferences: dict = None) -> str:
    """Sync wrapper — safe to call from Streamlit."""
    return asyncio.run(_run_agent_async(resume_text, user_location, preferences))
