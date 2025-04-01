import requests
import pandas as pd
import os

headers = {
    "accept": "application/json",
    "User-Agent": "WikimediaDataCollector/1.0 (youremail@example.com)"
}

projects = ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org", "es.wikipedia.org"]
access_methods = ["desktop"]  # exclude all-access
years = [str(y) for y in range(2023, 2025)]  # 2018 to 2024
months = [f"{m:02d}" for m in range(1, 13)]
days = [f"{d:02d}" for d in range(1, 32)]

output_csv = "most_viewed_pages.csv"

if os.path.exists(output_csv):
    collected_data = pd.read_csv(output_csv)
else:
    collected_data = pd.DataFrame(columns=["project", "access", "year", "month", "day", "article", "views", "rank"])

def fetch_top_pages(project, access, year, month, day):
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
           f"{project}/{access}/{year}/{month}/{day}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

for project in projects:
    for access in access_methods:
        for year in years:
            for month in months:
                for day in days:
                    try:
                        data = fetch_top_pages(project, access, year, month, day)
                        items = data.get("items", [])
                        if not items:
                            continue
                        # items[0] should contain the articles list
                        articles = items[0].get("articles", [])
                        if not articles:
                            continue

                        temp_df = pd.DataFrame(articles)
                        # temp_df should have columns: article, views, rank
                        # Add project, access, year, month, day
                        temp_df["project"] = project
                        temp_df["access"] = access
                        temp_df["year"] = year
                        temp_df["month"] = month
                        temp_df["day"] = day

                        # Reorder columns
                        temp_df = temp_df[["project", "access", "year", "month", "day", "article", "views", "rank"]]

                        collected_data = pd.concat([collected_data, temp_df], ignore_index=True)

                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching data for {project}, {access}, {year}-{month}-{day}: {e}")
                    except KeyError as ke:
                        print(f"KeyError: {ke} for {project}, {access}, {year}-{month}-{day}, skipping.")

# Remove duplicates if any
collected_data.drop_duplicates(inplace=True)

# Sort the data for readability
collected_data.sort_values(by=["project", "access", "year", "month", "day", "rank"], inplace=True)

collected_data.to_csv(output_csv, index=False)
print(f"Data collection completed. Results saved in {output_csv}")
