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