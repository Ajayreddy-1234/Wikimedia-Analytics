import requests
import pandas as pd
import os
from datetime import datetime

# User-Agent header required by the API
headers = {
    "accept": "application/json",
    "User-Agent": "WikimediaDataCollector/1.0 (youremail@example.com)"
}

# Parameters
projects = ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org", "es.wikipedia.org"]
access_methods = ["desktop", "mobile-app", "mobile-web"]
agents = ["user", "spider", "automated"]

# Fixed date range in YYYYMMDDHH format
start = "2018010100"
end = "2024010100"
granularity = "daily"

# Output CSV file
output_csv = "pageviews_daily_all_params.csv"

# Check if the CSV already exists; if not, create an empty DataFrame
if os.path.exists(output_csv):
    collected_data = pd.read_csv(output_csv)
else:
    collected_data = pd.DataFrame(columns=["project", "access", "agent", "timestamp", "views"])

def fetch_pageviews_data(project, access, agent, granularity, start, end):
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/"
           f"{project}/{access}/{agent}/{granularity}/{start}/{end}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

# Iterate over all combinations of project, access, agent
for project in projects:
    for access in access_methods:
        for agent in agents:
            try:
                data = fetch_pageviews_data(project, access, agent, granularity, start, end)
                items = data.get("items", [])
                if items:
                    df = pd.DataFrame(items)
                    # Convert timestamp to datetime
                    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d%H")
                    # Add project, access, agent columns
                    df["project"] = project
                    df["access"] = access
                    df["agent"] = agent
                    # Keep required columns
                    df = df[["project", "access", "agent", "timestamp", "views"]]
                    # Append to main DataFrame
                    collected_data = pd.concat([collected_data, df], ignore_index=True)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {project}, {access}, {agent}: {e}")

# Remove duplicates if any
collected_data.drop_duplicates(inplace=True)

# Sort the data
collected_data.sort_values(by=["project", "access", "agent", "timestamp"], inplace=True)

# Save to CSV
collected_data.to_csv(output_csv, index=False)

print(f"Data collection completed. Results saved in {output_csv}")
