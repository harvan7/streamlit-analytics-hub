
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="DISH Network - Data Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .header-title {
        color: #1f77b4;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📡 DISH Network - Data Intelligence Hub")

# --- Sidebar Navigation & Filters ---
st.sidebar.title("🔧 Navigation & Filters")
page = st.sidebar.selectbox("📊 Choose Dashboard:", [
    "Dashboard 1: Financial & Health Insights",
    "Dashboard 2: Viewer Engagement",
    "Dashboard 3: Network Operations",
    "Executive Summary"
])

# Add refresh button
if st.sidebar.button("🔄 Refresh Data", help="Clear cache and reload fresh data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# --- Data Loading with Caching ---
def get_file_mod_time(file_path):
    """Get file modification time for cache busting"""
    if os.path.exists(file_path):
        return os.path.getmtime(file_path)
    return 0

@st.cache_data(ttl=300)  # Cache for 5 minutes, then refresh
def load_data(file_path):
    """Loads a CSV file into a pandas DataFrame."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file {file_path} was not found. Please run the data processing script first.")
        return None

# Helper function to create metric cards
def create_metric_card(col, label, value, delta=None, delta_color="normal"):
    """Creates a styled metric card"""
    if delta is not None:
        col.metric(label, value, delta=delta, delta_color=delta_color)
    else:
        col.metric(label, value)

# --- Page 1: Financial & Health Insights ---
if page == "Dashboard 1: Financial & Health Insights":
    st.markdown("<div class='header-title'>💰 Financial & Customer Health Insights</div>", unsafe_allow_html=True)
    
    billing_df = load_data('data/gold_layer/gold_billing_segmentation.csv')

    if billing_df is not None:
        # --- Sidebar Filters ---
        st.sidebar.subheader("Filter Options")
        all_regions = list(billing_df['Region'].unique())
        all_segments = list(billing_df['Customer_Segment'].unique()) if 'Customer_Segment' in billing_df.columns else []
        
        selected_regions = st.sidebar.multiselect("Select Regions:", 
                                                   all_regions)
        selected_segments = st.sidebar.multiselect("Customer Segments:",
                                                    all_segments)
        
        # Filter data
        filtered_df = billing_df.copy()
        if selected_regions:
            filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
        
        if selected_segments:
            filtered_df = filtered_df[filtered_df['Customer_Segment'].isin(selected_segments)]

        # --- Key Performance Indicators ---
        st.subheader("📈 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_revenue = filtered_df['Monthly_Bill'].sum()
        annual_revenue = total_revenue * 12
        avg_bill = filtered_df['Monthly_Bill'].mean()
        total_customers = len(filtered_df)
        
        create_metric_card(col1, "Total Monthly Revenue", f"${total_revenue:,.0f}")
        create_metric_card(col2, "Annual Revenue (Projected)", f"${annual_revenue:,.0f}")
        create_metric_card(col3, "Active Customers", f"{total_customers:,}")
        create_metric_card(col4, "Avg Monthly Bill", f"${avg_bill:,.2f}")

        # --- Additional KPIs ---
        col1, col2, col3, col4 = st.columns(4)
        
        avg_health_score = filtered_df['Service_Health_Score'].mean() if 'Service_Health_Score' in filtered_df.columns else 0
        payment_healthy = (filtered_df['Payment_Status'] == 'Paid').sum() if 'Payment_Status' in filtered_df.columns else 0
        churn_risk_high = (filtered_df['Calculated_Churn_Risk'] == 'High').sum() if 'Calculated_Churn_Risk' in filtered_df.columns else 0
        ltv_mean = filtered_df['Customer_Lifetime_Value'].mean() if 'Customer_Lifetime_Value' in filtered_df.columns else 0
        
        create_metric_card(col1, "Avg Health Score (0-100)", f"{avg_health_score:.1f}")
        create_metric_card(col2, "Customers in Good Standing", f"{payment_healthy:,}")
        create_metric_card(col3, "High Churn Risk Count", f"{churn_risk_high:,}")
        create_metric_card(col4, "Avg Customer LTV", f"${ltv_mean:,.0f}")

        # --- Row 1: Revenue Analysis ---
        st.subheader("💵 Revenue Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Revenue by Region
            revenue_by_region = filtered_df.groupby('Region').agg({
                'Monthly_Bill': 'sum',
                'Customer_ID': 'count'
            }).reset_index()
            revenue_by_region.columns = ['Region', 'Total_Revenue', 'Customer_Count']
            
            fig_region = px.bar(revenue_by_region, x='Region', y='Total_Revenue',
                               hover_data=['Customer_Count'],
                               title='Monthly Revenue by Region',
                               color='Total_Revenue',
                               color_continuous_scale='Viridis')
            st.plotly_chart(fig_region, use_container_width=True)

        with col2:
            # Bill Category Distribution
            bill_dist = filtered_df['Bill_Category'].value_counts().reset_index()
            bill_dist.columns = ['Bill_Category', 'Count']
            revenue_by_cat = filtered_df.groupby('Bill_Category')['Monthly_Bill'].sum().reset_index()
            
            fig_cat = px.pie(bill_dist, names='Bill_Category', values='Count',
                            title='Customer Distribution by Bill Category',
                            color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_cat, use_container_width=True)

        # --- Row 2: Health & Risk Analysis ---
        st.subheader("🏥 Customer Health & Risk Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Service Health Score Distribution
            if 'Service_Health_Score' in filtered_df.columns:
                fig_health = px.histogram(filtered_df, x='Service_Health_Score',
                                         nbins=20, title='Service Health Score Distribution',
                                         color_discrete_sequence=['#636EFA'])
                fig_health.add_vline(x=filtered_df['Service_Health_Score'].mean(),
                                    line_dash="dash", line_color="red",
                                    annotation_text=f"Mean: {filtered_df['Service_Health_Score'].mean():.1f}")
                st.plotly_chart(fig_health, use_container_width=True)
            else:
                st.info("Service Health Score data not available")

        with col2:
            # Churn Risk Distribution
            if 'Calculated_Churn_Risk' in filtered_df.columns:
                churn_dist = filtered_df['Calculated_Churn_Risk'].value_counts().reset_index()
                churn_dist.columns = ['Churn_Risk', 'Count']
                
                fig_churn = px.pie(churn_dist, names='Churn_Risk', values='Count',
                                  title='Customer Churn Risk Distribution',
                                  color_discrete_map={'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'})
                st.plotly_chart(fig_churn, use_container_width=True)
            else:
                st.info("Churn Risk data not available")

        # --- Row 3: Payment & Contract Analysis ---
        st.subheader("📋 Payment & Contract Status")
        col1, col2 = st.columns(2)

        with col1:
            # Payment Status
            if 'Payment_Status' in filtered_df.columns:
                payment_dist = filtered_df['Payment_Status'].value_counts().reset_index()
                payment_dist.columns = ['Payment_Status', 'Count']
                
                fig_payment = px.bar(payment_dist, x='Payment_Status', y='Count',
                                    title='Customer Payment Status',
                                    color='Payment_Status',
                                    color_discrete_map={
                                        'Paid': '#2ecc71',
                                        'Pending': '#f39c12',
                                        'Overdue': '#e74c3c',
                                        'Disputed': '#9b59b6'
                                    })
                st.plotly_chart(fig_payment, use_container_width=True)

        with col2:
            # Contract Renewal Risk
            if 'Contract_Renewal_Risk' in filtered_df.columns:
                contract_dist = filtered_df['Contract_Renewal_Risk'].value_counts().reset_index()
                contract_dist.columns = ['Contract_Risk', 'Count']
                
                fig_contract = px.pie(contract_dist, names='Contract_Risk', values='Count',
                                     title='Contract Renewal Risk Status',
                                     color_discrete_map={
                                         'Stable': '#2ecc71',
                                         'At Risk': '#f39c12',
                                         'Expiring Soon': '#e74c3c'
                                     })
                st.plotly_chart(fig_contract, use_container_width=True)

        # --- Row 4: Engagement Metrics ---
        st.subheader("🎯 Customer Engagement Metrics")
        col1, col2 = st.columns(2)

        with col1:
            # Loyalty Index vs LTV Index
            if 'Loyalty_Index' in filtered_df.columns and 'LTV_Index' in filtered_df.columns:
                fig_scatter = px.scatter(filtered_df, x='Loyalty_Index', y='LTV_Index',
                                        size='Monthly_Bill', color='Service_Health_Score',
                                        hover_data=['Customer_ID', 'Monthly_Bill'],
                                        title='Loyalty Index vs Lifetime Value Index',
                                        color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            # Device Adoption Score
            if 'Device_Adoption_Score' in filtered_df.columns:
                fig_device = px.histogram(filtered_df, x='Device_Adoption_Score',
                                         nbins=15, title='Device Adoption Score Distribution',
                                         color_discrete_sequence=['#ab63fa'])
                st.plotly_chart(fig_device, use_container_width=True)

        # --- Row 5: Customer Segmentation ---
        st.subheader("🎪 Customer Segmentation Analysis")
        if 'Customer_Segment' in filtered_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                segment_dist = filtered_df['Customer_Segment'].value_counts().reset_index()
                segment_dist.columns = ['Segment', 'Count']
                
                fig_segment = px.pie(segment_dist, names='Segment', values='Count',
                                    title='Customer Segment Distribution',
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_segment, use_container_width=True)

            with col2:
                # Segment Revenue Contribution
                segment_revenue = filtered_df.groupby('Customer_Segment')['Monthly_Bill'].sum().reset_index()
                segment_revenue.columns = ['Segment', 'Revenue']
                
                fig_seg_rev = px.bar(segment_revenue, x='Segment', y='Revenue',
                                    title='Monthly Revenue by Customer Segment',
                                    color='Revenue',
                                    color_continuous_scale='Blues')
                st.plotly_chart(fig_seg_rev, use_container_width=True)

        # --- Data Table ---
        st.subheader("📊 Detailed Customer Data")
        display_columns = ['Customer_ID', 'Name', 'Region', 'Monthly_Bill', 'Service_Tier', 
                          'Service_Health_Score', 'Payment_Status', 'Calculated_Churn_Risk', 
                          'Customer_Segment'] if 'Service_Health_Score' in filtered_df.columns else ['Customer_ID', 'Region', 'Monthly_Bill']
        display_cols = [col for col in display_columns if col in filtered_df.columns]
        
        st.dataframe(filtered_df[display_cols], use_container_width=True)

# --- Page 2: Viewer Engagement ---
elif page == "Dashboard 2: Viewer Engagement":
    st.markdown("<div class='header-title'>🎬 Content Strategy & Viewer Engagement</div>", unsafe_allow_html=True)
    
    content_df = load_data('data/gold_layer/gold_content_strategy.csv')

    if content_df is not None:
        # --- Sidebar Filters ---
        st.sidebar.subheader("Filter Options")
        # Get unique values as lists for multiselect
        all_genres = list(content_df['Program_Genre'].unique()) if 'Program_Genre' in content_df.columns else []
        all_devices = list(content_df['Device_Type'].unique()) if 'Device_Type' in content_df.columns else []
        
        selected_genres = st.sidebar.multiselect("Select Genres:",
                                                 all_genres)
        selected_devices = st.sidebar.multiselect("Select Devices:",
                                                  all_devices)

        # Filter data
        filtered_content = content_df.copy()
        if selected_genres:
            filtered_content = filtered_content[filtered_content['Program_Genre'].isin(selected_genres)]
        if selected_devices:
            filtered_content = filtered_content[filtered_content['Device_Type'].isin(selected_devices)]

        # --- Key Metrics ---
        st.subheader("📊 Key Engagement Metrics")
        col1, col2, col3, col4 = st.columns(4)

        total_views = filtered_content['Total_Views'].sum() if 'Total_Views' in filtered_content.columns else 0
        total_hours = filtered_content['Total_Engagement_Hours'].sum() if 'Total_Engagement_Hours' in filtered_content.columns else 0
        avg_viewers = filtered_content['Unique_Customer_Count'].mean() if 'Unique_Customer_Count' in filtered_content.columns else 0
        avg_rating = filtered_content['Avg_User_Rating'].mean() if 'Avg_User_Rating' in filtered_content.columns else 0

        create_metric_card(col1, "Total Views", f"{total_views:,.0f}")
        create_metric_card(col2, "Total Engagement Hours", f"{total_hours:,.0f}")
        create_metric_card(col3, "Avg Unique Viewers", f"{avg_viewers:,.0f}")
        create_metric_card(col4, "Avg User Rating", f"{avg_rating:.2f}/5.0")

        # --- Row 1: Content Consumption ---
        st.subheader("📺 Content Consumption Patterns")
        col1, col2 = st.columns(2)

        with col1:
            # Top Genres by View Duration
            if 'Program_Genre' in filtered_content.columns:
                genre_data = filtered_content.groupby('Program_Genre').agg({
                    'Total_View_Duration_Mins': 'sum',
                    'Total_Views': 'sum'
                }).reset_index().sort_values('Total_View_Duration_Mins', ascending=True)
                
                fig_genre = px.bar(genre_data, x='Total_View_Duration_Mins', y='Program_Genre',
                                  orientation='h',
                                  title='Total View Duration by Genre',
                                  color='Total_View_Duration_Mins',
                                  color_continuous_scale='Viridis')
                st.plotly_chart(fig_genre, use_container_width=True)

        with col2:
            # Device Type Distribution
            if 'Device_Type' in filtered_content.columns:
                device_data = filtered_content.groupby('Device_Type').agg({
                    'Total_Views': 'sum',
                    'Unique_Customer_Count': 'sum'
                }).reset_index()
                
                fig_device = px.pie(device_data, names='Device_Type', values='Total_Views',
                                   title='Total Views by Device Type',
                                   color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig_device, use_container_width=True)

        # --- Row 2: Engagement Scores ---
        st.subheader("🎯 Engagement & Quality Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Engagement Score Distribution
            if 'Engagement_Score' in filtered_content.columns:
                fig_engage = px.histogram(filtered_content, x='Engagement_Score',
                                         nbins=15, title='Engagement Score Distribution',
                                         color_discrete_sequence=['#00cc96'])
                fig_engage.add_vline(x=filtered_content['Engagement_Score'].mean(),
                                    line_dash="dash", line_color="red")
                st.plotly_chart(fig_engage, use_container_width=True)

        with col2:
            # Quality Satisfaction
            if 'Quality_Satisfaction' in filtered_content.columns:
                quality_dist = filtered_content['Quality_Satisfaction'].value_counts().reset_index()
                quality_dist.columns = ['Quality', 'Count']
                
                fig_quality = px.pie(quality_dist, names='Quality', values='Count',
                                    title='Streaming Quality Satisfaction Levels',
                                    color_discrete_map={
                                        'Excellent': '#2ecc71',
                                        'Good': '#3498db',
                                        'Fair': '#f39c12',
                                        'Poor': '#e74c3c'
                                    })
                st.plotly_chart(fig_quality, use_container_width=True)

        # --- Row 3: Content Performance ---
        st.subheader("⭐ Content Performance Metrics")
        col1, col2 = st.columns(2)

        with col1:
            # Popularity Tier
            if 'Popularity_Tier' in filtered_content.columns:
                pop_dist = filtered_content['Popularity_Tier'].value_counts().reset_index()
                pop_dist.columns = ['Tier', 'Count']
                
                fig_pop = px.bar(pop_dist, x='Tier', y='Count',
                                title='Content Popularity Distribution',
                                color='Tier',
                                color_discrete_map={
                                    'Viral': '#e74c3c',
                                    'High': '#f39c12',
                                    'Medium': '#3498db',
                                    'Low': '#95a5a6'
                                })
                st.plotly_chart(fig_pop, use_container_width=True)

        with col2:
            # Content Health Status
            if 'Content_Health' in filtered_content.columns:
                health_dist = filtered_content['Content_Health'].value_counts().reset_index()
                health_dist.columns = ['Health', 'Count']
                
                fig_health = px.pie(health_dist, names='Health', values='Count',
                                   title='Content Health Status',
                                   color_discrete_map={
                                       'Excellent': '#2ecc71',
                                       'Healthy': '#3498db',
                                       'At_Risk': '#f39c12',
                                       'Critical': '#e74c3c'
                                   })
                st.plotly_chart(fig_health, use_container_width=True)

        # --- Row 4: Content Reach & Rotation ---
        st.subheader("📊 Content Reach & Viewing Patterns")
        col1, col2 = st.columns(2)

        with col1:
            # Content Reach Score
            if 'Content_Reach_Score' in filtered_content.columns:
                reach_sorted = filtered_content.nlargest(15, 'Content_Reach_Score')
                channel_reach = reach_sorted.groupby('Channel_Name' if 'Channel_Name' in reach_sorted.columns else 'Program_Genre').agg({
                    'Content_Reach_Score': 'mean'
                }).reset_index().sort_values('Content_Reach_Score', ascending=True)
                
                x_col = 'Channel_Name' if 'Channel_Name' in channel_reach.columns else 'Program_Genre'
                fig_reach = px.bar(channel_reach, x='Content_Reach_Score', y=x_col,
                                  orientation='h',
                                  title='Top Content by Reach Score',
                                  color='Content_Reach_Score',
                                  color_continuous_scale='Blues')
                st.plotly_chart(fig_reach, use_container_width=True)

        with col2:
            # Engagement vs User Rating
            if 'Engagement_Score' in filtered_content.columns and 'Avg_User_Rating' in filtered_content.columns:
                fig_engage_rating = px.scatter(filtered_content, x='Engagement_Score', y='Avg_User_Rating',
                                              size='Total_Views', color='Content_Health',
                                              hover_data=['Program_Genre', 'Channel_Name'],
                                              title='Engagement Score vs User Rating',
                                              color_discrete_map={
                                                  'Excellent': '#2ecc71',
                                                  'Healthy': '#3498db',
                                                  'At_Risk': '#f39c12',
                                                  'Critical': '#e74c3c'
                                              })
                st.plotly_chart(fig_engage_rating, use_container_width=True)

        # --- Row 5: Top Performing Content ---
        st.subheader("🏆 Top Performing Content")
        col1, col2 = st.columns(2)

        with col1:
            top_viewed = filtered_content.nlargest(10, 'Total_Views')[['Channel_Name' if 'Channel_Name' in filtered_content.columns else 'Program_Genre', 'Total_Views', 'Engagement_Score', 'Avg_User_Rating']]
            st.write("**Top 10 Most Viewed Content**")
            st.dataframe(top_viewed, use_container_width=True)

        with col2:
            top_rated = filtered_content.nlargest(10, 'Avg_User_Rating')[['Channel_Name' if 'Channel_Name' in filtered_content.columns else 'Program_Genre', 'Avg_User_Rating', 'Engagement_Score', 'Total_Views']]
            st.write("**Top 10 Highest Rated Content**")
            st.dataframe(top_rated, use_container_width=True)

        # --- Quality Metrics Table ---
        st.subheader("📈 Detailed Content Metrics")
        display_cols = ['Program_Genre', 'Channel_Name', 'Device_Type', 'Total_Views', 'Unique_Customer_Count',
                       'Avg_User_Rating', 'Engagement_Score', 'Content_Health', 'Content_Reach_Score']
        available_cols = [col for col in display_cols if col in filtered_content.columns]
        # Shuffle data to show variety of genres (data is sorted by genre in source)
        shuffled_content = filtered_content.sample(frac=1, random_state=42).reset_index(drop=True)
        st.dataframe(shuffled_content[available_cols], use_container_width=True)

# --- Page 3: Network Operations ---
elif page == "Dashboard 3: Network Operations":
    st.markdown("<div class='header-title'>🔧 Network Operations & Service Quality</div>", unsafe_allow_html=True)
    
    operations_df = load_data('data/gold_layer/gold_network_operations.csv')

    if operations_df is not None:
        # --- Sidebar Filters ---
        st.sidebar.subheader("Filter Options")
        selected_equipment = []
        selected_dept = []
        
        if 'Equipment_Model' in operations_df.columns:
            all_equipment = list(operations_df['Equipment_Model'].unique())
            selected_equipment = st.sidebar.multiselect("Equipment Models:",
                                                        all_equipment)
        if 'Department' in operations_df.columns:
            all_depts = list(operations_df['Department'].unique())
            selected_dept = st.sidebar.multiselect("Departments:",
                                                   all_depts)

        # Filter data
        filtered_ops = operations_df.copy()
        if 'Equipment_Model' in operations_df.columns and selected_equipment:
            filtered_ops = filtered_ops[filtered_ops['Equipment_Model'].isin(selected_equipment)]
        if 'Department' in operations_df.columns and selected_dept:
            filtered_ops = filtered_ops[filtered_ops['Department'].isin(selected_dept)]

        # --- Key Metrics ---
        st.subheader("📊 Operational Metrics")
        col1, col2, col3, col4 = st.columns(4)

        total_tickets = len(filtered_ops)
        avg_resolution = filtered_ops['Resolution_Time_Hrs'].mean() if 'Resolution_Time_Hrs' in filtered_ops.columns else 0
        high_performance = (filtered_ops['Performance_Tier'] == 'Expert').sum() if 'Performance_Tier' in filtered_ops.columns else 0
        avg_satisfaction = filtered_ops['Customer_Satisfaction_Rating'].mean() if 'Customer_Satisfaction_Rating' in filtered_ops.columns else 0

        create_metric_card(col1, "Total Service Tickets", f"{total_tickets:,}")
        create_metric_card(col2, "Avg Resolution Time (hrs)", f"{avg_resolution:.1f}")
        create_metric_card(col3, "Expert Technicians", f"{high_performance:,}")
        create_metric_card(col4, "Avg Satisfaction Rating", f"{avg_satisfaction:.2f}/5.0")

        # --- Row 1: Resolution Analysis ---
        st.subheader("⏱️ Ticket Resolution Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Resolution Time Distribution
            fig_res_time = px.histogram(filtered_ops, x='Resolution_Time_Hrs',
                                       nbins=20, title='Resolution Time Distribution',
                                       color_discrete_sequence=['#636EFA'])
            fig_res_time.add_vline(x=filtered_ops['Resolution_Time_Hrs'].mean(),
                                  line_dash="dash", line_color="red")
            st.plotly_chart(fig_res_time, use_container_width=True)

        with col2:
            # Resolution Efficiency
            if 'Resolution_Efficiency' in filtered_ops.columns:
                eff_dist = filtered_ops['Resolution_Efficiency'].value_counts().reset_index()
                eff_dist.columns = ['Efficiency', 'Count']
                
                fig_eff = px.pie(eff_dist, names='Efficiency', values='Count',
                                title='Ticket Resolution Efficiency',
                                color_discrete_map={'High': '#2ecc71', 'Low': '#e74c3c'})
                st.plotly_chart(fig_eff, use_container_width=True)

        # --- Row 2: Technician Performance ---
        st.subheader("👨‍💼 Technician Performance Scorecard")
        col1, col2 = st.columns(2)

        with col1:
            # Technician Performance Tier
            if 'Performance_Tier' in filtered_ops.columns:
                perf_dist = filtered_ops['Performance_Tier'].value_counts().reset_index()
                perf_dist.columns = ['Tier', 'Count']
                
                fig_perf = px.bar(perf_dist, x='Tier', y='Count',
                                 title='Technician Performance Distribution',
                                 color='Tier',
                                 color_discrete_map={
                                     'Expert': '#2ecc71',
                                     'Proficient': '#3498db',
                                     'Developing': '#f39c12'
                                 })
                st.plotly_chart(fig_perf, use_container_width=True)

        with col2:
            # Performance Score Distribution
            if 'Overall_Performance_Score' in filtered_ops.columns:
                fig_score = px.histogram(filtered_ops, x='Overall_Performance_Score',
                                        nbins=20, title='Overall Performance Score Distribution',
                                        color_discrete_sequence=['#ab63fa'])
                st.plotly_chart(fig_score, use_container_width=True)

        # --- Row 3: Equipment & Issues ---
        st.subheader("🛠️ Equipment & Issue Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Issues by Equipment Model
            if 'Equipment_Model' in filtered_ops.columns:
                equip_dist = filtered_ops['Equipment_Model'].value_counts().reset_index()
                equip_dist.columns = ['Equipment', 'Count']
                
                fig_equip = px.bar(equip_dist, x='Equipment', y='Count',
                                  title='Service Tickets by Equipment Model',
                                  color='Count',
                                  color_continuous_scale='Reds')
                st.plotly_chart(fig_equip, use_container_width=True)

        with col2:
            # Equipment Reliability
            if 'Reliability_Index' in filtered_ops.columns:
                reliability = filtered_ops.groupby('Equipment_Model')['Reliability_Index'].mean().reset_index().sort_values('Reliability_Index', ascending=True)
                
                fig_reliability = px.bar(reliability, x='Reliability_Index', y='Equipment_Model',
                                        orientation='h',
                                        title='Equipment Reliability Index',
                                        color='Reliability_Index',
                                        color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_reliability, use_container_width=True)

        # --- Row 4: Issue Categories ---
        st.subheader("📋 Issue Category Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Issues by Category
            if 'Issue_Category' in filtered_ops.columns:
                issue_dist = filtered_ops['Issue_Category'].value_counts().reset_index()
                issue_dist.columns = ['Category', 'Count']
                
                fig_issue = px.pie(issue_dist, names='Category', values='Count',
                                  title='Service Tickets by Issue Category',
                                  color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig_issue, use_container_width=True)

        with col2:
            # Issue Impact Score
            if 'Issue_Impact_Score' in filtered_ops.columns:
                fig_impact = px.histogram(filtered_ops, x='Issue_Impact_Score',
                                         nbins=15, title='Issue Impact Score Distribution',
                                         color_discrete_sequence=['#FFA15A'])
                st.plotly_chart(fig_impact, use_container_width=True)

        # --- Row 5: Signal Quality ---
        st.subheader("📡 Signal Quality Assessment")
        col1, col2 = st.columns(2)

        with col1:
            # Signal Quality Distribution
            if 'Signal_Quality' in filtered_ops.columns:
                signal_dist = filtered_ops['Signal_Quality'].value_counts().reset_index()
                signal_dist.columns = ['Quality', 'Count']
                
                fig_signal = px.pie(signal_dist, names='Quality', values='Count',
                                   title='Signal Quality Distribution',
                                   color_discrete_map={
                                       'Excellent': '#2ecc71',
                                       'Good': '#3498db',
                                       'Fair': '#f39c12',
                                       'Poor': '#e74c3c'
                                   })
                st.plotly_chart(fig_signal, use_container_width=True)

        with col2:
            # Satisfaction vs Resolution Time
            if 'Customer_Satisfaction_Rating' in filtered_ops.columns:
                fig_sat = px.scatter(filtered_ops, x='Resolution_Time_Hrs', y='Customer_Satisfaction_Rating',
                                    size='Issue_Impact_Score' if 'Issue_Impact_Score' in filtered_ops.columns else None,
                                    color='Performance_Tier' if 'Performance_Tier' in filtered_ops.columns else 'Status',
                                    title='Satisfaction vs Resolution Time',
                                    color_discrete_map={
                                        'Expert': '#2ecc71',
                                        'Proficient': '#3498db',
                                        'Developing': '#f39c12'
                                    })
                st.plotly_chart(fig_sat, use_container_width=True)

        # --- Row 6: Department Performance ---
        if 'Department' in filtered_ops.columns:
            st.subheader("🏢 Department Performance")
            dept_perf = filtered_ops.groupby('Department').agg({
                'Ticket_ID': 'count',
                'Resolution_Time_Hrs': 'mean',
                'Customer_Satisfaction_Rating': 'mean' if 'Customer_Satisfaction_Rating' in filtered_ops.columns else lambda x: 4.0,
                'Overall_Performance_Score': 'mean' if 'Overall_Performance_Score' in filtered_ops.columns else lambda x: 75
            }).reset_index()
            dept_perf.columns = ['Department', 'Tickets', 'Avg_Resolution_Hrs', 'Avg_Satisfaction', 'Avg_Performance']
            
            fig_dept = px.bar(dept_perf, x='Department', y=['Avg_Resolution_Hrs', 'Avg_Satisfaction', 'Avg_Performance'],
                             title='Department Performance Comparison',
                             barmode='group')
            st.plotly_chart(fig_dept, use_container_width=True)

        # --- Detailed Operations Data ---
        st.subheader("📊 Detailed Operations Data")
        display_cols = ['Ticket_ID', 'Customer_ID', 'Equipment_Model', 'Issue_Category', 'Status',
                       'Resolution_Time_Hrs', 'Performance_Tier', 'Overall_Performance_Score',
                       'Customer_Satisfaction_Rating', 'Signal_Quality']
        available_cols = [col for col in display_cols if col in filtered_ops.columns]
        st.dataframe(filtered_ops[available_cols], use_container_width=True)

# --- Page 4: Executive Summary ---
elif page == "Executive Summary":
    st.markdown("<div class='header-title'>📊 Executive Summary Dashboard</div>", unsafe_allow_html=True)
    
    billing_df = load_data('data/gold_layer/gold_billing_segmentation.csv')
    operations_df = load_data('data/gold_layer/gold_network_operations.csv')
    content_df = load_data('data/gold_layer/gold_content_strategy.csv')

    if billing_df is not None and operations_df is not None and content_df is not None:
        st.subheader("📌 Business Overview")
        col1, col2, col3, col4 = st.columns(4)

        create_metric_card(col1, "Total Customers", f"{len(billing_df):,}")
        create_metric_card(col2, "Monthly Revenue", f"${billing_df['Monthly_Bill'].sum():,.0f}")
        create_metric_card(col3, "Avg Customer Satisfaction", f"{operations_df['Customer_Satisfaction_Rating'].mean():.2f}/5.0")
        create_metric_card(col4, "Total Content Views", f"{content_df['Total_Views'].sum():,.0f}")

        st.subheader("🎯 Key Insights")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.info(f"""
            **💰 Revenue Health**
            - Total Monthly Revenue: ${billing_df['Monthly_Bill'].sum():,.0f}
            - High-Value Customers: {(billing_df['Bill_Category'] == 'High').sum():,}
            - Annual Revenue Projection: ${billing_df['Monthly_Bill'].sum() * 12:,.0f}
            """)

        with col2:
            st.warning(f"""
            **⚠️ Risk Assessment**
            - High Churn Risk: {(billing_df['Calculated_Churn_Risk'] == 'High').sum():,} customers
            - Payment Issues: {(billing_df['Payment_Status'] != 'Paid').sum():,} customers
            - Contracts Expiring Soon: {(billing_df['Contract_Renewal_Risk'] == 'Expiring Soon').sum():,} customers
            """)

        with col3:
            st.success(f"""
            **✅ Performance Highlights**
            - Expert Technicians: {(operations_df['Performance_Tier'] == 'Expert').sum():,}
            - Avg Resolution Time: {operations_df['Resolution_Time_Hrs'].mean():.1f} hours
            - Viral Content: {(content_df['Popularity_Tier'] == 'Viral').sum():,} items
            """)

        st.subheader("📈 Cross-Functional Analysis")
        col1, col2 = st.columns(2)

        with col1:
            # Revenue vs Churn Risk
            risk_revenue = billing_df.groupby('Calculated_Churn_Risk')['Monthly_Bill'].sum().reset_index()
            fig_risk_rev = px.bar(risk_revenue, x='Calculated_Churn_Risk', y='Monthly_Bill',
                                 title='Revenue at Risk by Churn Category',
                                 color='Calculated_Churn_Risk',
                                 color_discrete_map={'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'})
            st.plotly_chart(fig_risk_rev, use_container_width=True)

        with col2:
            # Engagement vs Satisfaction
            if 'Engagement_Score' in content_df.columns:
                avg_engagement = content_df['Engagement_Score'].mean()
                avg_rating = content_df['Avg_User_Rating'].mean()
                
                metrics_data = pd.DataFrame({
                    'Metric': ['Engagement Score', 'User Rating'],
                    'Score': [avg_engagement, avg_rating * 20]
                })
                
                fig_metrics = px.bar(metrics_data, x='Metric', y='Score',
                                    title='Content Engagement vs User Satisfaction',
                                    color='Metric')
                st.plotly_chart(fig_metrics, use_container_width=True)

