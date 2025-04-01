import requests
import pandas as pd
import datetime

# User-Agent header required by the API
headers = {
    "accept": "application/json",
    "User-Agent": "WikimediaDataCollector/1.0 (youremail@example.com)"
}

# Define the parameter space you want to cover
projects = ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org", "es.wikipedia.org", "commons.wikimedia.org", "meta.wikimedia.org", "wikidata.org"]
editor_types = ["anonymous", "group-bot", "name-bot", "user"]
page_types = ["content", "non-content"]
activity_levels = ["1..4-edits", "5..24-edits", "25..99-edits", "100..-edits"]

# Date range for the data. Adjust as needed.
# For example, from 2023-01-01 to 2024-01-01
start_date = "20180101"
end_date = "20240101"

# Output CSV file
output_csv = "editors_data.csv"

# Initialize an empty DataFrame or check if the file already exists
try:
    # If file exists, append to it
    existing_df = pd.read_csv(output_csv)
    collected_data = existing_df
except FileNotFoundError:
    collected_data = pd.DataFrame(columns=["project", "editor_type", "page_type", "activity_level", "date", "editors"])

# Function to fetch data for a given parameter set
def fetch_editors_data(project, editor_type, page_type, activity_level, granularity, start, end):
    url = (f"https://wikimedia.org/api/rest_v1/metrics/editors/aggregate/"
           f"{project}/{editor_type}/{page_type}/{activity_level}/{granularity}/{start}/{end}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

# Iterate over all combinations of parameters
for project in projects:
    for editor_type in editor_types:
        for page_type in page_types:
            for activity_level in activity_levels:
                try:
                    data = fetch_editors_data(project, editor_type, page_type, activity_level, "daily", start_date, end_date)
                    items = data.get("items", [])
                    
                    if items:
                        # Each item has "results" which contain timestamps and editors count
                        # Example structure:
                        # "items": [
                        #   {
                        #     "project": "en.wikipedia",
                        #     "editor-type": "all-editor-types",
                        #     "page-type": "all-page-types",
                        #     "activity-level": "5..24-edits",
                        #     "granularity": "monthly",
                        #     "results": [
                        #       {
                        #         "timestamp": "2023-01-01T00:00:00.000Z",
                        #         "editors": 48660
                        #       }
                        #     ]
                        #   }
                        # ]

                        # Usually there's one item matching the requested parameters
                        item = items[0]
                        results = item.get("results", [])
                        temp_df = pd.DataFrame(results)

                        # Convert timestamp to a date string (YYYY-MM-DD)
                        temp_df["date"] = pd.to_datetime(temp_df["timestamp"]).dt.date

                        # Add parameter columns
                        temp_df["project"] = project
                        temp_df["editor_type"] = editor_type
                        temp_df["page_type"] = page_type
                        temp_df["activity_level"] = activity_level

                        # Select the required columns
                        temp_df = temp_df[["project", "editor_type", "page_type", "activity_level", "date", "editors"]]

                        # Append to the main dataframe
                        collected_data = pd.concat([collected_data, temp_df], ignore_index=True)

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data for {project}, {editor_type}, {page_type}, {activity_level}: {e}")

# Remove duplicates if any, and sort by date
collected_data.drop_duplicates(inplace=True)
collected_data.sort_values(by=["project", "editor_type", "page_type", "activity_level", "date"], inplace=True)

# Save to CSV
collected_data.to_csv(output_csv, index=False)

print(f"Data collection completed. Results saved in {output_csv}")
