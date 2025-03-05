import zipfile
import geopandas
import numpy as np
import pandas as pd

import streamlit as st
import plotly.express as px

def read_and_preprocess_data() -> tuple[pd.DataFrame, geopandas.GeoDataFrame]:
    """
    Reads Uber data from the zip file and preprocesses it.
    """
    
    with zipfile.ZipFile('data/uber-data.zip') as zip:
        with zip.open('madrid-barrios-2020-1-All-DatesByHourBucketsAggregate.csv') as csv:
            data = pd.read_csv(csv)
        with zip.open('madrid_barrios.json') as geojson:
            codes = geopandas.read_file(geojson, encoding="utf-8")

    # change data types in codes because they are not the same as in data
    codes['GEOCODIGO'] = codes['GEOCODIGO'].astype(int)
    codes['MOVEMENT_ID'] = codes['MOVEMENT_ID'].astype(int)

    codes["DISPLAY_NAME"] = codes["DISPLAY_NAME"].str.split().str[1:].str.join(" ")

    # Merge the data with the codes (source)
    data = data.merge(codes[["GEOCODIGO","MOVEMENT_ID","DISPLAY_NAME"]], left_on="sourceid", right_on="MOVEMENT_ID", how="left")
    data = data.rename(columns={"GEOCODIGO":"src_neigh_code", "DISPLAY_NAME":"src_neigh_name"}).drop(columns=["MOVEMENT_ID"])

    data = data.merge(codes[["GEOCODIGO","MOVEMENT_ID","DISPLAY_NAME"]], left_on="dstid", right_on="MOVEMENT_ID", how="left")
    data = data.rename(columns={"GEOCODIGO":"dst_neigh_code", "DISPLAY_NAME":"dst_neigh_name"}).drop(columns=["MOVEMENT_ID"])

    # Create a new date column
    data["year"] = "2020"
    data["date"] = pd.to_datetime(data["day"].astype(str)+data["month"].astype(str)+data["year"].astype(str)+":"+data["start_hour"].astype(str), format="%d%m%Y:%H")

    # Create a new day_period column
    data["day_period"] = data.start_hour.astype(str) + "-" + data.end_hour.astype(str)
    data["day_of_week"] = data.date.dt.weekday
    data["day_of_week_str"] = data.date.dt.day_name()

    return data, codes


def main():

    st.set_page_config(
        page_title="Madrid Mobility Dashboard",
        page_icon=":bar_chart:",
        layout="wide"
    )

    st.title("Madrid Mobility Dashboard")
    st.write("""
    This dashboard visualizes Uber movement data for Madrid neighborhoods in 2020.
    
    ### Features:
    - **Travel Time Analysis**: View average travel times between any two neighborhoods
    - **Day of Week Patterns**: Compare travel times across different days of the week
    - **Time Period Comparison**: Analyze how travel times vary by hour of the day
    - **Interactive Map**: Visualize the geographic distribution of travel times
             
    ### How to use: 
    - Use the sidebar to select source and destination neighborhoods to explore the data.
    - The dashboard will display the average travel time between the selected neighborhoods.
    - The map will show the geographic distribution of travel times between the selected neighborhoods.
    - The charts will display the average travel time by day of week and hour of day.
    """)
    
    st.markdown("---")
    
    data, codes = read_and_preprocess_data()
    sources = sorted(data.src_neigh_name.unique())
    destinations = sorted(data.dst_neigh_name.unique())
    
    source = st.sidebar.selectbox('Select the source', sources)
    destination = st.sidebar.selectbox('Select the destination', destinations)
    
    aux = data[(data.src_neigh_name == source) & (data.dst_neigh_name == destination)]
    aux = aux.sort_values("date")
    
    # CHART 1
    fig1 = px.line(
        aux, x="date", y="mean_travel_time", text="day_period",
        error_y="standard_deviation_travel_time",
        title="Travel time from {} to {}".format(source, destination),
        template="none"
    )

    fig1.update_xaxes(title="Date")
    fig1.update_yaxes(title="Avg. travel time (seconds)")
    fig1.update_traces(mode="lines+markers", marker_size=10, line_width=3, error_y_color="gray", error_y_thickness=1, error_y_width=10)
    
    st.plotly_chart(fig1, use_container_width=True)

    
    #CHART 2
    aux2 = aux.groupby(["day_of_week_str","day_of_week", "day_period", "start_hour"])[["mean_travel_time"]].mean().reset_index()
    
    fig2 = px.bar(
        aux2.sort_values(["start_hour","day_of_week"]), x="day_of_week_str", y="mean_travel_time",
        color="day_period", barmode="group", opacity=0.7, color_discrete_sequence=px.colors.sequential.RdBu_r,
        category_orders={"day_of_week_str": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
        title="Avg. travel time from {} to {} by day of week".format(source, destination),
        template="none"
    )

    fig2.update_xaxes(title="Period of Day")
    fig2.update_yaxes(title="Avg. travel time (seconds)")
    fig2.update_layout(legend_title="Day Period")
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # CHART 3
    # Calculate average travel times from the source to all other neighborhoods
    travel_times = data[data.src_neigh_name == source].groupby('dst_neigh_name')['mean_travel_time'].mean()

    # Prepare map data
    aux = codes.copy()
    aux = aux.set_index('DISPLAY_NAME')

    # Create a travel time column with missing values for neighborhoods without data
    aux['travel_time'] = np.nan
    aux.loc[travel_times.index, 'travel_time'] = travel_times
    aux['has_data'] = ~aux['travel_time'].isna()
    aux['is_source'] = aux.index == source

    # Create figure for neighborhoods with data
    fig = px.choropleth(
        aux[aux['has_data'] & ~aux['is_source']],  # Exclude source from this trace
        geojson=aux[aux['has_data'] & ~aux['is_source']].geometry,
        locations=aux[aux['has_data'] & ~aux['is_source']].index,
        color='travel_time',
        color_continuous_scale='Reds',
        range_color=[travel_times.min(), travel_times.max()],
        labels={'travel_time': 'Travel Time (seconds)'},
        title=f"Average Travel Times from {source}",
        height=600
    )

    # Add neighborhoods with no data in light gray
    no_data_trace = px.choropleth(
        aux[~aux['has_data'] & ~aux['is_source']],
        geojson=aux[~aux['has_data'] & ~aux['is_source']].geometry,
        locations=aux[~aux['has_data'] & ~aux['is_source']].index,
        color_discrete_sequence=['#e0e0e0']  # Light gray
    ).data[0]

    # Add the source neighborhood in navy blue
    source_trace = px.choropleth(
        aux[aux['is_source']],
        geojson=aux[aux['is_source']].geometry,
        locations=aux[aux['is_source']].index,
        color_discrete_sequence=['#000080']  # Navy blue
    ).data[0]

    # Add all traces to the figure
    fig.add_trace(no_data_trace)
    fig.add_trace(source_trace)

    # Update the layout
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin={"r":0,"l":0,"b":0},
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    
    
if __name__ == "__main__":
    main()