import streamlit as st
import pandas as pd
import plotly.express as px
st.title("COVID-19 Data Visualization Dashboard")

st.markdown("""
This dashboard explores global COVID-19 trends, vaccination progress,
and their relationship with deaths across countries.
""")
import streamlit as st
import pandas as pd
import requests
from io import StringIO

@st.cache_data(ttl=24*60*60)
def load_data():
    url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text))
    df["date"] = pd.to_datetime(df["date"])
    return df
    
df = load_data()
countries = df['location'].unique()
selected_country = st.sidebar.selectbox(
    "Select a Country",
    countries,
    index=list(countries).index("India")
)
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['date'].min(), df['date'].max()]
)
filtered_df = df[
    (df['location'] == selected_country) &
    (df['date'] >= pd.to_datetime(date_range[0])) &
    (df['date'] <= pd.to_datetime(date_range[1]))
]
latest = filtered_df.sort_values('date').iloc[-1]

col1, col2, col3 = st.columns(3)

def fmt_int(x):
    return f"{int(x):,}" if pd.notna(x) else "N/A"

def fmt_float1(x):
    return f"{float(x):.1f}" if pd.notna(x) else "N/A"

col1.metric("Total Cases", fmt_int(latest.get("total_cases")))
col2.metric("Total Deaths", fmt_int(latest.get("total_deaths")))
col3.metric("Fully Vaccinated (%)", fmt_float1(latest.get("people_fully_vaccinated_per_hundred")))

fig = px.area(
    filtered_df,
    x="date",
    y="total_cases",
    title="Total COVID-19 Cases Over Time"
)

st.plotly_chart(fig, use_container_width=True)
latest_all = df.sort_values('date').groupby('location').last().reset_index()
top10 = latest_all.sort_values(
    'total_deaths_per_million',
    ascending=False
).head(10)

fig2 = px.bar(
    top10,
    x="location",
    y="total_deaths_per_million",
    title="Top 10 Countries by Deaths per Million"
)

st.plotly_chart(fig2, use_container_width=True)
scatter_df = latest_all[
    ['people_fully_vaccinated_per_hundred', 'total_deaths_per_million']
].dropna()

fig3 = px.scatter(
    scatter_df,
    x='people_fully_vaccinated_per_hundred',
    y='total_deaths_per_million',
    title="Vaccination Rate vs Deaths per Million"
)

st.plotly_chart(fig3, use_container_width=True)
st.subheader("Filtered Data Preview")
st.dataframe(filtered_df.head(50))



