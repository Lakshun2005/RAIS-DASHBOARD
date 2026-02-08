import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_trend_data, load_visual_defects, load_shop_floor_defects, load_integrity_data

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Production Quality 2025-26",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏭 Manufacturing Quality Assurance Dashboard (2025-26)")
st.markdown("### Interactive Analytics for Assembly, Inspection, & Shop Floor")

# ---------------------------------------------------------
# 2. DATA LOADING (From Excel Files via data_loader)
# ---------------------------------------------------------

# Load data from Excel files
df_trend = load_trend_data()
df_visual = load_visual_defects()
df_shop = load_shop_floor_defects()
df_integrity = load_integrity_data()


# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("Dashboard Controls")
view_mode = st.sidebar.radio("Select View:", ["Executive Summary", "Defect Deep Dive", "Process Integrity"])

# ---------------------------------------------------------
# 4. MAIN DASHBOARD VIEWS
# ---------------------------------------------------------

if view_mode == "Executive Summary":
    # --- KPI METRICS ---
    total_prod = df_trend['Production_Qty'].sum()
    avg_rej = df_trend['Rejection_Rate'].mean()
    peak_month = df_trend.loc[df_trend['Rejection_Rate'].idxmax()]['Month']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Production (YTD)", f"{total_prod:,.0f} Units", delta="Apr-Dec 2025")
    col2.metric("Avg Rejection Rate", f"{avg_rej:.2f}%", delta_color="inverse", delta="+2.5% vs Target")
    col3.metric("Peak Rejection Month", peak_month, "16.04% Rate")
    col4.metric("Best Quality Month", "Aug-25", "5.80% Rate")

    st.divider()

    # --- TREND CHART (Dual Axis) ---
    st.subheader("📈 Monthly Production vs. Rejection Rate")
    
    fig_trend = go.Figure()
    # Bar Chart for Production
    fig_trend.add_trace(go.Bar(
        x=df_trend['Month'],
        y=df_trend['Production_Qty'],
        name='Production Quantity',
        marker_color='#2E86C1',
        opacity=0.6
    ))
    # Line Chart for Rejection Rate
    fig_trend.add_trace(go.Scatter(
        x=df_trend['Month'],
        y=df_trend['Rejection_Rate'],
        name='Rejection Rate (%)',
        yaxis='y2',
        line=dict(color='#E74C3C', width=4, shape='spline'),
        mode='lines+markers'
    ))
    
    fig_trend.update_layout(
        title="Correlation: Production Volume vs. Quality",
        yaxis=dict(title='Production Units'),
        yaxis2=dict(title='Rejection %', overlaying='y', side='right', range=[0, 20]),
        legend=dict(x=0.1, y=1.1, orientation="h"),
        hovermode="x unified"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.info("💡 **Insight:** December 2025 saw the highest production (381k) but also the highest rejection rate (16.04%), indicating a trade-off between speed and quality.")

elif view_mode == "Defect Deep Dive":
    st.subheader("🔍 Root Cause Analysis: Visual & Shop Floor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top Visual Inspection Defects")
        fig_visual = px.bar(
            df_visual, 
            x='Quantity', 
            y='Defect', 
            orientation='h',
            text='Quantity',
            color='Quantity',
            color_continuous_scale='Reds'
        )
        fig_visual.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_visual, use_container_width=True)
        st.caption("Primary Issue: Black Marks & Pin Holes account for ~50% of visual rejects.")

    with col2:
        st.markdown("#### Shop Floor (Dipping) Defects")
        fig_shop = px.pie(
            df_shop, 
            values='Quantity', 
            names='Defect', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_shop, use_container_width=True)
        st.caption("Process Issue: 'Others', 'Surface Defects', and 'Coagulum' are widely distributed.")

elif view_mode == "Process Integrity":
    st.subheader("🛡️ Functional Integrity Analysis (Balloon & Valve)")
    
    col1, col2 = st.columns(2)
    
    # Valve Integrity Chart
    with col1:
        st.markdown("#### Valve Failure Modes")
        df_valve = df_integrity[df_integrity['Test_Type'] == 'Valve Integrity']
        fig_valve = px.bar(
            df_valve, x='Defect_Type', y='Quantity', 
            color='Defect_Type', 
            title=f"Total Rejections: {df_valve['Quantity'].sum():,}"
        )
        st.plotly_chart(fig_valve, use_container_width=True)
        st.error("Critical: 'Thin Spot' causes nearly 50% of valve failures.")

    # Balloon Integrity Chart
    with col2:
        st.markdown("#### Balloon Failure Modes")
        df_balloon = df_integrity[df_integrity['Test_Type'] == 'Balloon Integrity']
        fig_balloon = px.pie(
            df_balloon, values='Quantity', names='Defect_Type',
            title=f"Total Rejections: {df_balloon['Quantity'].sum():,}",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig_balloon, use_container_width=True)
        st.warning("Critical: 'Struck Balloon' is the dominant failure mode (61%).")

# ---------------------------------------------------------
# 5. FOOTER / RAW DATA
# ---------------------------------------------------------
with st.expander("📂 View Raw Source Data Tables"):
    st.write(" **1. Yearly Trend Data**")
    st.dataframe(df_trend)
    st.write(" **2. Visual Defect Counts**")
    st.dataframe(df_visual)