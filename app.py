import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# --- Page Config ---
st.set_page_config(
    page_title="Water Usage Dashboard",
    layout="wide",
    page_icon="💧"
)

# --- Custom CSS for Navy Theme and Chatbot Icon ---
st.markdown("""
    <style>
        /* Navy Blue Theme */
        .main, .css-18e3th9, .css-1d391kg {
            background-color: #f7f9fc !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #002B5B;
        }
        .st-bb, .st-cg, .st-df, .st-e3 {
            color: #002B5B;
        }

        /* Floating Chatbot Icon */
        #chatbot-button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background-color: #002B5B;
            color: white;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            text-align: center;
            font-size: 30px;
            line-height: 60px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            z-index: 100;
        }

        /* Top Bar Icons */
        #top-icons {
            position: fixed;
            top: 15px;
            right: 25px;
            z-index: 100;
        }
        #top-icons i {
            font-size: 24px;
            color: #002B5B;
            margin-left: 15px;
            cursor: pointer;
        }
    </style>

    <div id="chatbot-button">💬</div>

    <div id="top-icons">
        <i class="fas fa-user-circle"></i>
        <i class="fas fa-cog"></i>
    </div>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)

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

# --- Title ---
st.title("💧 AquaVisionX - Water Usage Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])

if len(date_range) != 2:
    st.error("Please select a valid date range.")
    st.stop()

start_date, end_date = date_range

all_categories = df['Category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Select Categories", options=all_categories, default=all_categories
)

if not selected_categories:
    st.warning("No categories selected. Showing default: Boys.")
    selected_categories = ["Boys"]

# --- Filter Data ---
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

# --- Line Chart ---
st.markdown("### 📈 Water Usage Over Time")
if not filtered_df.empty:
    fig1 = px.line(
        filtered_df,
        x='Date',
        y='Water Usage (Litres)',
        color='Category',
        markers=True,
        template='plotly_white',
        title='Daily Water Usage by Category'
    )
    fig1.update_layout(
        xaxis_title="Date",
        yaxis_title="Litres Used",
        legend_title="Category",
        hovermode="x unified",
        font=dict(size=14),
        margin=dict(l=30, r=30, t=50, b=30),
        title_font=dict(color="#002B5B")
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.write("No data to display.")

# --- Pie Chart ---
st.markdown("### 🥧 Usage Distribution by Category")
if not filtered_df.empty:
    category_usage = filtered_df.groupby('Category')['Water Usage (Litres)'].sum().reset_index()
    
    pie_chart = px.pie(
        category_usage,
        names='Category',
        values='Water Usage (Litres)',
        hole=0.45,
        template='plotly_white',
        title='Water Usage Breakdown by Category'
    )
    pie_chart.update_traces(
        textinfo='percent+label',
        pull=[0.05] * len(category_usage)
    )
    pie_chart.update_layout(
        font=dict(size=14),
        margin=dict(l=30, r=30, t=50, b=30),
        title_font=dict(color="#002B5B")
    )
    st.plotly_chart(pie_chart, use_container_width=True)

    # --- Bar Chart ---
    bar_chart = px.bar(
        category_usage,
        x='Category',
        y='Water Usage (Litres)',
        color='Category',
        text_auto=True,
        template='plotly_white',
        title='Total Water Usage by Category'
    )
    bar_chart.update_layout(
        font=dict(size=14),
        margin=dict(l=30, r=30, t=50, b=30),
        title_font=dict(color="#002B5B"),
        showlegend=False
    )
    st.plotly_chart(bar_chart, use_container_width=True)
else:
    st.write("No category usage data.")

# --- Leaderboard ---
st.markdown("### 🏆 Leaderboard (Gamification Idea)")
if not filtered_df.empty:
    leaderboard = filtered_df.groupby('Category')['Water Usage (Litres)'].sum().reset_index()
    leaderboard = leaderboard.sort_values(by='Water Usage (Litres)', ascending=True)
    st.dataframe(leaderboard.reset_index(drop=True), use_container_width=True)
else:
    st.write("Leaderboard unavailable due to lack of data.")
