import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# --- 1. Generate dish_customers.csv ---
def generate_customers_data(num_records=12000):
    """Generates enhanced dish_customers dataset with 12k+ records and additional columns."""
    customer_ids = list(range(1001, 1001 + num_records - 50))
    # Introduce 50 duplicate IDs
    duplicates = random.sample(customer_ids, 50)
    customer_ids.extend(duplicates)
    random.shuffle(customer_ids)

    # Subscription types with mixed casing for inconsistency
    subscription_types = ["America's Top 120", "america's top 200", "AMERICA'S TOP 250", "Sling Blue", "sling orange", "America's Top 500", "Spanish Premium"]
    payment_statuses = ['Paid', 'Pending', 'Overdue', 'Disputed']
    regions = ['Northeast', 'Midwest', 'South', 'West', 'Southwest', 'Northwest']
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    service_tiers = ['Basic', 'Standard', 'Premium', 'VIP']
    employment_statuses = ['Employed', 'Self-Employed', 'Retired', 'Student', 'Unemployed']

    data = {
        'Customer_ID': customer_ids[:num_records],
        'Name': [fake.name() for _ in range(num_records)],
        'Email': [fake.email() for _ in range(num_records)],
        'Phone': [fake.phone_number() for _ in range(num_records)],
        'Address': [fake.address().replace('\n', ', ') for _ in range(num_records)],
        'City': [fake.city() for _ in range(num_records)],
        'State': [fake.state() for _ in range(num_records)],
        'Zip_Code': [fake.zipcode() for _ in range(num_records)],
        'Subscription_Type': [random.choice(subscription_types) for _ in range(num_records)],
        'Service_Tier': [random.choice(service_tiers) for _ in range(num_records)],
        'Monthly_Bill': [round(random.uniform(50.0, 250.0), 2) for _ in range(num_records)],
        'Join_Date': [fake.date_between(start_date='-5y', end_date='today') for _ in range(num_records)],
        'Payment_Status': [random.choice(payment_statuses) for _ in range(num_records)],
        'Region': [random.choice(regions) for _ in range(num_records)],
        'Contract_End': [fake.date_between(start_date='today', end_date='+2y') for _ in range(num_records)],
        'Age_Group': [random.choice(age_groups) for _ in range(num_records)],
        'Employment_Status': [random.choice(employment_statuses) for _ in range(num_records)],
        'Customer_Lifetime_Value': [round(random.uniform(500, 15000), 2) for _ in range(num_records)],
        'Loyalty_Points': [random.randint(0, 50000) for _ in range(num_records)],
        'Churn_Risk': [random.choice(['Low', 'Medium', 'High']) for _ in range(num_records)],
        'Number_Of_Devices': [random.randint(1, 8) for _ in range(num_records)],
        'Has_Outdoor_Dish': [random.choice([True, False]) for _ in range(num_records)],
        'Auto_Pay_Enabled': [random.choice([True, False]) for _ in range(num_records)],
        'Paperless_Billing': [random.choice([True, False]) for _ in range(num_records)],
        'Last_Payment_Date': [fake.date_between(start_date='-3m', end_date='today') for _ in range(num_records)]
    }
    df = pd.DataFrame(data)

    # --- Inject Data Quality Issues ---
    # 5% Missing values in Monthly_Bill
    missing_indices = df.sample(frac=0.05).index
    df.loc[missing_indices, 'Monthly_Bill'] = np.nan

    # 2% Missing Phone values
    missing_phone = df.sample(frac=0.02).index
    df.loc[missing_phone, 'Phone'] = np.nan

    # Outliers for Monthly_Bill
    outlier_indices = df.sample(n=50).index
    df.loc[outlier_indices, 'Monthly_Bill'] = [round(random.uniform(5000.0, 7000.0), 2) for _ in range(50)]

    # Future Join_Date values (data quality issue)
    future_date_indices = df.sample(n=100).index
    for i in future_date_indices:
        df.loc[i, 'Join_Date'] = fake.date_between(start_date='+1y', end_date='+4y')

    # Ensure Customer_ID for duplicates has slightly different info
    for dup_id in duplicates:
        dup_rows = df[df['Customer_ID'] == dup_id]
        if len(dup_rows) > 1:
            # Change name and monthly bill for the second instance
            df.loc[dup_rows.index[1], 'Name'] = fake.name()
            df.loc[dup_rows.index[1], 'Monthly_Bill'] = round(random.uniform(50.0, 250.0), 2)

    return df

# --- 2. Generate dish_service_tickets.csv ---
def generate_service_tickets_data(customer_ids, num_records=11500):
    """Generates enhanced dish_service_tickets dataset with 11k+ records and additional columns."""
    equipment_models = ['Hopper 3', 'Joey', 'Wally', 'Outdoor Dish', 'Hopper 2', 'Super Joey', '4K Joey']
    issue_categories = ['Signal Loss', 'Hardware Failure', 'Billing', 'Remote Pairing', 'Installation', 'Upgrade', 'Cancellation', 'Activation']
    # Statuses with mixed casing for inconsistency
    statuses = ['CLOSED', 'Open', 'In Progress', 'closed', 'Clsd', 'On Hold', 'Resolved']
    priorities = ['Low', 'Medium', 'High', 'Critical']
    departments = ['Technical Support', 'Billing', 'Installation', 'Sales', 'Network Operations', 'Equipment Support']
    
    base_date = datetime.now() - timedelta(days=730)

    data = {
        'Ticket_ID': list(range(2001, 2001 + num_records)),
        'Customer_ID': random.choices(customer_ids, k=num_records),
        'Equipment_Model': [random.choice(equipment_models) for _ in range(num_records)],
        'Issue_Category': [random.choice(issue_categories) for _ in range(num_records)],
        'Priority_Level': [random.choice(priorities) for _ in range(num_records)],
        'Signal_Strength_dBm': [random.randint(-100, -30) for _ in range(num_records)],
        'Technician_Assigned': [fake.name() for _ in range(num_records)],
        'Department': [random.choice(departments) for _ in range(num_records)],
        'Created_Date': [base_date + timedelta(days=random.randint(0, 730)) for _ in range(num_records)],
        'Resolved_Date': [base_date + timedelta(days=random.randint(0, 730)) for _ in range(num_records)],
        'Resolution_Time_Hrs': [random.randint(1, 72) for _ in range(num_records)],
        'Status': [random.choice(statuses) for _ in range(num_records)],
        'Customer_Satisfaction_Rating': [round(random.uniform(1.0, 5.0), 1) for _ in range(num_records)],
        'Escalation_Flag': [random.choice([True, False]) for _ in range(num_records)],
        'First_Contact_Resolution': [random.choice([True, False]) for _ in range(num_records)],
        'Technician_Expertise_Level': [random.choice(['Junior', 'Senior', 'Expert']) for _ in range(num_records)],
        'Remote_Resolution_Attempted': [random.choice([True, False]) for _ in range(num_records)],
        'On_Site_Visit_Required': [random.choice([True, False]) for _ in range(num_records)],
        'Cost_Of_Resolution': [round(random.uniform(0, 500), 2) for _ in range(num_records)],
        'Parts_Replaced': [random.choice([True, False]) for _ in range(num_records)]
    }
    df = pd.DataFrame(data)

    # --- Inject Data Quality Issues ---
    # 5% Missing values in Signal_Strength_dBm
    missing_indices = df.sample(frac=0.05).index
    df.loc[missing_indices, 'Signal_Strength_dBm'] = np.nan

    # 3% Missing Satisfaction Ratings
    missing_rating = df.sample(frac=0.03).index
    df.loc[missing_rating, 'Customer_Satisfaction_Rating'] = np.nan

    # 2% Missing Technician names
    missing_tech = df.sample(frac=0.02).index
    df.loc[missing_tech, 'Technician_Assigned'] = np.nan

    return df

# --- 3. Generate dish_viewing_logs.csv ---
def generate_viewing_logs_data(customer_ids, num_records=15000):
    """Generates enhanced dish_viewing_logs dataset with 15k+ records and additional columns."""
    channels = ['ESPN', 'HBO', 'CNN', 'Discovery Channel', 'HGTV', 'FOX News', 'Local Channel', 'NBC', 'ABC', 'CBS', 'Showtime', 'AMC', 'Netflix', 'Disney+']
    genres = ['Sports', 'Movie', 'News', 'Documentary', 'Reality TV', 'Drama', 'Comedy', 'Thriller', 'Animation', 'Talk Show', 'Series']
    devices = ['Smart TV', 'Mobile App', 'Set-top Box', 'Tablet', 'Laptop']
    qualities = ['4K', 'HD', 'SD']
    networks = ['Home WiFi', 'Mobile Network', 'Guest WiFi', 'Cellular']
    
    base_date = datetime.now() - timedelta(days=365)

    data = {
        'Log_ID': list(range(3001, 3001 + num_records)),
        'Customer_ID': random.choices(customer_ids, k=num_records),
        'Channel_Name': [random.choice(channels) for _ in range(num_records)],
        'Program_Genre': [random.choice(genres) for _ in range(num_records)],
        'Device_Type': [random.choice(devices) for _ in range(num_records)],
        'Network_Type': [random.choice(networks) for _ in range(num_records)],
        'View_Duration_Mins': [random.randint(5, 240) for _ in range(num_records)],
        'Stream_Quality': [random.choice(qualities) for _ in range(num_records)],
        'Video_Resolution': [random.choice(['1080p', '720p', '480p', '2160p']) for _ in range(num_records)],
        'Buffering_Events': [random.randint(0, 15) for _ in range(num_records)],
        'Start_Time': [base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59)) for _ in range(num_records)],
        'End_Time': [base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59)) for _ in range(num_records)],
        'Timestamp': [base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59)) for _ in range(num_records)],
        'Content_Type': [random.choice(['Live', 'On-Demand', 'Recorded']) for _ in range(num_records)],
        'Playback_Speed': [random.choice(['1x', '1.5x', '2x', '0.5x']) for _ in range(num_records)],
        'Subtitles_Enabled': [random.choice([True, False]) for _ in range(num_records)],
        'Closed_Captions_Enabled': [random.choice([True, False]) for _ in range(num_records)],
        'DVR_Playback': [random.choice([True, False]) for _ in range(num_records)],
        'Skip_Ads': [random.choice([True, False]) for _ in range(num_records)],
        'User_Rating': [random.choice([1, 2, 3, 4, 5, None]) for _ in range(num_records)],
        'Autoplay_Triggered': [random.choice([True, False]) for _ in range(num_records)]
    }
    df = pd.DataFrame(data)

    # --- Inject Data Quality Issues ---
    # Outliers for View_Duration_Mins
    outlier_indices = df.sample(n=100).index
    df.loc[outlier_indices, 'View_Duration_Mins'] = [random.randint(5000, 9000) for _ in range(100)]

    # 3% Missing Buffering Events
    missing_buffering = df.sample(frac=0.03).index
    df.loc[missing_buffering, 'Buffering_Events'] = np.nan

    # 5% Missing User Ratings (already has some None values, but add more)
    missing_rating_indices = df.sample(frac=0.05).index
    df.loc[missing_rating_indices, 'User_Rating'] = np.nan

    return df


# --- Main execution ---
if __name__ == "__main__":
    print("Generating enhanced DISH Network datasets...")
    print("-" * 60)

    # Generate and save Customers
    print("Generating dish_customers.csv (12,000 records with 24 columns)...")
    customers_df = generate_customers_data()
    customers_df.to_csv('data/bronze_layer/dish_customers.csv', index=False)
    print(f"✓ Successfully generated {len(customers_df)} records for data/bronze_layer/dish_customers.csv")
    print(f"  Columns: {len(customers_df.columns)}")

    # Use customer IDs for other datasets
    customer_id_list = customers_df['Customer_ID'].unique().tolist()

    # Generate and save Service Tickets
    print("\nGenerating dish_service_tickets.csv (11,500 records with 20 columns)...")
    service_tickets_df = generate_service_tickets_data(customer_id_list)
    service_tickets_df.to_csv('data/bronze_layer/dish_service_tickets.csv', index=False)
    print(f"✓ Successfully generated {len(service_tickets_df)} records for data/bronze_layer/dish_service_tickets.csv")
    print(f"  Columns: {len(service_tickets_df.columns)}")

    # Generate and save Viewing Logs
    print("\nGenerating dish_viewing_logs.csv (15,000 records with 23 columns)...")
    viewing_logs_df = generate_viewing_logs_data(customer_id_list)
    viewing_logs_df.to_csv('data/bronze_layer/dish_viewing_logs.csv', index=False)
    print(f"✓ Successfully generated {len(viewing_logs_df)} records for data/bronze_layer/dish_viewing_logs.csv")
    print(f"  Columns: {len(viewing_logs_df.columns)}")

    print("-" * 60)
    print("✓ All datasets generated successfully!")
    print(f"Total records generated: {len(customers_df) + len(service_tickets_df) + len(viewing_logs_df):,}")
