import streamlit as st

import numpy as np
import plotly.express as px
from utils import read_and_preprocess_data

data, codes = read_and_preprocess_data()
sources = sorted(data.src_neigh_name.unique())
# destinations = sorted(data.dst_neigh_name.unique())

source = st.sidebar.selectbox('Select the source', sources)
# destination = st.sidebar.selectbox('Select the destination', destinations)

aux = data[(data.src_neigh_name == source)]
aux = aux.sort_values("date")

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