import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Title & Config
# -------------------------------
st.set_page_config(page_title="Nautilus Maritime Dashboard", layout="wide")
st.title("🌊 Nautilus Maritime Incidents Dashboard")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("maritime_incidentsrr.csv")
    
    # Normalize column names (avoid spaces/typos)
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    
    # Fix date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    
    # Convert Cargo_Loss Yes/No → 1/0
    df["Cargo_Loss_Flag"] = df["Cargo_Loss"].map({"Yes": 1, "No": 0})
    
    return df

data = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔍 Filters")
years = st.sidebar.multiselect("Select Year(s):", sorted(data["Year"].dropna().unique()), default=None)
countries = st.sidebar.multiselect("Select Country:", sorted(data["Country"].dropna().unique()), default=None)
vessels = st.sidebar.multiselect("Select Vessel Type:", sorted(data["Vessel_Type"].dropna().unique()), default=None)
incidents = st.sidebar.multiselect("Select Incident Type:", sorted(data["Incident_Type"].dropna().unique()), default=None)

# Apply filters
filtered = data.copy()
if years: filtered = filtered[filtered["Year"].isin(years)]
if countries: filtered = filtered[filtered["Country"].isin(countries)]
if vessels: filtered = filtered[filtered["Vessel_Type"].isin(vessels)]
if incidents: filtered = filtered[filtered["Incident_Type"].isin(incidents)]

st.sidebar.write(f"📊 Showing {len(filtered)} records")

# -------------------------------
# KPI Metrics
# -------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Incidents", len(filtered))
c2.metric("Total Casualties", int(filtered["Casualties"].sum()))   # ✅ fixed spelling
c3.metric("Total Cargo Loss", int(filtered["Cargo_Loss_Flag"].sum()))

# -------------------------------
# Visualizations
# -------------------------------

# 1. Incidents Over Time (Monthly)
st.subheader("📈 Incidents Over Time (Monthly)")
monthly_counts = filtered.groupby(filtered["Date"].dt.to_period("M")).size().reset_index(name="Count")
monthly_counts["Date"] = monthly_counts["Date"].astype(str)
fig1 = px.line(monthly_counts, x="Date", y="Count", markers=True, title="Monthly Trend of Incidents")
st.plotly_chart(fig1, use_container_width=True)

# 2. Top Countries
st.subheader("🌍 Top Countries by Incidents")
country_counts = filtered["Country"].value_counts().nlargest(10).reset_index()
country_counts.columns = ["Country", "Incidents"]
fig2 = px.treemap(country_counts, path=["Country"], values="Incidents", title="Incidents by Country")
st.plotly_chart(fig2, use_container_width=True)

# 3. Incident Type Distribution
st.subheader("⚠️ Incident Type Distribution")
fig3 = px.sunburst(filtered, path=["Incident_Type", "Vessel_Type"], title="Incident Types & Vessel Types")
st.plotly_chart(fig3, use_container_width=True)

# 4. Map of Incidents
st.subheader("🗺️ Incident Locations")
fig4 = px.scatter_mapbox(
    filtered,
    lat="Latitude",
    lon="Longitude",
    hover_name="Incident_Type",
    hover_data=["Country", "Vessel_Type", "Casualties", "Cargo_Loss"],  # ✅ fixed typo
    color="Incident_Type",
    size_max=12,
    zoom=2,
    height=500
)
fig4.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# Show Raw Data
# -------------------------------
st.subheader("📄 Raw Data Preview")
st.dataframe(filtered.head(50))

