import streamlit as st

import plotly.express as px

from utils import read_and_preprocess_data


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