"""##Graphs"""
import altair as alt
import plotly.express as px
import pandas as pd


"""**Table 1 - Interactive Bar Chart**"""

def get_interactive_bar_chart(merged_data_with_descriptions):
    custom_years = [2000, 2005, 2010, 2015, 2020, 2024]

    year_selector = alt.binding_select(
        options=custom_years,
        name="Year:"
    )

    select_year = alt.selection_point(
        fields=["YEAR"],
        bind=year_selector,
        value=2000
    )

    chart = alt.Chart(merged_data_with_descriptions).mark_bar().encode(
        x=alt.X("Description:N", sort="-y", title="Degree Description"),
        y=alt.Y("Total Count:Q", title="Total Count"),
        tooltip=["YEAR", "Description", "Total Count"]
    ).add_params(
        select_year
    ).transform_filter(
        select_year
    ).properties(
        title="Total Count by Description for Selected Year"
    ).interactive()

    return chart

"""**Table 2**"""

def get_line_chart(merged_data_filtered, cip_descriptions_df):
    # Aggregate data to count degrees per CIPCODE and Year
    degrees_per_year_cipcode = merged_data_filtered.groupby(['YEAR', 'CIPCODE']).size().reset_index(name='Degrees_Awarded')

    # Merge with descriptions to get the 'Description' for each CIPCODE
    degrees_growth_data = pd.merge(degrees_per_year_cipcode, cip_descriptions_df, on='CIPCODE', how='left')

    # Drop rows where Description might be missing
    degrees_growth_data.dropna(subset=['Description'], inplace=True)

    # Calculate total degrees awarded for each description across all years
    total_degrees_by_description = degrees_growth_data.groupby('Description')['Degrees_Awarded'].sum().reset_index(name='Overall_Total_Degrees')

    # Get the top 15 descriptions based on overall total degrees
    top_n = 15
    top_descriptions = total_degrees_by_description.nlargest(top_n, 'Overall_Total_Degrees')['Description'].tolist()

    # Filter data to include only top descriptions
    filtered_degrees_growth_data = degrees_growth_data[degrees_growth_data['Description'].isin(top_descriptions)]

    # Legend selection
    legend_selection = alt.selection_point(
        fields=['Description'],
        bind='legend',
        name='description_selection',
        toggle=True
    )

    # Year interval selection
    year_interval_selection = alt.selection_interval(encodings=['x'], name='year_interval')

    # Create the line chart
    line_chart = alt.Chart(filtered_degrees_growth_data).mark_line(point=True).encode(
        x=alt.X('YEAR:O', axis=alt.Axis(format='d'), title='Year'),
        y=alt.Y('Degrees_Awarded:Q', title='Degrees Awarded'),
        color=alt.Color('Description:N', legend=alt.Legend(title="Degree Description")),
        tooltip=['YEAR:O', 'Description:N', 'Degrees_Awarded:Q'],
        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2))
    ).add_params(
        legend_selection,
        year_interval_selection
    ).transform_filter(
        year_interval_selection
    ).properties(
        title=f'Growth of Top {top_n} Degrees Over Time (Select Year Range)'
    ).interactive()

    return line_chart

"""**Table 3**"""

def get_choropleth_map(data_states):
    data_states_cleaned = data_states.copy()

    data_states_cleaned = data_states_cleaned[
        data_states_cleaned['State'] != 'Total'
    ]
    data_states_cleaned = data_states_cleaned.dropna(subset=['State'])
    data_states_cleaned['State'] = (
        data_states_cleaned['State']
        .astype(str)
        .str.strip()
    )

    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
        'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
        'Wisconsin': 'WI', 'Wyoming': 'WY'
    }

    data_states_cleaned['abbr'] = data_states_cleaned['State'].map(state_abbrev)
    data_states_cleaned = data_states_cleaned.dropna(subset=['abbr'])

    selected_column = 'Computer and Information Sciences and Support Services'

    fig = px.choropleth(
        data_states_cleaned,
        locations='abbr',
        locationmode='USA-states',
        color=selected_column,
        hover_name='State',
        scope='usa',
        color_continuous_scale='Blues',
        labels={selected_column: 'Degrees Awarded'},
        title='Degrees Awarded by State (2023-2024)'
    )

    fig.update_layout(
        width=1000,
        height=600,
        geo=dict(bgcolor='rgba(0,0,0,0)')
    )

    return fig

"""**Table 4**"""

def get_treemap(cipcode_totals_with_description):
    treemap_data = cipcode_totals_with_description.sort_values(by='Total Count', ascending=False)

    fig = px.treemap(
        treemap_data,
        path=[px.Constant("All Degrees"), 'Description'],
        values='Total Count',
        title='Overall Distribution of Degrees by Major',
        color='Total Count',
        color_continuous_scale='Blues',
        hover_data=['CIPCODE', 'Total Count']
    )

    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    return fig

"""**Table 5**"""

def get_growth_bar_chart(degrees_growth_data):
    growth_data = []

    for desc in degrees_growth_data['Description'].unique():
        subset = degrees_growth_data[degrees_growth_data['Description'] == desc].sort_values('YEAR')

        if len(subset) > 1:
            first_year_data = subset.iloc[0]
            last_year_data = subset.iloc[-1]

            initial_degrees = first_year_data['Degrees_Awarded']
            final_degrees = last_year_data['Degrees_Awarded']
            initial_year = first_year_data['YEAR']
            final_year = last_year_data['YEAR']

            if initial_degrees > 0:
                growth_percent = ((final_degrees - initial_degrees) / initial_degrees) * 100
                growth_data.append({
                    'Description': desc,
                    'Initial_Degrees': initial_degrees,
                    'Final_Degrees': final_degrees,
                    'Initial_Year': initial_year,
                    'Final_Year': final_year,
                    'Growth_Percent': growth_percent,
                    'Years_Span': final_year - initial_year
                })
            elif final_degrees > 0:
                growth_data.append({
                    'Description': desc,
                    'Initial_Degrees': initial_degrees,
                    'Final_Degrees': final_degrees,
                    'Initial_Year': initial_year,
                    'Final_Year': final_year,
                    'Growth_Percent': float('inf'),
                    'Years_Span': final_year - initial_year
                })

    growth_df = pd.DataFrame(growth_data)
    growth_df_sorted = growth_df.sort_values(by='Growth_Percent', ascending=False)
    chart_data = growth_df_sorted[growth_df_sorted['Growth_Percent'] != float('inf')].head(20)

    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Growth_Percent:Q', title='Percentage Growth (from initial to final year)'),
        y=alt.Y('Description:N', sort='-x', title='Field Description'),
        tooltip=[
            'Description:N',
            'Initial_Degrees:Q',
            'Final_Degrees:Q',
            'Initial_Year:O',
            'Final_Year:O',
            alt.Tooltip('Growth_Percent:Q', format='.2f', title='Growth %')
        ]
    ).properties(
        title='Top 20 Fields by Percentage Growth (from first to last recorded year)'
    ).interactive()

    return bar_chart