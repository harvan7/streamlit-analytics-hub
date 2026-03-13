
"""
Main orchestrator for DISH data pipeline.

This module coordinates the processing of three distinct data sources through
the Silver and Gold transformation layers:
- Customers: Processed via pipelines.process_customers module
- Service Tickets: Processed via pipelines.process_tickets module  
- Viewing Logs: Processed via pipelines.process_logs module

Each module is independently executable and creates both Silver and Gold layer outputs.
Data flows through defined paths:
  - Bronze: data/bronze_layer/
  - Solver (Silver): data/solver_layer/
  - Gold: data/gold_layer/
"""

from pipelines.process_customers import process_customers_silver, process_billing_gold
from pipelines.process_tickets import process_tickets_silver, process_network_operations_gold
from pipelines.process_logs import process_logs_silver, process_content_strategy_gold


def process_silver_layer():
    """
    Processes the Bronze layer data (raw CSVs) into the Silver layer.
    This involves cleaning, standardizing, and applying basic transformations
    to prepare the data for business analysis. The goal is to create a clean,
    consistent, and standardized version of the source data.
    
    Orchestrates:
    - Customer data processing
    - Service ticket data processing
    - Viewing log data processing
    """
    print("\n=== Processing Silver Layer ===")
    process_customers_silver()
    process_tickets_silver()
    process_logs_silver()
    print("Silver layer processing completed.")


def process_gold_layer():
    """
    Processes the Silver layer data into the Gold layer. This involves creating
    three thematic, aggregated tables designed for specific business dashboards,
    providing high-value, ready-to-use data for analysis.
    
    Orchestrates:
    - Billing segmentation (customers + tickets)
    - Content strategy (viewing logs aggregation)
    - Network operations (service ticket efficiency)
    """
    print("\n=== Processing Gold Layer ===")
    process_billing_gold()
    process_content_strategy_gold()
    process_network_operations_gold()
    print("Gold layer processing completed.")


if __name__ == "__main__":
    print("Starting DISH Data Solution pipeline...")
    process_silver_layer()
    process_gold_layer()
    print("\n✓ Silver and Gold layers processed successfully.")
