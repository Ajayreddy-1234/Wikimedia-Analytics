import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date

# Set page configuration for wide view
st.set_page_config(page_title="Wikimedia Dashboard", layout="wide")

# Set up the Streamlit app
st.title("Wikimedia Dashboard")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Pageviews", "Unique Devices", "Editors", "Most Popular Pages"])

########################################
# Tab 1: Pageviews
########################################
with tab1:
    st.header("Pageviews")

    # Inputs for Pageviews tab
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        projects = [
            "en.wikipedia.org",
            "de.wikipedia.org",
            "fr.wikipedia.org",
            "es.wikipedia.org",
            "commons.wikimedia.org",
            "meta.wikimedia.org",
            "wikidata.org"
        ]
        # Add a unique key for this selectbox
        project = st.selectbox("Select Project", projects, key="pageviews_project")
    with col2:
        granularity_options = ["daily", "monthly"]
        granularity = st.selectbox("Select Granularity", granularity_options, key="pageviews_granularity")
    with col3:
        default_start_date = date(2024, 10, 1)
        start_date = st.date_input("Start Date", default_start_date, key="pageviews_start_date")
    with col4:
        default_end_date = date(2024, 11, 30)
        end_date = st.date_input("End Date", default_end_date, key="pageviews_end_date")

    # Format dates for API
    start = start_date.strftime("%Y%m%d00")
    end = end_date.strftime("%Y%m%d00")

    # Custom User-Agent header
    headers = {
        "accept": "application/json",
        "User-Agent": "WikimediaDashboard/1.0 (your_email@example.com)"
    }

    # Fetch data and display chart
    if st.button("Fetch Pageviews Data", key="fetch_pageviews"):
        api_url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/{project}/all-access/all-agents/{granularity}/{start}/{end}"

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if items:
                df = pd.DataFrame(items)
                df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d%H")

                # Plot the data
                st.write("### Pageviews Line Chart")
                fig = px.line(
                    df,
                    x="timestamp",
                    y="views",
                    title=f"Pageviews for {project}",
                    labels={"timestamp": "Time", "views": "Page Views"}
                )
                st.plotly_chart(fig)
            else:
                st.warning("No data available for the selected parameters.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")

########################################
# Tab 2: Unique Devices
########################################
with tab2:
    st.header("Unique Devices")

    # Inputs for Unique Devices tab
    col1, col2, col3 = st.columns(3)
    with col1:
        default_start_date_devices = date(2023, 1, 1)
        start_date_devices = st.date_input("Start Date", default_start_date_devices, key="unique_devices_start_date")
    with col2:
        default_end_date_devices = date(2024, 1, 1)
        end_date_devices = st.date_input("End Date", default_end_date_devices, key="unique_devices_end_date")
    with col3:
        project_devices = st.selectbox(
            "Select Project for Unique Devices",
            ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org"],
            key="unique_devices_project"
        )

    # Format dates for API
    start_devices = start_date_devices.strftime("%Y%m%d")
    end_devices = end_date_devices.strftime("%Y%m%d")

    # Fetch and display unique devices data
    if st.button("Fetch Unique Devices Data", key="fetch_unique_devices"):
        api_url = f"https://wikimedia.org/api/rest_v1/metrics/unique-devices/{project_devices}/all-sites/daily/{start_devices}/{end_devices}"

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if items:
                df = pd.DataFrame(items)
                df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d")

                # Plot unique devices data
                st.write("### Unique Devices Chart")
                fig = px.area(
                    df,
                    x="timestamp",
                    y="devices",
                    title=f"Unique Devices for {project_devices}",
                    labels={"timestamp": "Time", "devices": "Unique Devices"}
                )
                st.plotly_chart(fig)
            else:
                st.warning("No data available for the selected parameters.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")

########################################
# Tab 3: Editors
########################################
with tab3:
    st.header("Editors")

    # Create subtabs for Editors
    editors_tab1, editors_tab2 = st.tabs(["Aggregate Editors", "Editors by Country"])

    # Subtab 1: Aggregate Editors
    with editors_tab1:
        st.subheader("Aggregate Editors")

        # Inputs for aggregate editors API
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            project_editors = st.selectbox(
                "Project",
                ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org"],
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

        # Format dates for API
        start_editors = start_date_editors.strftime("%Y%m%d")
        end_editors = end_date_editors.strftime("%Y%m%d")

        if st.button("Fetch Aggregate Editors Data", key="fetch_aggregate_editors"):
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
                        # The timestamp is ISO format
                        df["timestamp"] = pd.to_datetime(df["timestamp"])

                        st.write("### Number of Editors Over Time")
                        fig = px.line(
                            df,
                            x="timestamp",
                            y="editors",
                            title=f"Editors for {project_editors}",
                            labels={"timestamp": "Time", "editors": "Number of Editors"}
                        )
                        st.plotly_chart(fig)
                    else:
                        st.warning("No data in 'results' for the selected parameters.")
                else:
                    st.warning("No data available for the selected parameters.")
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")

    # Subtab 2: Editors by Country
    with editors_tab2:
        st.subheader("Editors by Country")

        # Inputs for editors by country API
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            project_country = st.selectbox(
                "Project",
                ["en.wikipedia.org", "de.wikipedia.org", "fr.wikipedia.org"],
                key="country_editors_project"
            )
        with col2:
            # activity-level allowed: "5..99-edits" or "100..-edits"
            activity_level_country = st.selectbox("Activity Level", ["5..99-edits", "100..-edits"], key="country_editors_activity_level")
        with col3:
            year_country = st.selectbox("Year", ["2023", "2024"], key="country_editors_year")
        with col4:
            month_country = st.selectbox("Month", [f"{i:02d}" for i in range(1, 13)], key="country_editors_month")

        if st.button("Fetch Editors by Country Data", key="fetch_editors_by_country"):
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
                    if countries:
                        df = pd.DataFrame(countries)

                        st.write("### Editors by Country")
                        fig = px.bar(
                            df,
                            x="editors-ceil",
                            y="country",
                            title=f"Editors by Country for {project_country} ({year_country}-{month_country})",
                            labels={"editors-ceil": "Number of Editors", "country": "Country"},
                            orientation="h"
                        )
                        # Reverse the order so the largest bar is on top
                        fig.update_layout(yaxis=dict(autorange="reversed"))
                        st.plotly_chart(fig)
                    else:
                        st.warning("No country data available for the selected parameters.")
                else:
                    st.warning("No data available for the selected parameters.")
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")

########################################
# Tab 4: Most Viewed Pages
########################################
with tab4:
    st.header("Most Viewed Pages")

    # Inputs for Most Viewed Pages tab
    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox("Select Country", ["IN", "US", "UK", "FR", "DE", "CA"], key="most_viewed_country")
    with col2:
        access = st.selectbox("Select Access", ["all-access", "desktop", "mobile-web"], key="most_viewed_access")
    with col3:
        date_input = st.date_input("Select Date", date(2023, 1, 1), key="most_viewed_date")

    # Format date for API
    year = date_input.strftime("%Y")
    month = date_input.strftime("%m")
    day = date_input.strftime("%d")

    # Fetch data and display chart
    if st.button("Fetch Most Viewed Pages Data", key="fetch_most_viewed"):
        api_url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top-per-country/{country}/{access}/{year}/{month}/{day}"

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract articles data
            articles = data.get("items", [])[0].get("articles", [])
            if articles:
                df = pd.DataFrame(articles)
                df = df[~df['article'].str.contains('XX', case=False, na=False)].reset_index(drop=True)

                # Sort by views and take the top 15
                df = df.sort_values(by="views_ceil", ascending=False).head(15)

                # Plot the data
                st.write("### Most Viewed Pages")
                fig = px.bar(
                    df,
                    x="views_ceil",
                    y="article",
                    title=f"Most Viewed Pages in {country} on {date_input}",
                    labels={"views_ceil": "Views", "article": "Article"},
                    orientation="h",
                    height=600
                )

                fig.update_layout(
                    yaxis=dict(title="", automargin=True),
                    xaxis=dict(title="Views", tickformat=",d"),
                    title=dict(font=dict(size=20)),
                    margin=dict(l=100, r=30, t=60, b=30),
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for the selected parameters.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")
