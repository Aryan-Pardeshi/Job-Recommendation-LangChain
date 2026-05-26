from jobspy import scrape_jobs
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

SUPPORTED_SITES = ["linkedin", "indeed", "google", "zip_recruiter", "glassdoor"]

EXPERIENCE_MAP = {
    "1": "internship",
    "2": None,
    "3": None,
    "4": None,
    "5": None,
}

WORK_TYPE_MAP = {
    "1": False,
    "2": True,
    "3": False,
}

JOB_TYPE_MAP = {
    "fulltime": "fulltime",
    "parttime": "parttime",
    "contract": "contract",
    "internship": "internship",
}


def search_jobs(
    job_title: str,
    location: str = "",
    experience_level: str = None,
    work_type: str = None,
    site_name: list = None,
    results_wanted: int = 10,
    hours_old: int = 720,
    country: str = "USA",
    job_type: str = None,
) -> list[dict]:
    if site_name is None:
        site_name = ["linkedin", "indeed", "google"]

    jt = EXPERIENCE_MAP.get(experience_level, None)
    is_remote = WORK_TYPE_MAP.get(work_type) if work_type else None

    try:
        jobs_df = scrape_jobs(
            site_name=site_name,
            search_term=job_title,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            job_type=jt,
            is_remote=is_remote,
            country_indeed=country,
        )
    except Exception as e:
        raise RuntimeError(f"JobSpy scrape failed: {e}")

    if jobs_df is None or jobs_df.empty:
        return []

    jobs_df = jobs_df.where(pd.notna(jobs_df), None)

    records = jobs_df.to_dict(orient="records")
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and pd.isna(v):
                r[k] = None

    return records


def search_jobs_broad(
    job_title: str,
    location: str = "",
    results_wanted: int = 15,
    country: str = "USA",
) -> list[dict]:
    return search_jobs(
        job_title=job_title,
        location=location,
        experience_level=None,
        work_type=None,
        site_name=["linkedin", "indeed"],
        results_wanted=results_wanted,
        hours_old=720,
        country=country,
    )


def get_job_stats(jobs: list[dict]) -> dict:
    if not jobs:
        return {}
    df = pd.DataFrame(jobs)
    stats = {
        "total": len(jobs),
        "by_site": df["site"].value_counts().to_dict() if "site" in df else {},
        "top_companies": (
            df["company"].value_counts().head(5).to_dict()
            if "company" in df
            else {}
        ),
        "remote_count": int(df["is_remote"].sum()) if "is_remote" in df and df["is_remote"].dtype == bool else 0,
        "salary_count": int(df["min_amount"].notna().sum()) if "min_amount" in df else 0,
    }
    if "min_amount" in df and "max_amount" in df:
        valid = df["min_amount"].notna() & df["max_amount"].notna()
        if valid.any():
            stats["salary_min"] = float(df.loc[valid, "min_amount"].min())
            stats["salary_max"] = float(df.loc[valid, "max_amount"].max())
    return stats


if __name__ == "__main__":
    jobs = search_jobs("Software Engineer", "New York", "4", "1")
    for job in jobs:
        print(job)
    print("\nStats:", get_job_stats(jobs))
