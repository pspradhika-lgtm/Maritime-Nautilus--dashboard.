import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# -------------------------------
# Title & Config
# -------------------------------
st.set_page_config(page_title="🌊 Nautilus Advanced Dashboard", layout="wide")
st.title("🚢 Nautilus Maritime Incidents – Advanced Interactive Dashboard")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("maritime_incidentsrr.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["Cargo_Loss_Flag"] = df["Cargo_Loss"].map({"Yes": 1, "No": 0})
    return df

data = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔍 Filters")
years = st.sidebar.multiselect("Select Year(s):", sorted(data["Year"].dropna().unique()))
countries = st.sidebar.multiselect("Select Country:", sorted(data["Country"].dropna().unique()))
vessels = st.sidebar.multiselect("Select Vessel Type:", sorted(data["Vessel_Type"].dropna().unique()))
incidents = st.sidebar.multiselect("Select Incident Type:", sorted(data["Incident_Type"].dropna().unique()))

filtered = data.copy()
if years: filtered = filtered[filtered["Year"].isin(years)]
if countries: filtered = filtered[filtered["Country"].isin(countries)]
if vessels: filtered = filtered[filtered["Vessel_Type"].isin(vessels)]
if incidents: filtered = filtered[filtered["Incident_Type"].isin(incidents)]

st.sidebar.success(f"📊 Showing {len(filtered)} records")

# -------------------------------
# KPI Metrics
# -------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Incidents", len(filtered))
c2.metric("Total Casualties", int(filtered["Casualties"].fillna(0).sum()))
c3.metric("Cargo Loss Events", int(filtered["Cargo_Loss_Flag"].fillna(0).sum()))
c4.metric("Countries Involved", filtered["Country"].nunique())

# -------------------------------
# Tabs for Advanced Visuals
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Calendar Heatmap", "🎥 Animated Timeline", "🔗 Incident-Vessel Sankey",
    "🕸 Radar Chart"])

# 1. Calendar Heatmap
with tab1:
    st.subheader("📅 Incidents by Month & Year")
    if not filtered.empty:
        pivot = filtered.pivot_table(index="Month", columns="Year", values="Incident_Type", aggfunc="count", fill_value=0)
        fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale="RdYlBu_r",
                        labels=dict(x="Year", y="Month", color="Incidents"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for selected filters.")

# 2. Animated Timeline
with tab2:
    st.subheader("🎥 Animated Incidents Over Time")
    if not filtered.empty:
        fig = px.scatter(
            filtered,
            x="Longitude", y="Latitude",
            animation_frame="Year", animation_group="Incident_Type",
            size="Casualties", color="Incident_Type",
            hover_name="Country",
            title="Incidents Progression Over Years",
            size_max=30, projection="natural earth"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for selected filters.")

# 3. Sankey Diagram
with tab3:
    st.subheader("🔗 Incident Types vs Vessel Types")
    if not filtered.empty:
        source_labels = list(filtered["Incident_Type"].unique()) + list(filtered["Vessel_Type"].unique())
        source_dict = {k: v for v, k in enumerate(source_labels)}
        
        sankey_data = filtered.groupby(["Incident_Type", "Vessel_Type"]).size().reset_index(name="count")
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20, thickness=20,
                line=dict(color="black", width=0.5),
                label=source_labels
            ),
            link=dict(
                source=sankey_data["Incident_Type"].map(source_dict),
                target=sankey_data["Vessel_Type"].map(source_dict),
                value=sankey_data["count"]
            )
        )])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for selected filters.")

# 4. Radar Chart
with tab4:
    st.subheader("🕸 Country Comparison (Radar Chart)")
    if not filtered.empty:
        top_countries = filtered["Country"].value_counts().nlargest(5).index
        radar_data = filtered[filtered["Country"].isin(top_countries)].groupby("Country").agg({
            "Casualties": "sum",
            "Cargo_Loss_Flag": "sum",
            "Incident_Type": "count"
        }).reset_index()
        
        categories = ["Casualties", "Cargo_Loss_Flag", "Incident_Type"]
        fig = go.Figure()
        for _, row in radar_data.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=row[categories].values,
                theta=categories,
                fill='toself',
                name=row["Country"]
            ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for selected filters.")




