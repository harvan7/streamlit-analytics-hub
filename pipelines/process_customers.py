import pandas as pd
import numpy as np
from datetime import datetime

def process_customers_silver():
    """
    Processes the raw customer data into the Silver layer.
    This involves cleaning, standardizing, and applying basic transformations
    to prepare the data for business analysis. The goal is to create a clean,
    consistent, and standardized version of the source data.
    """
    bronze_customers_path = 'data/bronze_layer/dish_customers.csv'
    silver_customers_path = 'data/silver_layer/silver_customers.csv'

    # Read the raw customer data - this is the first step of our pipeline
    customers_df = pd.read_csv(bronze_customers_path)

    # Standardize categorical data to Title Case for consistency
    customers_df['Subscription_Type'] = customers_df['Subscription_Type'].str.title()
    customers_df['Service_Tier'] = customers_df['Service_Tier'].str.title()
    customers_df['Employment_Status'] = customers_df['Employment_Status'].str.title()

    # Standardize string fields to proper format
    customers_df['Name'] = customers_df['Name'].str.title()
    customers_df['City'] = customers_df['City'].str.title()
    customers_df['State'] = customers_df['State'].str.upper()

    # Impute missing billing data with the median
    median_bill = customers_df['Monthly_Bill'].median()
    customers_df['Monthly_Bill'].fillna(median_bill, inplace=True)

    # Impute missing Phone with placeholder
    customers_df['Phone'].fillna('Unknown', inplace=True)

    # Convert date columns
    customers_df['Join_Date'] = pd.to_datetime(customers_df['Join_Date'])
    customers_df['Contract_End'] = pd.to_datetime(customers_df['Contract_End'])
    customers_df['Last_Payment_Date'] = pd.to_datetime(customers_df['Last_Payment_Date'])

    # Correct future join dates
    future_date_cap = pd.to_datetime('2026-03-13')
    customers_df.loc[customers_df['Join_Date'] > future_date_cap, 'Join_Date'] = future_date_cap

    # Deduplicate customer records based on Customer_ID
    customers_df.drop_duplicates(subset=['Customer_ID'], keep='first', inplace=True)
    
    # Save the cleaned customer data to the Silver layer
    customers_df.to_csv(silver_customers_path, index=False)
    print(f"Silver customers data saved to {silver_customers_path}")


def process_billing_gold():
    """
    Creates the gold billing segmentation data for dashboard analysis.
    This processes the Silver layer customer and ticket data with advanced KPIs
    for revenue, customer health, and churn prediction.
    """
    silver_customers_path = 'data/silver_layer/silver_customers.csv'
    silver_tickets_path = 'data/silver_layer/silver_tickets.csv'
    gold_billing_path = 'data/gold_layer/gold_billing_segmentation.csv'

    # Load the clean data
    customers_df = pd.read_csv(silver_customers_path)
    tickets_df = pd.read_csv(silver_tickets_path)

    # Convert date columns
    customers_df['Join_Date'] = pd.to_datetime(customers_df['Join_Date'])
    customers_df['Last_Payment_Date'] = pd.to_datetime(customers_df['Last_Payment_Date'])
    
    # Aggregate ticket metrics by customer
    ticket_metrics = tickets_df.groupby('Customer_ID').agg(
        Total_Tickets=('Ticket_ID', 'count'),
        Avg_Resolution_Time=('Resolution_Time_Hrs', 'mean'),
        Critical_Escalations=('Escalation_Flag', 'sum') if 'Escalation_Flag' in tickets_df.columns else ('Ticket_ID', 'count'),
        Avg_Satisfaction=('Customer_Satisfaction_Rating', 'mean') if 'Customer_Satisfaction_Rating' in tickets_df.columns else ('Ticket_ID', 'count'),
        FCR_Rate=('First_Contact_Resolution', 'mean') if 'First_Contact_Resolution' in tickets_df.columns else ('Ticket_ID', 'count'),
        Avg_Signal_Strength=('Signal_Strength_dBm', 'mean') if 'Signal_Strength_dBm' in tickets_df.columns else ('Ticket_ID', 'count')
    ).reset_index().fillna(0)

    # Join customer with ticket metrics
    billing_df = pd.merge(customers_df, ticket_metrics, on='Customer_ID', how='left').fillna(0)

    # Calculate customer tenure in years
    billing_df['Customer_Tenure_Years'] = (pd.to_datetime('2026-03-13') - billing_df['Join_Date']).dt.days / 365.25

    # Create Bill_Category for revenue segmentation
    bins = [0, 80, 150, np.inf]
    labels = ['Low', 'Medium', 'High']
    billing_df['Bill_Category'] = pd.cut(billing_df['Monthly_Bill'], bins=bins, labels=labels, right=False)

    # Calculate Monthly Revenue Impact
    billing_df['Monthly_Revenue'] = billing_df['Monthly_Bill'] * 12

    # Service Health Score (0-100)
    # Combination of signal strength, ticket volume, and satisfaction
    billing_df['Service_Health_Score'] = (
        (np.clip(-billing_df['Avg_Signal_Strength'] + 100, 0, 100) * 0.3) +
        (np.clip(100 - (billing_df['Total_Tickets'] * 10), 0, 100) * 0.3) +
        (np.clip(billing_df['Avg_Satisfaction'] * 20, 0, 100) * 0.4)
    ).astype(int)

    # Payment Risk Score (0-100) - higher is riskier
    billing_df['Payment_Days_Overdue'] = (pd.to_datetime('2026-03-13') - billing_df['Last_Payment_Date']).dt.days
    billing_df['Payment_Risk_Score'] = np.where(
        billing_df['Payment_Status'] == 'Overdue',
        np.clip(billing_df['Payment_Days_Overdue'] * 2, 0, 100),
        np.where(billing_df['Payment_Status'] == 'Pending', 30, 
                 np.where(billing_df['Payment_Status'] == 'Disputed', 50, 10))
    ).astype(int)

    # Churn Risk Classification
    billing_df['Calculated_Churn_Risk'] = np.where(
        billing_df['Service_Health_Score'] < 40, 'High',
        np.where(billing_df['Service_Health_Score'] < 70, 'Medium', 'Low')
    )

    # LTV Index (normalized against customer_lifetime_value)
    billing_df['LTV_Index'] = np.clip(
        (billing_df['Customer_Lifetime_Value'] - billing_df['Customer_Lifetime_Value'].min()) /
        (billing_df['Customer_Lifetime_Value'].max() - billing_df['Customer_Lifetime_Value'].min()) * 100,
        0, 100
    ).astype(int)

    # Loyalty Index (combination of tenure, loyalty points, and engagement)
    billing_df['Loyalty_Index'] = np.clip(
        (billing_df['Customer_Tenure_Years'] / 5 * 40) +
        (np.clip(billing_df['Loyalty_Points'] / billing_df['Loyalty_Points'].max() * 60, 0, 60)),
        0, 100
    ).astype(int)

    # Device Adoption Score
    billing_df['Device_Adoption_Score'] = np.clip(
        (billing_df['Number_Of_Devices'] / 8 * 100), 0, 100
    ).astype(int)

    # Contract Risk
    contract_end = pd.to_datetime(billing_df['Contract_End']) if 'Contract_End' in billing_df.columns else pd.to_datetime('2026-03-13')
    billing_df['Days_Until_Contract_End'] = (contract_end - pd.to_datetime('2026-03-13')).dt.days
    billing_df['Contract_Renewal_Risk'] = np.where(
        billing_df['Days_Until_Contract_End'] < 30, 'Expiring Soon',
        np.where(billing_df['Days_Until_Contract_End'] < 90, 'At Risk', 'Stable')
    )

    # Revenue Health Indicator
    billing_df['Revenue_Health'] = np.where(
        billing_df['Monthly_Bill'] < 100, 'Undermonetized',
        np.where((billing_df['Monthly_Bill'] >= 100) & (billing_df['Monthly_Bill'] < 180), 'Optimal',
                 'Premium')
    )

    # Segment customers into buckets for marketing
    billing_df['Customer_Segment'] = np.where(
        billing_df['Service_Health_Score'] >= 80, 'VIP_Advocates',
        np.where((billing_df['Service_Health_Score'] >= 60) & (billing_df['LTV_Index'] >= 50), 'Growth_Opportunity',
                 np.where(billing_df['Service_Health_Score'] < 40, 'At_Risk_High_Value',
                          'Standard'))
    )

    # Select final columns for the gold layer
    billing_final_df = billing_df[[
        'Customer_ID', 'Name', 'City', 'State', 'Region', 'Email',
        'Subscription_Type', 'Service_Tier', 'Monthly_Bill', 'Monthly_Revenue',
        'Bill_Category', 'Payment_Status', 'Payment_Risk_Score', 'Payment_Days_Overdue',
        'Customer_Tenure_Years', 'Join_Date', 'Contract_Renewal_Risk',
        'Auto_Pay_Enabled', 'Paperless_Billing',
        'Total_Tickets', 'Avg_Resolution_Time', 'Critical_Escalations',
        'Avg_Satisfaction', 'FCR_Rate', 'Avg_Signal_Strength',
        'Service_Health_Score',
        'Churn_Risk', 'Calculated_Churn_Risk',
        'Customer_Lifetime_Value', 'LTV_Index',
        'Loyalty_Points', 'Loyalty_Index',
        'Number_Of_Devices', 'Device_Adoption_Score',
        'Age_Group', 'Employment_Status',
        'Revenue_Health', 'Customer_Segment'
    ]]

    billing_final_df.to_csv(gold_billing_path, index=False)
    print(f"Gold billing segmentation data saved to {gold_billing_path}")

if __name__ == "__main__":
    process_customers_silver()
    process_billing_gold()
    print("✓ Customers Silver and Gold layers processed successfully.")
