import requests
import pandas as pd
import datetime
import os

# User-Agent header required by the API
headers = {
    "accept": "application/json",
    "User-Agent": "WikimediaDataCollector/1.0 (youremail@example.com)"
}

# Define the parameter space you want to cover
projects = ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org", "es.wikipedia.org"]
activity_levels = ["5..99-edits", "100..-edits"]
years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

# Output CSV file
output_csv = "editors_by_country.csv"

# Initialize the DataFrame
if os.path.exists(output_csv):
    collected_data = pd.read_csv(output_csv)
else:
    collected_data = pd.DataFrame(columns=["project", "activity_level", "year", "month", "country", "editors"])

def fetch_editors_data(project, activity_level, year, month):
    url = (f"https://wikimedia.org/api/rest_v1/metrics/editors/by-country/"
           f"{project}/{activity_level}/{year}/{month}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

# Iterate over all combinations of parameters
for project in projects:
    for activity_level in activity_levels:
        for year in years:
            for month in months:
                try:
                    data = fetch_editors_data(project, activity_level, year, month)
                    items = data.get("items", [])
                    
                    if items:
                        # Usually there's one item per request
                        item = items[0]
                        results = item.get("countries", [])
                        
                        # Create a temporary DataFrame
                        temp_df = pd.DataFrame(results)
                        
                        if not temp_df.empty:
                            # Rename editors-ceil to editors
                            if "editors-ceil" in temp_df.columns:
                                temp_df.rename(columns={"editors-ceil": "editors"}, inplace=True)
                            
                            # Exclude rows where country is "--"
                            temp_df = temp_df[temp_df["country"] != "--"]

                            if not temp_df.empty:
                                # Add parameter columns
                                temp_df["project"] = project
                                temp_df["activity_level"] = activity_level
                                temp_df["year"] = year
                                temp_df["month"] = month

                                # Reorder columns
                                temp_df = temp_df[["project", "activity_level", "year", "month", "country", "editors"]]

                                # Append to the main DataFrame
                                collected_data = pd.concat([collected_data, temp_df], ignore_index=True)

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data for {project}, {activity_level}, {year}-{month}: {e}")

# Remove duplicates if any
collected_data.drop_duplicates(inplace=True)

# Sort data by project, activity_level, year, month
collected_data.sort_values(by=["project", "activity_level", "year", "month"], inplace=True)

# Save to CSV
collected_data.to_csv(output_csv, index=False)

print(f"Data collection completed. Results saved in {output_csv}")
