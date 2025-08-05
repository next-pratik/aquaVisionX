import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# --- Generate Sample Data ---
@st.cache_data
def generate_data():
    dates = pd.date_range(start=datetime.today() - timedelta(days=30), periods=31)
    categories = ['Boys', 'Girls', 'Staff']

    data = []
    for date in dates:
        for cat in categories:
            usage = np.random.randint(50, 200)
            data.append({'Date': date, 'Category': cat, 'Water Usage (Litres)': usage})

    return pd.DataFrame(data)

df = generate_data()

# --- Streamlit UI ---
st.set_page_config(page_title="Water Usage Dashboard", layout="wide")

st.title("💧 AquaVisionX")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])

# Ensure valid date range
if len(date_range) != 2:
    st.error("Please select a valid date range.")
    st.stop()

start_date, end_date = date_range

# Category filter with fallback
all_categories = df['Category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Select Categories", options=all_categories, default=all_categories
)

if not selected_categories:
    st.warning("No categories selected. Showing default: Boys.")
    selected_categories = ["Boys"]

# --- Filter data ---
filtered_df = df[
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date)) &
    (df['Category'].isin(selected_categories))
]

# --- KPI Metrics ---
st.markdown("### 🔢 Key Metrics")

if filtered_df.empty:
    st.info("No data available for the selected filters.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Water Used", "0 Litres")
    col2.metric("Average Daily Usage", "0 Litres")
    col3.metric("Peak Usage Day", "N/A")
else:
    total_usage = filtered_df['Water Usage (Litres)'].sum()
    avg_daily = filtered_df.groupby('Date')['Water Usage (Litres)'].sum().mean()
    peak_day = filtered_df.groupby('Date')['Water Usage (Litres)'].sum().idxmax()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Water Used", f"{total_usage:.0f} Litres")
    col2.metric("Average Daily Usage", f"{avg_daily:.0f} Litres")
    col3.metric("Peak Usage Day", peak_day.strftime('%Y-%m-%d'))

# --- Charts ---
st.markdown("### 📈 Water Usage Over Time")
if not filtered_df.empty:
    fig1 = px.line(filtered_df, x='Date', y='Water Usage (Litres)', color='Category', markers=True)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.write("No data to display.")

st.markdown("### 📊 Usage by Category")
if not filtered_df.empty:
    category_usage = filtered_df.groupby('Category')['Water Usage (Litres)'].sum().reset_index()
    fig2 = px.bar(category_usage, x='Category', y='Water Usage (Litres)', color='Category')
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.write("No category usage data.")

# --- Leaderboard ---
st.markdown("### 🏆 Leaderboard (Gamification Idea)")
if not filtered_df.empty:
    leaderboard = filtered_df.groupby('Category')['Water Usage (Litres)'].sum().reset_index()
    leaderboard = leaderboard.sort_values(by='Water Usage (Litres)', ascending=True)
    st.dataframe(leaderboard.reset_index(drop=True))
else:
    st.write("Leaderboard unavailable due to lack of data.")
