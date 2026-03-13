import pandas as pd
import numpy as np
from datetime import datetime

def process_logs_silver():
    """
    Processes the raw viewing log data into the Silver layer.
    This involves cleaning, standardizing, and applying basic transformations
    to prepare the data for business analysis.
    """
    bronze_logs_path = 'data/bronze_layer/dish_viewing_logs.csv'
    silver_logs_path = 'data/silver_layer/silver_logs.csv'

    # Read the raw viewing log data
    logs_df = pd.read_csv(bronze_logs_path)
    
    # Standardize text fields
    logs_df['Device_Type'] = logs_df['Device_Type'].str.title()
    logs_df['Channel_Name'] = logs_df['Channel_Name'].str.title()
    logs_df['Program_Genre'] = logs_df['Program_Genre'].str.title()
    logs_df['Stream_Quality'] = logs_df['Stream_Quality'].str.upper()
    
    if 'Content_Type' in logs_df.columns:
        logs_df['Content_Type'] = logs_df['Content_Type'].str.title()
    if 'Video_Resolution' in logs_df.columns:
        logs_df['Video_Resolution'] = logs_df['Video_Resolution'].str.upper()

    # Convert timestamp columns
    if 'Timestamp' in logs_df.columns:
        logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    if 'Start_Time' in logs_df.columns:
        logs_df['Start_Time'] = pd.to_datetime(logs_df['Start_Time'])
    if 'End_Time' in logs_df.columns:
        logs_df['End_Time'] = pd.to_datetime(logs_df['End_Time'])

    # Cap viewing duration outliers
    logs_df['View_Duration_Mins'] = logs_df['View_Duration_Mins'].apply(lambda x: min(x, 480))

    # Impute missing Buffering Events
    if 'Buffering_Events' in logs_df.columns:
        logs_df['Buffering_Events'].fillna(logs_df['Buffering_Events'].mean(), inplace=True)

    # Impute missing User Ratings
    if 'User_Rating' in logs_df.columns:
        median_rating = logs_df['User_Rating'].median()
        logs_df['User_Rating'].fillna(median_rating, inplace=True)

    # Save the cleaned logs data to the Silver layer
    logs_df.to_csv(silver_logs_path, index=False)
    print(f"Silver logs data saved to {silver_logs_path}")

def process_content_strategy_gold():
    """
    Creates the gold content strategy data for dashboard analysis.
    This processes the Silver layer viewing logs with advanced KPIs for
    content engagement, streaming quality, and user behavior analytics.
    """
    silver_logs_path = 'data/silver_layer/silver_logs.csv'
    gold_content_path = 'data/gold_layer/gold_content_strategy.csv'

    # Load the clean logs data
    logs_df = pd.read_csv(silver_logs_path)

    # Convert timestamps
    if 'Timestamp' in logs_df.columns:
        logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    if 'Start_Time' in logs_df.columns:
        logs_df['Start_Time'] = pd.to_datetime(logs_df['Start_Time'])
    if 'End_Time' in logs_df.columns:
        logs_df['End_Time'] = pd.to_datetime(logs_df['End_Time'])

    # --- Content Aggregation with Advanced Metrics ---
    content_agg_df = logs_df.groupby(['Program_Genre', 'Channel_Name', 'Device_Type', 'Stream_Quality']).agg(
        Total_View_Duration_Mins=('View_Duration_Mins', 'sum'),
        Average_View_Duration_Mins=('View_Duration_Mins', 'mean'),
        Unique_Customer_Count=('Customer_ID', 'nunique'),
        Total_Views=('Log_ID', 'count'),
        Avg_Buffering_Events=('Buffering_Events', 'mean') if 'Buffering_Events' in logs_df.columns else ('Log_ID', lambda x: 0),
        Avg_User_Rating=('User_Rating', 'mean') if 'User_Rating' in logs_df.columns else ('Log_ID', lambda x: 4.0),
    ).reset_index().fillna(0)

    # Engagement Score (0-100)
    # Based on view duration, view count, and user ratings
    content_agg_df['Total_Engagement_Hours'] = content_agg_df['Total_View_Duration_Mins'] / 60
    content_agg_df['Engagement_Score'] = np.clip(
        (np.log1p(content_agg_df['Total_Views']) / np.log1p(content_agg_df['Total_Views'].max()) * 40) +
        (content_agg_df['Average_View_Duration_Mins'] / content_agg_df['Average_View_Duration_Mins'].max() * 30) +
        (content_agg_df['Avg_User_Rating'] / 5 * 30),
        0, 100
    ).astype(int)

    # Streaming Quality Performance
    content_agg_df['Quality_Satisfaction'] = np.where(
        content_agg_df['Avg_Buffering_Events'] > 5, 'Poor',
        np.where(content_agg_df['Avg_Buffering_Events'] > 2, 'Fair',
                 np.where(content_agg_df['Avg_Buffering_Events'] > 0, 'Good', 'Excellent'))
    )

    # Content Categorization by Popularity
    content_agg_df['Popularity_Tier'] = pd.qcut(
        content_agg_df['Total_Views'],
        q=4,
        labels=['Low', 'Medium', 'High', 'Viral'],
        duplicates='drop'
    )

    # Customer Retention Indicator
    content_agg_df['Customer_Penetration'] = (
        content_agg_df['Unique_Customer_Count'] / content_agg_df['Unique_Customer_Count'].max() * 100
    ).astype(int)

    # --- Genre Performance Analysis ---
    genre_performance = logs_df.groupby('Program_Genre').agg(
        Genre_Total_Viewers=('Customer_ID', 'nunique'),
        Genre_Total_Views=('Log_ID', 'count'),
        Genre_Avg_Duration=('View_Duration_Mins', 'mean'),
        Genre_Avg_Rating=('User_Rating', 'mean') if 'User_Rating' in logs_df.columns else ('Log_ID', lambda x: 4.0),
        Genre_Peak_Quality=('Stream_Quality', lambda x: x.mode()[0] if len(x.mode()) > 0 else 'HD'),
    ).reset_index().fillna(0)

    genre_performance['Genre_Strength_Index'] = np.clip(
        (np.log1p(genre_performance['Genre_Total_Viewers']) / np.log1p(genre_performance['Genre_Total_Viewers'].max()) * 100),
        0, 100
    ).astype(int)

    # Merge genre metrics back
    content_agg_df = pd.merge(content_agg_df, genre_performance[['Program_Genre', 'Genre_Strength_Index']], 
                               on='Program_Genre', how='left')

    # --- Device Usage Analytics ---
    device_performance = logs_df.groupby('Device_Type').agg(
        Device_Total_Views=('Log_ID', 'count'),
        Device_Unique_Users=('Customer_ID', 'nunique'),
        Device_Avg_Duration=('View_Duration_Mins', 'mean'),
        Device_Preferred_Quality=('Stream_Quality', lambda x: x.mode()[0] if len(x.mode()) > 0 else 'HD'),
        Device_Avg_Buffering=('Buffering_Events', 'mean') if 'Buffering_Events' in logs_df.columns else ('Log_ID', lambda x: 0),
    ).reset_index().fillna(0)

    device_performance['Device_Adoption_Index'] = np.clip(
        (device_performance['Device_Total_Views'] / device_performance['Device_Total_Views'].max() * 100),
        0, 100
    ).astype(int)

    # Merge device metrics
    content_agg_df = pd.merge(content_agg_df, device_performance[['Device_Type', 'Device_Adoption_Index']], 
                               on='Device_Type', how='left')

    # --- Content Type Performance ---
    if 'Content_Type' in logs_df.columns:
        content_type_perf = logs_df.groupby('Content_Type').agg(
            ContentType_Views=('Log_ID', 'count'),
            ContentType_Unique_Viewers=('Customer_ID', 'nunique'),
            ContentType_Avg_Duration=('View_Duration_Mins', 'mean'),
        ).reset_index().fillna(0)

        # Merge content type metrics
        logs_df = pd.merge(logs_df, content_type_perf, on='Content_Type', how='left')

    # --- Streaming Quality Analysis ---
    quality_analysis = logs_df.groupby('Stream_Quality').agg(
        Quality_View_Count=('Log_ID', 'count'),
        Quality_Avg_Buffering=('Buffering_Events', 'mean') if 'Buffering_Events' in logs_df.columns else ('Log_ID', lambda x: 0),
        Quality_Avg_Rating=('User_Rating', 'mean') if 'User_Rating' in logs_df.columns else ('Log_ID', lambda x: 4.0),
    ).reset_index().fillna(0)

    # --- Hour of Day & Viewing Patterns ---
    if 'Start_Time' in logs_df.columns:
        logs_df['Hour_Of_Day'] = logs_df['Start_Time'].dt.hour
        logs_df['Day_Of_Week'] = logs_df['Start_Time'].dt.day_name()
        
        peak_analysis = logs_df.groupby('Hour_Of_Day').agg(
            Peak_Views=('Log_ID', 'count'),
            Peak_Duration=('View_Duration_Mins', 'mean')
        ).reset_index().fillna(0)

    # --- Content Churn Risk (content that's losing viewership) ---
    content_agg_df['Content_Health'] = np.where(
        content_agg_df['Engagement_Score'] >= 75, 'Excellent',
        np.where(content_agg_df['Engagement_Score'] >= 50, 'Healthy',
                 np.where(content_agg_df['Engagement_Score'] >= 25, 'At_Risk', 'Critical'))
    )

    # Viewing Rotation Index (how frequently is this content viewed)
    content_agg_df['Viewing_Frequency'] = np.clip(
        (content_agg_df['Total_Views'] / content_agg_df['Unique_Customer_Count'] * 10),
        0, 100
    ).astype(int)

    # Content Reach Score (how many unique customers interact with it)
    content_agg_df['Content_Reach_Score'] = np.clip(
        (content_agg_df['Customer_Penetration'] * 0.6) +
        (content_agg_df['Viewing_Frequency'] * 0.4),
        0, 100
    ).astype(int)

    # --- Advertising Opportunity Score ---
    # Content that has high engagement but lower satisfaction might benefit from ad support
    content_agg_df['Ad_Opportunity_Score'] = np.clip(
        (content_agg_df['Total_Views'] / content_agg_df['Total_Views'].max() * 100) -
        (content_agg_df['Avg_User_Rating'] / 5 * 20),
        0, 100
    ).astype(int)

    # Select final columns for the gold layer
    content_final_df = content_agg_df[[
        'Program_Genre', 'Channel_Name', 'Device_Type', 'Stream_Quality',
        'Total_View_Duration_Mins', 'Total_Engagement_Hours', 'Average_View_Duration_Mins',
        'Total_Views', 'Unique_Customer_Count',
        'Avg_Buffering_Events', 'Avg_User_Rating', 'Quality_Satisfaction',
        'Engagement_Score', 'Popularity_Tier',
        'Customer_Penetration', 'Genre_Strength_Index', 'Device_Adoption_Index',
        'Content_Health', 'Viewing_Frequency', 'Content_Reach_Score',
        'Ad_Opportunity_Score'
    ]]

    # Remove any duplicate columns
    content_final_df = content_final_df.loc[:, ~content_final_df.columns.duplicated()]

    content_final_df.to_csv(gold_content_path, index=False)
    print(f"Gold content strategy data saved to {gold_content_path}")

if __name__ == "__main__":
    process_logs_silver()
    process_content_strategy_gold()
    print("✓ Logs Silver and Gold layers processed successfully.")
