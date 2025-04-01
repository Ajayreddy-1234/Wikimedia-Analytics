import requests
import pandas as pd
import os

headers = {
    "accept": "application/json",
    "User-Agent": "WikimediaDataCollector/1.0 (youremail@example.com)"
}

# Read categories from a TSV file
categories_df = pd.read_csv("commons_category_allow_list.tsv", sep='\t', header=None)
categories = categories_df[0].tolist()

# Parameters
scopes = ["shallow", "deep"]
wikis = ["en.wikipedia", "de.wikipedia", "fr.wikipedia", "es.wikipedia", "hi.wikipedia"]
years = ["2023", "2024"]  # Adjust as needed
months = [f"{m:02d}" for m in range(1, 13)]

output_csv = "top_pages_by_category.csv"

if os.path.exists(output_csv):
    collected_data = pd.read_csv(output_csv)
else:
    collected_data = pd.DataFrame(columns=["category", "category_scope", "wiki", "year", "month", "article", "views_ceil", "rank"])

def fetch_commons_data(category, category_scope, wiki, year, month):
    url = (f"https://wikimedia.org/api/rest_v1/metrics/commons-analytics/top-pages-per-category-monthly/"
           f"{category}/{category_scope}/{wiki}/{year}/{month}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

for category in categories:
    for category_scope in scopes:
        for wiki in wikis:
            for year in years:
                for month in months:
                    try:
                        data = fetch_commons_data(category, category_scope, wiki, year, month)
                        items = data.get("items", [])
                        if not items:
                            continue
                        # items contain page data
                        df_temp = pd.DataFrame(items)
                        
                        if df_temp.empty:
                            continue

                        # Rename columns to match desired naming (article, views_ceil)
                        if 'page-title' in df_temp.columns:
                            df_temp.rename(columns={'page-title': 'article', 'pageview-count': 'views_ceil'}, inplace=True)

                        # Add parameter columns
                        df_temp["category"] = category
                        df_temp["category_scope"] = category_scope
                        df_temp["wiki"] = wiki
                        df_temp["year"] = year
                        df_temp["month"] = month

                        # Reorder columns
                        df_temp = df_temp[["category", "category_scope", "wiki", "year", "month", "article", "views_ceil", "rank"]]

                        collected_data = pd.concat([collected_data, df_temp], ignore_index=True)

                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching data for {category}, {category_scope}, {wiki}, {year}-{month}: {e}")
                    except KeyError as ke:
                        print(f"KeyError: {ke} for {category}, {category_scope}, {wiki}, {year}-{month}, skipping.")

# Remove duplicates if any
collected_data.drop_duplicates(inplace=True)

# Sort for readability
collected_data.sort_values(by=["category", "category_scope", "wiki", "year", "month", "rank"], inplace=True)

collected_data.to_csv(output_csv, index=False)
print(f"Data collection completed. Results saved in {output_csv}")
