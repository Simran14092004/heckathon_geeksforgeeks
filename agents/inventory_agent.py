#inventory_agent.py

import pandas as pd

def get_inventory_status(df: pd.DataFrame):
    # Example processing (adapt to your logic)
    try:
        # Process your inventory data
        inventory = df[['Product ID', 'Store ID', 'Stock Levels', 'Reorder Point']]

        # If you need to apply any filters or business logic:
        low_stock_items = inventory[inventory['Stock Levels'] < inventory['Reorder Point']]

        return low_stock_items
    except Exception as e:
        print(f"Error in get_inventory_status: {e}")
        return None


