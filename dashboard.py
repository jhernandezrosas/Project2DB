import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import numpy as np

from project_2 import (
    get_interactive_bar_chart,
    get_line_chart,
    get_growth_bar_chart,
    get_treemap
)

st.set_page_config(page_title="Project 2 Dashboard", layout="wide")

# Loading data
data00 = pd.read_csv("CSVFiles/data00_cleaned.csv")
data05 = pd.read_csv("CSVFiles/data05_cleaned.csv")
data10 = pd.read_csv("CSVFiles/data10_cleaned.csv")
data15 = pd.read_csv("CSVFiles/data15_cleaned.csv")
data20 = pd.read_csv("CSVFiles/data20_cleaned.csv")
data24 = pd.read_csv("CSVFiles/data24_cleaned.csv")
data_states_cleaned= pd.read_csv("CSVFiles/data_states_cleaned.csv")

data00["YEAR"] = 2000
data05["YEAR"] = 2005
data10["YEAR"] = 2010
data15["YEAR"] = 2015
data20["YEAR"] = 2020
data24["YEAR"] = 2024

merged_df = pd.concat(
    [data00, data05, data10, data15, data20, data24],
    ignore_index=True
)

cip_descriptions_df = pd.read_csv(
    "CSVFiles/CIPCODES+Major - Sheet1.csv",
    header=None,
    names=["CIPCODE", "Description"]
)

merged_df["CIPCODE"] = merged_df["CIPCODE"].astype(str)
cip_descriptions_df["CIPCODE"] = cip_descriptions_df["CIPCODE"].astype(str)

merged_data_filtered = merged_df[merged_df["AWLEVEL"] == 5].copy()

merged_data_with_descriptions = pd.merge(
    merged_data_filtered,
    cip_descriptions_df,
    on="CIPCODE",
    how="left"
)

merged_data_with_descriptions = merged_data_with_descriptions.dropna(
    subset=["Description"]
)

cipcode_totals_with_description = (
    merged_data_with_descriptions
    .groupby(["CIPCODE", "Description"])
    .size()
    .reset_index(name="Total Count")
)

degrees_per_year_cipcode = (
    merged_data_filtered
    .groupby(["YEAR", "CIPCODE"])
    .size()
    .reset_index(name="Degrees_Awarded")
)

degrees_growth_data = pd.merge(
    degrees_per_year_cipcode,
    cip_descriptions_df,
    on="CIPCODE",
    how="left"
)

degrees_growth_data = degrees_growth_data.dropna(subset=["Description"])
bar_chart_data = (
    merged_data_with_descriptions
    .groupby(["YEAR", "CIPCODE", "Description"])
    .size()
    .reset_index(name="Total Count")
)

# Dashboard
st.title("Project 2 Dashboard")

tabs = st.tabs(["Intro", "Table 1", "Table 2", "Table 3", "Table 4", "Table 5"])

with tabs[0]:
    st.header("Project 2")
    st.subheader("Computer Science and Engineering Majors Growth from 2000 to 2024.")
    st.image("images/compsciengin.webp")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Interactive Bar Graph")
        st.write("The bar chart shows the top degree descriptions for a selected year. "
                 "Users can choose a year using both a dropdown menu and a slider. "
                 "This makes it easy to compare degree popularity across different years "
                 "and see which majors had the highest number of degrees awarded.")
        st.subheader("Line Graph")
        st.write("The line graph shows how degree fields changed over time. "
                 "Each colored line represents a different degree of description. "
                 "Users can click the legend to focus on one field at a time or all fields at once. "
                 "This graph shows long term growth trends.")
    with col2:
        st.subheader("State Map")
        st.write("The state map shows where degrees were awarded across the United States for 2023-2024. "
                 "This helps identify which states have the highest number of Computer Science "
                 "or Engineering related degrees.")

    with col3:
        st.subheader("Tree Map")
        st.write("The tree map shows the overall distribution of degrees by major. "
                 "Larger boxes represent fields with more degrees awarded. "
                 "This is useful because it gives a quick visual summary of "
                 "which fields make up the largest share of data.")
        st.subheader("Growth bar Graph")
        st.write("The growth bar chart displays the percentage growth of different "
                 "Computer Science and Engineering degree fields from the earliest recorded year (2000) "
                 "to the most recent year (2024). The chart highlights which degree programs have grown the "
                 "fastest over time with Artificial Intelligence and related fields showing some of the highest growth. "
                 "This is helpful because it shows how technology trends influence education. ")

with tabs[1]:
    st.header("Top Computer Science/Engineering Degrees Awarded by Field")
    with st.container():
        st.write("This interactive bar chart displays the top 20 STEM degree fields "
                 " for the selected year, allowing users to compare the number of degrees "
                 "awarded across disciplines.")

        selected_year = st.selectbox(
            "Choose a year:",
            [2000, 2005, 2010, 2015, 2020, 2024]
        )

        slider_year = st.slider(
            "Or use the slider:",
            min_value=2000,
            max_value=2024,
            value=selected_year,
            step=1
        )

        selected_year = slider_year

        chart1_data = bar_chart_data[
            bar_chart_data["YEAR"] == selected_year
            ].copy()

        st.write("Rows found for this year:", len(chart1_data))

        chart1_data = chart1_data.sort_values(
            "Total Count",
            ascending=False
        ).head(20)

        chart = alt.Chart(chart1_data).mark_bar().encode(
            x=alt.X("Total Count:Q", title="Total Count"),
            y=alt.Y("Description:N", sort="-x", title="Degree Description"),
            tooltip=["YEAR", "Description", "Total Count"]
        ).properties(
            title=f"Top 20 Degree Descriptions in {selected_year}",
            height=500
        )

        st.altair_chart(chart, use_container_width=True)

    with tabs[2]:
        st.header("Degree Growth Timeline")
        st.subheader("The visualization highlights how degree programs have increased "
                     "or decreased in popularity from 2000 to 2024.”")
        st.altair_chart(
            get_line_chart(merged_data_filtered, cip_descriptions_df),
            use_container_width=True
        )


with tabs[3]:
    st.header("Computer Science/Engineering Degrees by State")
    st.subheader("This choropleth map visualizes the distribution of STEM degrees awarded "
                 "across U.S. states, allowing users to compare regional differences in education trends.”")

    fig_map = px.choropleth(
        data_states_cleaned,
        locations="State",
        locationmode="USA-states",
        color="Computer and Information Sciences and Support Services",
        hover_name="State",
        scope="usa",
        color_continuous_scale="Blues",
        labels={
            "Computer and Information Sciences and Support Services":
            "Degrees Awarded"
        },
        title="Computer and Information Sciences Degrees by State"
    )

    fig_map.update_layout(
        height=600,
        geo=dict(bgcolor="rgba(0,0,0,0)")
    )


    st.plotly_chart(fig_map, use_container_width=True, key="state_choropleth_chart")


with tabs[4]:
    st.header("Degree Growth Comparison")
    st.subheader("This bar chart compares the percentage growth of Computer Science and Engineering "
                 " degree fields over time, highlighting which programs experienced the largest increases")
    st.altair_chart(
        get_growth_bar_chart(degrees_growth_data),
        use_container_width=True
    )

with tabs[5]:
    st.header("Computer Science/Engineering Degree Distribution Overview")
    st.subheader("This treemap visualizes the proportion of degrees awarded across Computer Science and Engineering fields,"
                 "where larger sections represent programs with higher degree totals.")
    st.plotly_chart(
        get_treemap(cipcode_totals_with_description),
        use_container_width=True,
        key="treemap_chart")
