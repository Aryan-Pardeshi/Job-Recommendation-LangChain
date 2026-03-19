from mcp.server.fastmcp import FastMCP
from src.job_api import find_job

mcp = FastMCP("Job Recommender")


@mcp.tool()
def fetchlinkedin(job_title: str, location: str, experience_level: str, work_type: str):
    """Fetches LinkedIn jobs based on job title, location, experience level, and work type.
    job_title is the name of the job.
    location is the location of the job.
    experience_level: 1 = Internship, 2 = Entry level, 3 = Associate, 4 = Mid-Senior level, 5 = Director
    work_type: 1 = On-site, 2 = Remote, 3 = Hybrid"""
    return find_job(job_title, location, experience_level, work_type)

if __name__ == "__main__":
    mcp.run()
