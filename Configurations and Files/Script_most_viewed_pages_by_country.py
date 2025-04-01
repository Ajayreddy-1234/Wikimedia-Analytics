import requests
import pandas as pd
import os

headers = {
    "accept": "application/json",
    "User-Agent": "WikimediaDataCollector/1.0 (youremail@example.com)"
}

# Top 50 countries list (based on previous data)
countries = [
    "US","GB","IN","CA","AU","DE","PH","ID","BR","IT",
    "FR","NL","IE","MY","ES","BD","GR","JP","NZ","PL",
    "SE","HK","MX","NG","IL","KR","CH","BE","AR","PT",
    "NO","RO","ZA","TW","FI","CZ","RS","BG","UA","DK",
    "HU","NP","AT","CL","HR","LK","PE","CO","KE","LT"
]

access_methods = ["desktop"]
years = [str(y) for y in range(2023, 2025)]  # 2018 to 2024
months = [f"{m:02d}" for m in range(1, 13)]
days = [f"{d:02d}" for d in range(1, 32)]

output_csv = "top_pages_by_country.csv"

if os.path.exists(output_csv):
    collected_data = pd.read_csv(output_csv)
else:
    collected_data = pd.DataFrame(columns=["country", "access", "year", "month", "day", "project", "article", "views_ceil", "rank"])

def fetch_top_pages_country(country, access, year, month, day):
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top-per-country/"
           f"{country}/{access}/{year}/{month}/{day}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

for country in countries:
    for access in access_methods:
        for year in years:
            for month in months:
                for day in days:
                    try:
                        data = fetch_top_pages_country(country, access, year, month, day)
                        items = data.get("items", [])
                        if not items:
                            continue
                        item = items[0]
                        articles = item.get("articles", [])
                        if not articles:
                            continue
                        
                        temp_df = pd.DataFrame(articles)
                        # Columns from API: article, project, views_ceil, rank
                        # Add country, access, year, month, day
                        temp_df["country"] = country
                        temp_df["access"] = access
                        temp_df["year"] = year
                        temp_df["month"] = month
                        temp_df["day"] = day

                        temp_df = temp_df[["country", "access", "year", "month", "day", "project", "article", "views_ceil", "rank"]]

                        collected_data = pd.concat([collected_data, temp_df], ignore_index=True)

                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching data for {country}, {access}, {year}-{month}-{day}: {e}")
                    except KeyError as ke:
                        print(f"KeyError: {ke} for {country}, {access}, {year}-{month}-{day}, skipping.")

# Remove duplicates if any
collected_data.drop_duplicates(inplace=True)

# Sort the data for readability
collected_data.sort_values(by=["country", "access", "year", "month", "day", "rank"], inplace=True)

collected_data.to_csv(output_csv, index=False)
print(f"Data collection completed. Results saved in {output_csv}")
