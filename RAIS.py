import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_trend_data, load_visual_defects, load_shop_floor_defects, load_integrity_data, load_assembly_rejection

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
# 2. SIDEBAR - FILE UPLOAD
# ---------------------------------------------------------
st.sidebar.header("📁 Upload Data Files")
st.sidebar.markdown("Upload your Excel files to analyze:")

uploaded_production = st.sidebar.file_uploader(
    "1️⃣ YEARLY PRODUCTION COMMULATIVE",
    type=['xlsx', 'xls'],
    key="production"
)

uploaded_commulative = st.sidebar.file_uploader(
    "2️⃣ COMMULATIVE 2025-26",
    type=['xlsx', 'xls'],
    key="commulative"
)

uploaded_visual = st.sidebar.file_uploader(
    "3️⃣ Visual Inspection Report",
    type=['xlsx', 'xls'],
    key="visual"
)

uploaded_shopfloor = st.sidebar.file_uploader(
    "4️⃣ Shop Floor Rejection Report",
    type=['xlsx', 'xls'],
    key="shopfloor"
)

uploaded_integrity = st.sidebar.file_uploader(
    "5️⃣ Balloon & Valve Integrity Report",
    type=['xlsx', 'xls'],
    key="integrity"
)

uploaded_assembly = st.sidebar.file_uploader(
    "6️⃣ Assembly Rejection Report",
    type=['xlsx', 'xls'],
    key="assembly"
)

st.sidebar.divider()

# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("Dashboard Controls")
view_mode = st.sidebar.radio("Select View:", ["Executive Summary", "Commulative Summary", "Assembly Rejection", "Defect Deep Dive", "Process Integrity"])

# ---------------------------------------------------------
# 4. DATA LOADING (From Uploaded Files)
# ---------------------------------------------------------

# Load data from uploaded files
df_trend = load_trend_data(uploaded_production)
df_commulative = load_trend_data(uploaded_commulative)  # Same structure as production
df_visual = load_visual_defects(uploaded_visual)
df_shop = load_shop_floor_defects(uploaded_shopfloor)
df_integrity = load_integrity_data(uploaded_integrity)
df_assembly = load_assembly_rejection(uploaded_assembly)

# Check if data is loaded
has_production_data = len(df_trend) > 0 and df_trend['Production_Qty'].sum() > 0
has_commulative_data = len(df_commulative) > 0 and df_commulative['Production_Qty'].sum() > 0
has_visual_data = len(df_visual) > 0 and df_visual['Quantity'].sum() > 0
has_shop_data = len(df_shop) > 0 and df_shop['Quantity'].sum() > 0
has_integrity_data = len(df_integrity) > 0 and df_integrity['Quantity'].sum() > 0
has_assembly_data = len(df_assembly) > 0 and df_assembly['Total_Rej'].sum() > 0

# ---------------------------------------------------------
# 5. MAIN DASHBOARD VIEWS
# ---------------------------------------------------------

if view_mode == "Executive Summary":
    if not has_production_data:
        st.warning("⚠️ Please upload the **Production Data** file (YEARLY PRODUCTION COMMULATIVE) in the sidebar to view this section.")
    else:
        # --- KPI METRICS ---
        total_prod = df_trend['Production_Qty'].sum()
        avg_rej = df_trend['Rejection_Rate'].mean()
        peak_idx = df_trend['Rejection_Rate'].idxmax()
        peak_month = df_trend.loc[peak_idx]['Month'] if peak_idx is not None else "N/A"
        best_idx = df_trend['Rejection_Rate'].idxmin()
        best_month = df_trend.loc[best_idx]['Month'] if best_idx is not None else "N/A"
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Production (YTD)", f"{total_prod:,.0f} Units", delta="From uploaded data")
        col2.metric("Avg Rejection Rate", f"{avg_rej:.2f}%", delta_color="inverse")
        col3.metric("Peak Rejection Month", peak_month)
        col4.metric("Best Quality Month", best_month)

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
            yaxis2=dict(title='Rejection %', overlaying='y', side='right', range=[0, max(20, df_trend['Rejection_Rate'].max() + 5)]),
            legend=dict(x=0.1, y=1.1, orientation="h"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.info("💡 **Insight:** Chart shows correlation between production volume and quality metrics from your uploaded data.")

elif view_mode == "Commulative Summary":
    st.subheader("📊 Commulative 2025-26 Analysis")
    
    if not has_commulative_data:
        st.warning("⚠️ Please upload the **COMMULATIVE 2025-26** file in the sidebar to view this section.")
    else:
        # KPI Metrics
        total_prod = df_commulative['Production_Qty'].sum()
        avg_rej = df_commulative['Rejection_Rate'].mean()
        max_rej_idx = df_commulative['Rejection_Rate'].idxmax()
        peak_month = df_commulative.loc[max_rej_idx]['Month'] if max_rej_idx is not None else "N/A"
        min_rej_idx = df_commulative['Rejection_Rate'].idxmin()
        best_month = df_commulative.loc[min_rej_idx]['Month'] if min_rej_idx is not None else "N/A"
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Production", f"{total_prod:,.0f} Units")
        col2.metric("Avg Rejection Rate", f"{avg_rej:.2f}%")
        col3.metric("Peak Rejection Month", peak_month)
        col4.metric("Best Month", best_month)
        
        st.divider()
        
        # Trend Chart
        st.markdown("#### Monthly Production vs. Rejection Rate")
        
        fig_comm = go.Figure()
        fig_comm.add_trace(go.Bar(
            x=df_commulative['Month'],
            y=df_commulative['Production_Qty'],
            name='Production Quantity',
            marker_color='#9B59B6',
            opacity=0.6
        ))
        fig_comm.add_trace(go.Scatter(
            x=df_commulative['Month'],
            y=df_commulative['Rejection_Rate'],
            name='Rejection Rate (%)',
            yaxis='y2',
            line=dict(color='#E67E22', width=4, shape='spline'),
            mode='lines+markers'
        ))
        
        fig_comm.update_layout(
            title="Commulative Production & Rejection Trend",
            yaxis=dict(title='Production Units'),
            yaxis2=dict(title='Rejection %', overlaying='y', side='right', range=[0, max(20, df_commulative['Rejection_Rate'].max() + 5)]),
            legend=dict(x=0.1, y=1.1, orientation="h"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_comm, use_container_width=True)
        
        # Raw data
        st.markdown("#### Monthly Data Table")
        st.dataframe(df_commulative)

elif view_mode == "Assembly Rejection":
    st.subheader("📋 Assembly Section Rejection Analysis")
    
    if not has_assembly_data:
        st.warning("⚠️ Please upload the **Assembly Rejection Report** file in the sidebar to view this section.")
    else:
        # KPI Metrics
        total_visual = df_assembly['Visual_Rej'].sum()
        total_balloon = df_assembly['Balloon_Rej'].sum()
        total_valve = df_assembly['Valve_Rej'].sum()
        total_overall = df_assembly['Total_Rej'].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Visual Rejections", f"{total_visual:,.0f}")
        col2.metric("Balloon Rejections", f"{total_balloon:,.0f}")
        col3.metric("Valve Rejections", f"{total_valve:,.0f}")
        col4.metric("Total Rejections", f"{total_overall:,.0f}")
        
        st.divider()
        
        # Stacked bar chart showing rejection breakdown by month
        st.markdown("#### Monthly Rejection Breakdown by Type")
        
        fig_assembly = go.Figure()
        fig_assembly.add_trace(go.Bar(
            x=df_assembly['Month'],
            y=df_assembly['Visual_Rej'],
            name='Visual Rejections',
            marker_color='#3498DB'
        ))
        fig_assembly.add_trace(go.Bar(
            x=df_assembly['Month'],
            y=df_assembly['Balloon_Rej'],
            name='Balloon Rejections',
            marker_color='#E74C3C'
        ))
        fig_assembly.add_trace(go.Bar(
            x=df_assembly['Month'],
            y=df_assembly['Valve_Rej'],
            name='Valve Rejections',
            marker_color='#2ECC71'
        ))
        
        fig_assembly.update_layout(
            barmode='stack',
            title="Monthly Assembly Section Rejections",
            xaxis_title="Month",
            yaxis_title="Rejection Count",
            legend=dict(x=0.1, y=1.1, orientation="h"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_assembly, use_container_width=True)
        
        # Raw data table
        st.markdown("#### Monthly Summary Data")
        st.dataframe(df_assembly)

elif view_mode == "Defect Deep Dive":
    st.subheader("🔍 Root Cause Analysis: Visual & Shop Floor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top Visual Inspection Defects")
        if not has_visual_data:
            st.warning("⚠️ Upload **Visual Inspection Report** to view this chart.")
        else:
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
            st.caption(f"Total Visual Defects: {df_visual['Quantity'].sum():,.0f}")

    with col2:
        st.markdown("#### Shop Floor (Dipping) Defects")
        if not has_shop_data:
            st.warning("⚠️ Upload **Shop Floor Rejection Report** to view this chart.")
        else:
            fig_shop = px.pie(
                df_shop, 
                values='Quantity', 
                names='Defect', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            st.plotly_chart(fig_shop, use_container_width=True)
            st.caption(f"Total Shop Floor Defects: {df_shop['Quantity'].sum():,.0f}")

elif view_mode == "Process Integrity":
    st.subheader("🛡️ Functional Integrity Analysis (Balloon & Valve)")
    
    if not has_integrity_data:
        st.warning("⚠️ Please upload the **Balloon & Valve Integrity Report** file in the sidebar to view this section.")
    else:
        col1, col2 = st.columns(2)
        
        # Valve Integrity Chart
        with col1:
            st.markdown("#### Valve Failure Modes")
            df_valve = df_integrity[df_integrity['Test_Type'] == 'Valve Integrity']
            if len(df_valve) > 0:
                fig_valve = px.bar(
                    df_valve, x='Defect_Type', y='Quantity', 
                    color='Defect_Type', 
                    title=f"Total Rejections: {df_valve['Quantity'].sum():,.0f}"
                )
                st.plotly_chart(fig_valve, use_container_width=True)
            else:
                st.info("No valve integrity data found.")

        # Balloon Integrity Chart
        with col2:
            st.markdown("#### Balloon Failure Modes")
            df_balloon = df_integrity[df_integrity['Test_Type'] == 'Balloon Integrity']
            if len(df_balloon) > 0:
                fig_balloon = px.pie(
                    df_balloon, values='Quantity', names='Defect_Type',
                    title=f"Total Rejections: {df_balloon['Quantity'].sum():,.0f}",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                st.plotly_chart(fig_balloon, use_container_width=True)
            else:
                st.info("No balloon integrity data found.")

# ---------------------------------------------------------
# 6. FOOTER / RAW DATA
# ---------------------------------------------------------
with st.expander("📂 View Raw Source Data Tables"):
    if has_production_data:
        st.write("**1. Yearly Trend Data**")
        st.dataframe(df_trend)
    
    if has_visual_data:
        st.write("**2. Visual Defect Counts**")
        st.dataframe(df_visual)
    
    if has_shop_data:
        st.write("**3. Shop Floor Defect Counts**")
        st.dataframe(df_shop)
    
    if has_integrity_data:
        st.write("**4. Integrity Data**")
        st.dataframe(df_integrity)
    
    if not any([has_production_data, has_visual_data, has_shop_data, has_integrity_data]):
        st.info("Upload Excel files in the sidebar to see data here.")