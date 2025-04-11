# coordination_agent.py
from utils.logger import setup_logger

logger = setup_logger("coordination_agent")

def get_coordination_suggestions(demand_data, inventory_data, pricing_data):
    coordination_suggestions = []
    for product in demand_data:
        product_id = product["product_id"]
        demand = product["predicted_demand"]
        inventory = next((item for item in inventory_data if item["product_id"] == product_id), None)
        pricing = next((item for item in pricing_data if item["product_id"] == product_id), None)

        if inventory and inventory["stock_levels"] < inventory["reorder_point"]:
            action = "Restock urgently" if demand > 100 else "Restock soon"
            coordination_suggestions.append({
                "product_id": product_id,
                "action": action,
                "reason": "High demand and low stock",
                "suggested_price": pricing["suggested_price"] if pricing else None
            })

    return coordination_suggestions

    
