import pandas as pd
import numpy as np
from datetime import datetime

def process_tickets_silver():
    """
    Processes the raw service ticket data into the Silver layer.
    This involves cleaning, standardizing, and applying basic transformations
    to prepare the data for business analysis.
    """
    bronze_tickets_path = 'data/bronze_layer/dish_service_tickets.csv'
    silver_tickets_path = 'data/silver_layer/silver_tickets.csv'

    # Read the raw service ticket data
    tickets_df = pd.read_csv(bronze_tickets_path)

    # Standardize text fields
    tickets_df['Status'] = tickets_df['Status'].str.title()
    tickets_df['Equipment_Model'] = tickets_df['Equipment_Model'].str.title()
    tickets_df['Issue_Category'] = tickets_df['Issue_Category'].str.title()
    tickets_df['Department'] = tickets_df['Department'].str.title() if 'Department' in tickets_df.columns else tickets_df.get('Department')
    tickets_df['Technician_Assigned'] = tickets_df['Technician_Assigned'].str.title()
    
    # Convert date columns
    if 'Created_Date' in tickets_df.columns:
        tickets_df['Created_Date'] = pd.to_datetime(tickets_df['Created_Date'])
    if 'Resolved_Date' in tickets_df.columns:
        tickets_df['Resolved_Date'] = pd.to_datetime(tickets_df['Resolved_Date'])

    # Impute missing signal strength with the mean
    mean_signal = tickets_df['Signal_Strength_dBm'].mean()
    tickets_df['Signal_Strength_dBm'].fillna(mean_signal, inplace=True)

    # Impute missing Technician with placeholder
    tickets_df['Technician_Assigned'].fillna('Unassigned', inplace=True)

    # Impute missing satisfaction ratings with median
    if 'Customer_Satisfaction_Rating' in tickets_df.columns:
        median_satisfaction = tickets_df['Customer_Satisfaction_Rating'].median()
        tickets_df['Customer_Satisfaction_Rating'].fillna(median_satisfaction, inplace=True)

    # Impute missing Buffering Events
    if 'Buffering_Events' in tickets_df.columns:
        tickets_df['Buffering_Events'].fillna(tickets_df['Buffering_Events'].mean(), inplace=True)

    # Save the cleaned tickets data to the Silver layer
    tickets_df.to_csv(silver_tickets_path, index=False)
    print(f"Silver tickets data saved to {silver_tickets_path}")


def process_network_operations_gold():
    """
    Creates the gold network operations data for dashboard analysis.
    This processes the Silver layer tickets data with advanced KPIs for
    network efficiency, technician performance, and issue resolution quality.
    """
    silver_tickets_path = 'data/silver_layer/silver_tickets.csv'
    gold_operations_path = 'data/gold_layer/gold_network_operations.csv'

    # Load the clean tickets data
    tickets_df = pd.read_csv(silver_tickets_path)

    # Calculate Resolution_Efficiency
    avg_resolution_time = tickets_df['Resolution_Time_Hrs'].mean()
    tickets_df['Resolution_Efficiency'] = np.where(
        tickets_df['Resolution_Time_Hrs'] < avg_resolution_time, 'High', 'Low'
    )

    # Technician Performance Scoring (0-100)
    # Based on speed, satisfaction, first contact resolution, and expertise
    technician_stats = tickets_df.groupby('Technician_Assigned').agg(
        Tickets_Count=('Ticket_ID', 'count'),
        Avg_Resolution_Time=('Resolution_Time_Hrs', 'mean'),
        Avg_Satisfaction=('Customer_Satisfaction_Rating', 'mean') if 'Customer_Satisfaction_Rating' in tickets_df.columns else ('Ticket_ID', lambda x: 4.0),
        FCR_Rate=('First_Contact_Resolution', 'mean') if 'First_Contact_Resolution' in tickets_df.columns else ('Ticket_ID', lambda x: 0.7),
        Remote_Resolution_Rate=('Remote_Resolution_Attempted', 'mean') if 'Remote_Resolution_Attempted' in tickets_df.columns else ('Ticket_ID', lambda x: 0.5),
        Cost_Per_Ticket=('Cost_Of_Resolution', 'mean') if 'Cost_Of_Resolution' in tickets_df.columns else ('Ticket_ID', lambda x: 150),
    ).reset_index().fillna(0)

    # Normalize metrics to 0-100 scale for performance scoring
    technician_stats['Speed_Score'] = np.clip(100 - (technician_stats['Avg_Resolution_Time'] / technician_stats['Avg_Resolution_Time'].max() * 100), 0, 100).astype(int)
    technician_stats['Satisfaction_Score'] = np.clip((technician_stats['Avg_Satisfaction'] / 5 * 100), 0, 100).astype(int)
    technician_stats['FCR_Score'] = np.clip((technician_stats['FCR_Rate'] * 100), 0, 100).astype(int)
    technician_stats['Cost_Efficiency_Score'] = np.clip(100 - (technician_stats['Cost_Per_Ticket'] / technician_stats['Cost_Per_Ticket'].max() * 100), 0, 100).astype(int)

    # Overall Performance Score (weighted average)
    technician_stats['Overall_Performance_Score'] = (
        technician_stats['Speed_Score'] * 0.25 +
        technician_stats['Satisfaction_Score'] * 0.35 +
        technician_stats['FCR_Score'] * 0.25 +
        technician_stats['Cost_Efficiency_Score'] * 0.15
    ).astype(int)

    # Performance Tier
    technician_stats['Performance_Tier'] = np.where(
        technician_stats['Overall_Performance_Score'] >= 85, 'Expert',
        np.where(technician_stats['Overall_Performance_Score'] >= 70, 'Proficient', 'Developing')
    )

    # Merge performance stats back to tickets
    tickets_df = pd.merge(tickets_df, technician_stats[['Technician_Assigned', 'Overall_Performance_Score', 'Performance_Tier']], 
                          on='Technician_Assigned', how='left')

    # Issue Resolution Metrics by Category
    tickets_df['Issue_Resolution_Time'] = pd.cut(
        tickets_df['Resolution_Time_Hrs'],
        bins=[0, 4, 24, 72, np.inf],
        labels=['Critical_4h', 'High_24h', 'Medium_72h', 'Low_Extended']
    )

    # Signal Quality Assessment
    tickets_df['Signal_Quality'] = np.where(
        tickets_df['Signal_Strength_dBm'] >= -50, 'Excellent',
        np.where(tickets_df['Signal_Strength_dBm'] >= -70, 'Good',
                 np.where(tickets_df['Signal_Strength_dBm'] >= -85, 'Fair', 'Poor'))
    )

    # Equipment Reliability Score by Model
    equipment_reliability = tickets_df.groupby('Equipment_Model').agg(
        Total_Issues=('Ticket_ID', 'count'),
        Avg_Resolution_Time=('Resolution_Time_Hrs', 'mean'),
        High_Priority_Rate=('Priority_Level', lambda x: (x == 'High').sum() / len(x)) if 'Priority_Level' in tickets_df.columns else (lambda x: 0.2),
        Escalation_Rate=('Escalation_Flag', 'mean') if 'Escalation_Flag' in tickets_df.columns else (lambda x: 0.1),
    ).reset_index().fillna(0)

    equipment_reliability['Reliability_Index'] = np.clip(
        100 - (equipment_reliability['Total_Issues'] / equipment_reliability['Total_Issues'].max() * 40) -
        (equipment_reliability['Escalation_Rate'] * 60),
        0, 100
    ).astype(int)

    # Merge equipment reliability
    tickets_df = pd.merge(tickets_df, equipment_reliability[['Equipment_Model', 'Reliability_Index']], 
                          on='Equipment_Model', how='left')

    # Ticket Priority Management
    tickets_df['Priority_Response_SLA'] = np.where(
        tickets_df['Priority_Level'] == 'Critical', '<4h',
        np.where(tickets_df['Priority_Level'] == 'High', '<8h',
                 np.where(tickets_df['Priority_Level'] == 'Medium', '<24h', '<72h'))
    ) if 'Priority_Level' in tickets_df.columns else '<24h'

    # SLA Compliance
    if 'Created_Date' in tickets_df.columns and 'Resolved_Date' in tickets_df.columns:
        tickets_df['Created_Date'] = pd.to_datetime(tickets_df['Created_Date'])
        tickets_df['Resolved_Date'] = pd.to_datetime(tickets_df['Resolved_Date'])
        tickets_df['Actual_Resolution_Hours'] = (tickets_df['Resolved_Date'] - tickets_df['Created_Date']).dt.total_seconds() / 3600
        
        sla_hours = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
        if 'Priority_Level' in tickets_df.columns:
            tickets_df['SLA_Met'] = tickets_df.apply(
                lambda x: x['Actual_Resolution_Hours'] <= sla_hours.get(x['Priority_Level'], 72),
                axis=1
            )
        
            tickets_df['Days_To_Resolve'] = (tickets_df['Resolved_Date'] - tickets_df['Created_Date']).dt.days

    # Issue Impact Score (combination of factors)
    tickets_df['Issue_Impact_Score'] = (
        np.where(tickets_df['Status'].str.lower() == 'closed', 0, 25) +
        (np.where(tickets_df['Escalation_Flag'] == True, 25, 0) if 'Escalation_Flag' in tickets_df.columns else 0) +
        (np.clip(tickets_df['Total_Tickets'].fillna(0), 0, 50)) +
        (100 - np.clip(tickets_df['Avg_Satisfaction'].fillna(5) * 20, 0, 100))
    ).astype(int) if all(col in tickets_df.columns for col in ['Total_Tickets', 'Avg_Satisfaction']) else tickets_df['Ticket_ID'].apply(lambda x: 50)

    # Department Performance Metrics
    dept_performance = tickets_df.groupby('Department').agg(
        Tickets_Handled=('Ticket_ID', 'count'),
        Avg_Resolution=('Resolution_Time_Hrs', 'mean'),
        Satisfaction_Avg=('Customer_Satisfaction_Rating', 'mean') if 'Customer_Satisfaction_Rating' in tickets_df.columns else ('Ticket_ID', lambda x: 4.0),
    ).reset_index().fillna(0) if 'Department' in tickets_df.columns else pd.DataFrame()

    if not dept_performance.empty:
        dept_performance['Dept_Efficiency'] = np.clip(
            100 - (dept_performance['Avg_Resolution'] / dept_performance['Avg_Resolution'].max() * 100),
            0, 100
        ).astype(int)
        
        tickets_df = pd.merge(tickets_df, dept_performance[['Department', 'Dept_Efficiency']], 
                              on='Department', how='left')

    # Select final columns for the gold layer
    operations_final_df = tickets_df[[
        'Ticket_ID', 'Customer_ID', 'Equipment_Model', 'Issue_Category',
        'Priority_Level' if 'Priority_Level' in tickets_df.columns else 'Status',
        'Status', 'Department' if 'Department' in tickets_df.columns else 'Issue_Category',
        'Technician_Assigned', 'Overall_Performance_Score', 'Performance_Tier',
        'Created_Date' if 'Created_Date' in tickets_df.columns else 'Ticket_ID',
        'Resolution_Time_Hrs', 'Resolution_Efficiency',
        'Issue_Resolution_Time', 'Signal_Quality', 'Reliability_Index',
        'Customer_Satisfaction_Rating' if 'Customer_Satisfaction_Rating' in tickets_df.columns else 'Ticket_ID',
        'Escalation_Flag' if 'Escalation_Flag' in tickets_df.columns else 'Status',
        'First_Contact_Resolution' if 'First_Contact_Resolution' in tickets_df.columns else 'Status',
        'Remote_Resolution_Attempted' if 'Remote_Resolution_Attempted' in tickets_df.columns else 'Status',
        'Cost_Of_Resolution' if 'Cost_Of_Resolution' in tickets_df.columns else 'Ticket_ID',
        'Issue_Impact_Score'
    ]]

    # Remove duplicate columns if they exist
    operations_final_df = operations_final_df.loc[:, ~operations_final_df.columns.duplicated()]

    operations_final_df.to_csv(gold_operations_path, index=False)
    print(f"Gold network operations data saved to {gold_operations_path}")

if __name__ == "__main__":
    process_tickets_silver()
    process_network_operations_gold()
    print("✓ Tickets Silver and Gold layers processed successfully.")
