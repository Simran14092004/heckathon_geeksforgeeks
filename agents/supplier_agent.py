# agents/supplier_agent.py
from utils.logger import setup_logger

logger = setup_logger("supplier_agent")

def get_supplier_recommendation(product_id, demand, lead_time_days=5):
    try:
        supplier_data = {
            "supplier": "XYZ Distributors",
            "lead_time_days": lead_time_days,
            "min_order_qty": 50,
            "cost_per_unit": 12.5
        }

        recommendation = {
            "product": product_id,
            "expected_demand": demand,
            "recommended_order_qty": max(supplier_data["min_order_qty"], int(demand * 1.2)),
            "supplier_details": supplier_data
        }

        return recommendation

    except Exception as e:
        logger.exception("Error in supplier recommendation")
        return {"error": str(e)}

