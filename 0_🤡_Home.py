import streamlit as st

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
    
    
if __name__ == "__main__":
    main()