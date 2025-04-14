# # coordination_agent.py
# from utils.logger import setup_logger

# logger = setup_logger("coordination_agent")

# def get_coordination_suggestions(demand_data, inventory_data, pricing_data):
#     suggestions = []
#     for product in demand_data:
#         pid = product.get("Product ID") or product.get("product_id")
#         demand = product.get("Predicted Demand") or product.get("predicted_demand")

#         inventory = next((i for i in inventory_data if i.get("Product ID") == pid or i.get("product_id") == pid), None)
#         pricing = next((p for p in pricing_data if p.get("Product ID") == pid or p.get("product_id") == pid), None)

#         if inventory and inventory.get("Stock Levels", 0) < inventory.get("Reorder Point", 0):
#             urgency = "Restock urgently" if demand > 100 else "Restock soon"
#             suggestions.append({
#                 "Product ID": pid,
#                 "Action": urgency,
#                 "Reason": "High demand and low stock",
#                 "Suggested Price": pricing.get("Suggested Price") if pricing else None
#             })

#     return suggestions
# agents/coordination_agent.py
# coordination_agent.py
import pandas as pd

def get_coordination_suggestions(demand_data, inventory_data, pricing_data, filter_count=None):
    """
    Generate coordination suggestions based on demand, inventory, and pricing data.
    """
    try:
        # Ensure all required columns exist
        required_columns = ['Product ID']
        for df, name in [(demand_data, "Demand"), (inventory_data, "Inventory"), (pricing_data, "Pricing")]:
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing column '{col}' in {name} data")

        # Merge datasets
        merged_data = pd.merge(demand_data, inventory_data, on='Product ID', how='inner')
        merged_data = pd.merge(merged_data, pricing_data, on='Product ID', how='inner')

        # Apply filter if specified
        if filter_count:
            filter_count = int(filter_count)
            if 'Sales Quantity' in merged_data.columns:
                result = merged_data.nlargest(filter_count, 'Sales Quantity').to_dict(orient='records')
            else:
                raise ValueError("Column 'Sales Quantity' is missing for filtering")
        else:
            result = merged_data.to_dict(orient='records')

        return result

    except Exception as e:
        # Enhanced error logging
        return {"error": f"Coordination Suggestions Error: {str(e)}"}
  







