import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date
import pycountry

# Set page configuration for wide view
st.set_page_config(page_title="Wikimedia Dashboard", layout="wide")

# Set up the Streamlit app
st.title("Wikimedia Dashboard")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Pageviews", "Most Popular Pages", "Page Views for an Article", "Editors"])

def fetch_pageviews_data(input_dict):
    url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/{project}/{all_access}/{agent}/{granularity}/{start}/{end}"
    api_url = url.format(**input_dict)
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    items = data.get("items", [])
    return items

def get_country_name(country_code):
        country = pycountry.countries.get(alpha_2=country_code.upper())
        return country.name if country else "Invalid country code"

def fetch_most_popular_pages(popular_dict):
    if popular_dict['country'] == 'ALL':
        url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/{access}/{year}/{month}/{day}"
    else:
        url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top-per-country/{country}/{access}/{year}/{month}/{day}"
    api_url = url.format(**popular_dict)
    response = requests.get(api_url, headers=headers)  # Add headers to the request
    response.raise_for_status()
    data = response.json()
    # Extract articles data
    articles = data.get("items", [])[0].get("articles", [])
    return articles

def fetch_most_pageviews_category_data(most_by_cat_input):
    url = "https://wikimedia.org/api/rest_v1/metrics/commons-analytics/top-pages-per-category-monthly/{category}/{category_scope}/{wiki}/{year}/{month}"
    api_url = url.format(**most_by_cat_input)
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    return data


# Tab 1: Pageviews
with tab1:
    st.header("Pageviews")

    # Inputs specific to Pageviews tab, displayed horizontally
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        projects = [
            "all-projects",
            "en.wikipedia.org",
            "de.wikipedia.org",
            "fr.wikipedia.org",
            "es.wikipedia.org",
            "hi.wikipedia.org",
            "commons.wikimedia.org",
            "meta.wikimedia.org"
        ]
        project = st.selectbox("Select Project", projects)
    with col2:
        granularity_options = ["daily", "monthly"]
        granularity = st.selectbox("Select Granularity", granularity_options)
    with col3:
        agent_options = ["all-agents", "user", "spider", "automated"]
        agent = st.selectbox('Select Agent', agent_options, index = 1)
    with col4:
        default_start_date = date(2024, 6, 1)
        start_date = st.date_input("Start Date", default_start_date, key="pageviews_start_date")
    with col5:
        default_end_date = date(2024, 12, 1)
        end_date = st.date_input("End Date", default_end_date, key="pageviews_end_date")

    # Format dates for API
    start = start_date.strftime("%Y%m%d00")
    end = end_date.strftime("%Y%m%d00")

    page_views_dict = {'project' : project, 'all_access' : 'all-access', 'agent' : agent, 'granularity' : granularity, 'start' : start, 'end' : end}
    page_views_dict_desk = page_views_dict.copy()
    page_views_dict_desk['all_access'] = 'desktop'

    # Custom User-Agent header
    headers = {
        "accept": "application/json",
        "User-Agent": "WikimediaDashboard/1.0 (your_email@example.com)"
    }

    # Fetch data and display chart
    if st.button("Run"):
        try:
            items = fetch_pageviews_data(page_views_dict)
            items_desktop =  fetch_pageviews_data(page_views_dict_desk)
            if items:
                df = pd.DataFrame(items)
                df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d%H")
                df = df[['timestamp', 'views']]

                df_desk = pd.DataFrame(items_desktop)
                df_desk["timestamp"] = pd.to_datetime(df_desk["timestamp"], format="%Y%m%d%H")
                df_desk = df_desk[['timestamp', 'views']]


                df = df.merge(df_desk, on = ['timestamp'], how = 'left')
                df.rename({'views_x' : 'Overall Views', 'views_y' : 'Desktop Views'}, axis = 1, inplace = True)

                df['Mobile Views'] = df['Overall Views'] - df['Desktop Views']

                # Plot the data
                fig = px.line(
                    df,
                    x="timestamp",
                    y="Overall Views",
                    title=f"Pageviews for {project}",
                    labels={"timestamp": "Time", "views": "Page Views"}
                )
                st.plotly_chart(fig)

                fig = px.bar(
                    df,
                    x="timestamp",
                    y=["Desktop Views", "Mobile Views"],
                    title="Pageviews (Mobile vs Desktop)",
                    labels={"value": "Views", "timestamp": "Date", "variable" : "Access Type"},
                    barmode="stack"
                )
                st.plotly_chart(fig)
            else:
                st.warning("No data available for the selected parameters.")
        except requests.exceptions.RequestException as e:
            st.write(f"No data available for the selected parameters.")


# Tab 2: Most Viewed Pages
with tab2:
    st.header("Most Viewed Pages")

    # Inputs for API parameters
    col1, col2, col3 = st.columns(3)
    country_codes = [country.alpha_2 for country in pycountry.countries]
    country_names = [get_country_name(x) for x in country_codes]
    country_codes = ['ALL'] + country_codes
    country_names = ['All Countries'] + country_names
    country_dict = dict(zip(country_names, country_codes))

    with col1:
        ct_name = st.selectbox("Select Country", country_names, key="most_viewed_country", index = 0)
        country = country_dict[ct_name]
    with col2:
        access = st.selectbox("Select Access", ["all-access", "desktop", "mobile-web"], key="most_viewed_access")
    with col3:
        date_input = st.date_input("Select Date", date(2023, 1, 1), key="most_viewed_date")

    # Format date for API
    year = date_input.strftime("%Y")
    month = date_input.strftime("%m")
    day = date_input.strftime("%d")

    # Custom User-Agent header
    headers = {
        "User-Agent": "WikimediaDashboard/1.0 (your_email@example.com)",
        "accept": "application/json"
    }

    popular_dict = {'country' : country, 'access' : access, 'year' : year, 'month':month, 'day' : day}

    # Fetch data and display chart
    if st.button("Run", key="fetch_most_viewed"):

        try:
            articles = fetch_most_popular_pages(popular_dict)
            if articles:
                df = pd.DataFrame(articles)
                df.rename({'views' : 'views_ceil'}, axis = 1, inplace = True)
                df = df[~df['article'].str.contains('XX', case=False, na=False)].reset_index(drop=True)

                # Sort by views and take the top 15
                df = df.sort_values(by="views_ceil", ascending=False).head(15)
                df = df.sort_values(by="views_ceil", ascending=True)
                # Plot the data
                fig = px.bar(
                    df,
                    x="views_ceil",
                    y="article",
                    title=f"Most Viewed Pages in {ct_name} on {date_input}",
                    labels={"views_ceil": "Views", "article": "Article"},
                    orientation="h",
                    height=600,  # Adjust height for better spacing
                )

                # Update layout for better readability
                fig.update_layout(
                    yaxis=dict(title="", automargin=True),
                    xaxis=dict(title="Views", tickformat=",d"),  # Format views with commas
                    title=dict(font=dict(size=20)),
                    margin=dict(l=100, r=30, t=60, b=30),  # Adjust margins
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for the selected parameters.")
        except requests.exceptions.RequestException as e:
            st.write("No data available for the selected parameters.")

with tab3:

    st.header("Page Views for an Article")

    # Create columns for horizontal layout
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        access = st.selectbox(
            'Access', 
            ['all-access', 'desktop', 'mobile-app', 'mobile-web'], 
            key='article_pageview_access'
        )

    with col2:
        agent = st.selectbox(
            'Agent', 
            ['all-agents', 'user', 'spider', 'bot'], 
            key='article_pageview_agent'
        )

    with col3:
        article = st.text_input(
            'Article Name', 
            value='Donald_Trump', 
            key='article_pageview_article'
        )

    with col4:
        granularity = st.selectbox(
            'Granularity', 
            ['daily', 'monthly'], 
            key='article_pageview_granularity'
        )
    default_start_date = date(2024, 1, 1)
    with col5:
        start_date = st.date_input(
            'Start Date',
            default_start_date, 
            key='article_pageview_start_date'
        )
    default_end_date = date(2024, 12, 1)
    with col6:
        end_date = st.date_input(
            'End Date', 
            default_end_date,
            key='article_pageview_end_date'
        )

    project = 'en.wikipedia.org'

    # Button to submit and fetch data
    if st.button('Run', key='article_pageview_fetch_data'):
        # Convert dates to the required format (YYYYMMDDHH)
        start = start_date.strftime('%Y%m%d00')
        end = end_date.strftime('%Y%m%d00')

        # API URL
        api_url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}"

        headers = {
            "User-Agent": "MyWikimediaApp/1.0 (mailto:example@example.com)",  # Replace with your email
            "accept": "application/json"
        }

        try:
            # Request data from the API
            response = requests.get(api_url, headers=headers)
            response.raise_for_status() 
            data = response.json()
            
            if 'items' in data:
                df = pd.DataFrame(data['items'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H')
                df['views'] = df['views'].astype(int)

                # Plot the line chart using Plotly
                st.subheader("Pageviews Over Time")
                fig = px.line(
                    df, 
                    x='timestamp', 
                    y='views', 
                    title=f'Pageviews for {article} ({granularity})', 
                    labels={'timestamp': 'Date', 'views': 'Pageviews'}
                )
                st.plotly_chart(fig)
            else:
                st.warning("No data found for the selected parameters.")
        except requests.exceptions.RequestException as e:
            st.write("No data available for the selected parameters.")

    


with tab4:
    st.header("Editors")
    editors_tab1, editors_tab2 = st.tabs(["Aggregate Editors", "Editors by Country"])

    with editors_tab1:
        st.subheader("Aggregate Editors")
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            project_editors = st.selectbox(
                "Project",
                ["en.wikipedia.org",
                 "de.wikipedia.org",
                 "fr.wikipedia.org",
                 "es.wikipedia.org",
                 "hi.wikipedia.org",
                 "commons.wikimedia.org",
                 "meta.wikimedia.org"],
                key="aggregate_editors_project"
            )
        with col2:
            editor_types = ["all-editor-types", "anonymous", "group-bot", "name-bot", "user"]
            editor_type = st.selectbox("Editor Type", editor_types, key="aggregate_editors_type")
        with col3:
            page_types = ["all-page-types", "content", "non-content"]
            page_type = st.selectbox("Page Type", page_types, key="aggregate_editors_page_type")
        with col4:
            activity_levels = ["all-activity-levels", "1..4-edits", "5..24-edits", "25..99-edits", "100..-edits"]
            activity_level = st.selectbox("Activity Level", activity_levels, key="aggregate_editors_activity_level")
        with col5:
            granularity_editors = st.selectbox("Granularity", ["daily", "monthly"], key="aggregate_editors_granularity")
        with col6:
            default_start_date_editors = date(2023, 1, 1)
            start_date_editors = st.date_input("Start Date", default_start_date_editors, key="aggregate_editors_start_date")
        with col7:
            default_end_date_editors = date(2024, 1, 1)
            end_date_editors = st.date_input("End Date", default_end_date_editors, key="aggregate_editors_end_date")

        start_editors = start_date_editors.strftime("%Y%m%d")
        end_editors = end_date_editors.strftime("%Y%m%d")

        if st.button("Run", key="fetch_aggregate_editors"):
            api_url = (
                f"https://wikimedia.org/api/rest_v1/metrics/editors/aggregate/"
                f"{project_editors}/{editor_type}/{page_type}/{activity_level}/{granularity_editors}/{start_editors}/{end_editors}"
            )
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
                if items and "results" in items[0]:
                    results = items[0].get("results", [])
                    if results:
                        df = pd.DataFrame(results)
                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                        fig = px.line(
                            df,
                            x="timestamp",
                            y="editors",
                            title=f"Editors for {project_editors}",
                            labels={"timestamp": "Time", "editors": "Number of Editors"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data in 'results' for the selected parameters.")
                else:
                    st.warning("No data available for the selected parameters.")
            except requests.exceptions.RequestException as e:
                st.write("No data available for the selected parameters.")

    with editors_tab2:
        st.subheader("Editors by Country")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            project_country = st.selectbox(
                "Project",
                ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org"],
                key="country_editors_project"
            )
        with col2:
            activity_level_country = st.selectbox("Activity Level", ["5..99-edits", "100..-edits"], key="country_editors_activity_level")
        with col3:
            year_country = st.selectbox("Year", list(range(2018, 2025)), key="country_editors_year")
        with col4:
            month_country = st.selectbox("Month", [f"{i:02d}" for i in range(1, 13)], key="country_editors_month")

        if st.button("Run", key="fetch_editors_by_country"):
            api_url = (
                f"https://wikimedia.org/api/rest_v1/metrics/editors/by-country/"
                f"{project_country}/{activity_level_country}/{year_country}/{month_country}"
            )
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
                if items and "countries" in items[0]:
                    countries = items[0].get("countries", [])

                    # Sort by editors-ceil and take top 50 (excluding '--')
                    df = pd.DataFrame(countries)
                    df = df[df["country"] != "--"]
                    df = df.sort_values(by="editors-ceil", ascending=False).head(50)

                    country_name_map = {
                        "US": "United States",
                        "GB": "United Kingdom",
                        "IN": "India",
                        "CA": "Canada",
                        "AU": "Australia",
                        "DE": "Germany",
                        "PH": "Philippines",
                        "ID": "Indonesia",
                        "BR": "Brazil",
                        "IT": "Italy",
                        "FR": "France",
                        "NL": "Netherlands",
                        "IE": "Ireland",
                        "MY": "Malaysia",
                        "ES": "Spain",
                        "BD": "Bangladesh",
                        "GR": "Greece",
                        "JP": "Japan",
                        "NZ": "New Zealand",
                        "PL": "Poland",
                        "SE": "Sweden",
                        "HK": "Hong Kong",
                        "MX": "Mexico",
                        "NG": "Nigeria",
                        "IL": "Israel",
                        "KR": "South Korea",
                        "CH": "Switzerland",
                        "BE": "Belgium",
                        "AR": "Argentina",
                        "PT": "Portugal",
                        "NO": "Norway",
                        "RO": "Romania",
                        "ZA": "South Africa",
                        "TW": "Taiwan",
                        "FI": "Finland",
                        "CZ": "Czech Republic",
                        "RS": "Serbia",
                        "BG": "Bulgaria",
                        "UA": "Ukraine",
                        "DK": "Denmark",
                        "HU": "Hungary",
                        "NP": "Nepal",
                        "AT": "Austria",
                        "CL": "Chile",
                        "HR": "Croatia",
                        "LK": "Sri Lanka",
                        "PE": "Peru",
                        "CO": "Colombia",
                        "KE": "Kenya",
                        "LT": "Lithuania"
                    }

                    df["country_name"] = df["country"].map(country_name_map)
                    df = df.dropna(subset=["country_name"])
                    if df.empty:
                        st.warning("No mapped country data available for the selected parameters.")
                    else:
                        fig_map = px.choropleth(
                            df,
                            locations="country_name",
                            locationmode='country names',
                            color="editors-ceil",
                            hover_name="country_name",
                            color_continuous_scale="Viridis",
                            title=f"Top 50 Countries by Editors for {project_country} ({year_country}-{month_country})"
                        )
                        fig_map.update_layout(height=800)
                        st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.warning("No data available for the selected parameters.")
            except requests.exceptions.RequestException as e:
                st.write("No data available for the selected parameters.")