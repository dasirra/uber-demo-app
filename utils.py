import zipfile
import geopandas
import pandas as pd
import streamlit as st

@st.cache_data
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