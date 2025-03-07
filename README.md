# Uber Demo App
This project is a Streamlit application that shows the evolution of Uber pickups in New York City over time. The app displays three different charts: a line chart, a map, and a bar chart.

## Project Evolution: From Single-page to Multi-page Application

### 1. Multi-page Structure Implementation
To create a multi-page application, we followed these steps:
- Create a new `pages` directory in the root folder to organize different pages
- Create 3 different Python files inside `pages/` for the 3 charts we want to show in different pages
- Move the code for each chart to the corresponding Python file, importing necessary libraries and functions
- Create an `utils.py` file to store common functions the `read_and_preprocess_data()` function, which is common to all pages
- Remove all unnecessary code from the main `main.py` file
- Rename the chart pages using the following format: `1_📊_Chart1.py`, `2_🗺️_Chart2.py`, `3_📈_Chart3.py`
- Rename also the main page to `0_🏠_Home.py`

### 2. Implementing Streamlit Cache Mechanism
To improve performance and user experience, we implemented a caching strategy using `@cache_data`. This decorator caches the function output based on its input arguments, so that the function is not re-executed if the input arguments are the same. In our case, we used it in the `read_and_preprocess_data()` function.

#### Data Loading Optimization
```python
import streamlit as st

@st.cache_data
def read_and_preprocess_data():
    # Data loading logic
    pass
```

### 3. Deployment to Streamlit Cloud

#### Prerequisites
Create a `requirements.txt` file with all necessary dependencies. You can use the `pipreqs` library to generate this file automatically.
```bash
pip install pipreqs
pipreqs /path/to/project
```

#### Deployment Steps
1. Create a GitHub repository for the project
2. Push the code to the repository
3. Log into [Streamlit Cloud](https://share.streamlit.io/). You will need to associate your GitHub account with Streamlit.
5. Create a new App in the Streamlit Platform
6. Select the main file (`0_🏠_Home.py`) as the app's entry point
7. Deploy the application
