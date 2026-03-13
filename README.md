# DISH Network Analytics Hub

A comprehensive data intelligence solution built with Streamlit, featuring advanced analytics dashboards, data pipelines, and 38,500+ synthetic records with 20+ calculated KPIs.

## 📊 Dashboard Overview

### Dashboard 1: Financial & Customer Health Insights
- **Total Monthly Revenue** - Aggregated billing metrics across regions and segments
- **Customer Lifetime Value Analysis** - LTV trends and segmentation
- **Payment Health Tracking** - Payment status distribution and risk indicators
- **Regional Performance** - Revenue breakdown by geography
- **Service Health Scores** - Distribution of customer service quality metrics
- **Detailed Customer Data** - Full customer repository with 11,950+ records (filterable)

**Filters:** Regions, Customer Segments

### Dashboard 2: Viewer Engagement & Content Strategy
- **Total Views & Engagement Metrics** - Content consumption KPIs
- **Engagement Score Distribution** - Viewer satisfaction analysis
- **Content Popularity Tiers** - Viral, High, Medium, Low classification
- **Quality Satisfaction Levels** - Streaming experience assessment
- **Content Health Status** - Content performance monitoring
- **Genre & Device Analysis** - Consumption patterns by genre and device type
- **Top Performing Content** - Most viewed and highest-rated programs
- **Detailed Content Metrics** - 2,306+ content records (shuffled for variety)

**Filters:** Program Genres, Device Types

### Dashboard 3: Network Operations & Service Quality
- **Total Service Tickets** - Volume of support requests
- **Average Resolution Time** - Performance efficiency metrics
- **Expert Technician Count** - Workforce capacity indicators
- **Ticket Resolution Efficiency** - High/Low resolution success rates
- **Equipment Reliability** - Model-based performance analysis
- **Issue Category Breakdown** - Support ticket distribution
- **Department Performance** - Team-level metrics comparison
- **Detailed Operations Data** - 11,950+ ticket records (filterable)

**Filters:** Equipment Models, Departments

### Executive Summary
- Cross-functional KPI overview
- Key insights and trends
- High-level performance indicators

## 🗂️ Project Structure

```
Dish Data Solution Demo/
├── app.py                          # Main Streamlit application (645 lines)
├── process_dish_data.py            # Data processing orchestrator
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/
│   ├── bronze_layer/              # Raw source data
│   │   ├── dish_customers.csv      # 12,000 customer records
│   │   ├── dish_service_tickets.csv # 11,500 ticket records
│   │   ├── dish_viewing_logs.csv   # 15,000 viewing log records
│   │   └── generate_dish_datasets.py
│   │
│   ├── silver_layer/              # Cleaned and normalized data
│   │   ├── silver_customers.csv
│   │   ├── silver_logs.csv
│   │   └── silver_tickets.csv
│   │
│   └── gold_layer/                # Aggregated analytics data
│       ├── gold_billing_segmentation.csv      # 11,950 customer analytics
│       ├── gold_content_strategy.csv          # 2,306 content analytics
│       └── gold_network_operations.csv        # 11,950 operations analytics
│
└── pipelines/
    ├── process_customers.py       # Customer KPI transformations
    ├── process_tickets.py         # Operations KPI transformations
    └── process_logs.py            # Content engagement KPI transformations
```

## 📈 Key Features

### Advanced KPI Scoring
- **Service Health Score** (0-100): Weighted composite of uptime, satisfaction, performance
- **Payment Risk Score** (0-100): Financial health indicator
- **Churn Risk Classification**: High/Medium/Low customer retention risk
- **LTV Index**: Customer lifetime value ranking
- **Loyalty Index**: Customer retention propensity score
- **Engagement Score** (0-100): Viewer activity and satisfaction metric
- **Popularity Tier**: Viral/High/Medium/Low content classification
- **Content Health**: Excellent/Healthy/At_Risk/Critical content status
- And 12+ more sophisticated metrics...

### Data Transformation Pipeline
1. **Bronze Layer** (Raw): Synthetically generated source data with inherent quality issues
2. **Silver Layer** (Cleaned): Data validation, normalization, outlier handling
3. **Gold Layer** (Analytics): Aggregated metrics, KPI calculations, business insights

### Interactive Filtering
- Multi-select dropdowns for dynamic data filtering
- Real-time KPI updates based on filter selections
- Cascading filters across dashboard sections
- Support for no-filter ("All") selections

### Data Visualization
- 15+ chart types: Bar, Pie, Scatter, Histogram, and more
- Plotly interactive visualizations with hover details
- Color-coded status indicators and heatmaps
- Distribution analysis with mean/median indicators

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip or conda

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/harvan7/streamlit-analytics-hub.git
cd streamlit-analytics-hub
```

2. **Create virtual environment** (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

1. **Generate synthetic data** (optional - data already included)
```bash
python process_dish_data.py
```

2. **Launch Streamlit dashboard**
```bash
streamlit run app.py
```

3. **Access in browser**
```
http://localhost:8501
```

## 📊 Data Specifications

### Dataset Sizes
- **Bronze Layer**: 38,500 total records
  - Customers: 12,000 records × 25 columns
  - Service Tickets: 11,500 records × 20 columns
  - Viewing Logs: 15,000 records × 21 columns

- **Gold Layer**: 2,306-11,950 records per dataset
  - Customer Analytics: 11,950 records × 24 columns
  - Content Analytics: 2,306 records × 21 columns
  - Operations Analytics: 11,950 records × 22 columns

### Key Columns
**Customers:**  Customer_ID, Name, Region, Service_Tier, Monthly_Bill, Service_Health_Score, Payment_Status, Calculated_Churn_Risk, LTV_Index, Customer_Segment

**Tickets:** Ticket_ID, Customer_ID, Equipment_Model, Issue_Category, Resolution_Time_Hrs, Overall_Performance_Score, Performance_Tier, SLA_Met

**Logs:** Log_ID, Customer_ID, Program_Genre, Channel_Name, Total_Views, Total_View_Duration_Mins, Engagement_Score, Popularity_Tier, Content_Health

## 🔄 Data Refresh

The application uses Streamlit's caching with a 5-minute TTL (Time To Live):
- Data is cached automatically for 5 minutes
- Use the "🔄 Refresh Data" button in the sidebar to manually clear cache
- All filters and dashboard selections persist during cache duration

## 🛠️ Technology Stack

- **Streamlit** - Interactive web dashboard framework
- **Pandas** - Data manipulation and analysis
- **Plotly Express** - Interactive data visualization
- **NumPy** - Numerical computing
- **Faker** - Synthetic data generation
- **Python 3.13**

## 📋 Pipeline Details

### Customer Pipeline (process_customers.py)
Transforms customer data with:
- Service health scoring (weighted: availability, satisfaction, performance)
- Payment risk classification and LTV calculations
- Churn risk prediction (weighted: contract terms, support tickets, payment history)
- Customer segmentation (VIP, Standard, Budget)
- Device adoption and contract renewal indicators

### Tickets Pipeline (process_tickets.py)
Generates operations analytics with:
- Overall performance scoring (weighted: speed 25%, satisfaction 35%, FCR 25%, efficiency 15%)
- SLA compliance tracking
- Equipment reliability indexing
- Department efficiency metrics
- Issue impact assessment

### Logs Pipeline (process_logs.py)
Analyzes viewer engagement with:
- Engagement scoring (weighted: views 40%, duration 30%, rating 30%)
- Content popularity tier classification
- Genre strength indexing by device
- Content reach and ad opportunity scoring
- Quality satisfaction distribution analysis

## 📝 Notes

### Data Privacy
This project uses entirely synthetically generated data created with Faker. No real customer, operational, or business data is included.

### Performance Considerations
- Large datasets (11,950+ records) displayed with `st.dataframe()` which includes automatic scrolling
- Filters are applied server-side before display
- Caching enabled to minimize redundant data loads

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Minimum resolution: 1280x720 recommended for optimal dashboard view

## 🤝 Contributing

Suggestions and improvements welcome! Feel free to submit issues or pull requests.

## 📞 Support

For questions or issues:
1. Check existing GitHub issues
2. Review the code comments and docstrings
3. Ensure all dependencies are properly installed

## 📄 License

This project is open source and available under the MIT License.

## ✨ Highlights

- **Complete Analytics Stack**: From raw data generation through Gold-layer aggregation
- **Production-Ready Code**: 645-line main app with professional structure
- **Advanced Metrics**: 20+ sophisticated KPIs with multi-factor weighted scoring
- **Responsive Design**: Clean CSS styling with metric cards and color-coded indicators
- **Interactive Dashboards**: Seamless filtering across all four dashboard views
- **Scalable Architecture**: Medallion pattern supports easy extension and maintenance

---

**Created:** March 2026  
**Version:** 1.0  
**Status:** Production Ready ✅
