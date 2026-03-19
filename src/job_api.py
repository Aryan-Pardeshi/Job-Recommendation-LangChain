from apify_client import ApifyClient
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the ApifyClient with your API token
client = ApifyClient(os.getenv("APIFY_TOKEN"))

def find_job(job_title, location, experience_level, work_type):
    # workType:       "1" = On-site, "2" = Remote, "3" = Hybrid
    # experienceLevel: "1" = Internship, "2" = Entry level, "3" = Associate,
    #                  "4" = Mid-Senior level, "5" = Director
    run_input = {
        "experienceLevel": experience_level,
        "location": location,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        },
        "publishedAt": "r2592000",
        "title": job_title,
        "workType": work_type, #1 for on-site, 2 for remote, 3 for hybrid
        "rows": 10
    }
    # Run the Actor and wait for it to finish
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    # Fetch and return Actor results from the run's dataset
    jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs

if __name__ == "__main__":
    jobs = find_job("Software Engineer", "New York", "4", "1")
    for job in jobs:
        print(job)