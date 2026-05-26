from jobspy import scrape_jobs
import os
from dotenv import load_dotenv
load_dotenv()


def find_job(job_title, location, experience_level, work_type):
    job_type_map = {"1": "internship"}
    jt = job_type_map.get(experience_level, None)

    is_remote = work_type == "2"
    
    results_wanted_count = 10

    jobs_df = scrape_jobs(
        site_name=["linkedin", "indeed", "google"],
        search_term=job_title,
        location=location,
        results_wanted=results_wanted_count,
        hours_old=720,
        job_type=jt,
        is_remote=is_remote,
        country_indeed="USA",
    )

    if jobs_df.empty:
        return []
    return jobs_df.to_dict(orient="records")


if __name__ == "__main__":
    jobs = find_job("Software Engineer", "New York", "4", "1")
    for job in jobs:
        print(job)
