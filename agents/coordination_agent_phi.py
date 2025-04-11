import pandas as pd
from utils.logger import setup_logger
from utils.phi_utils import run_phi_agent

logger = setup_logger("coordination_agent_phi")

def get_coordination_suggestions_phi(demand_df: pd.DataFrame, inventory_df: pd.DataFrame):
    try:
        if demand_df.empty or inventory_df.empty:
            return {"error": "One or both datasets are empty"}

        # Merge datasets on Product ID
        merged_df = pd.merge(demand_df, inventory_df, on='Product ID', how='inner')

        prompt_data = merged_df.to_json(orient='records')

        prompt = f"""
You are an AI coordination agent. Based on demand forecasts and inventory levels, suggest actions like restocking, price adjustments, or supplier orders.

Return in this format:
[
  {{
    "Product ID": "<Product ID>",
    "Forecasted Demand": <int>,
    "Current Stock": <int>,
    "Suggestion": "<Action to take>",
    "Reason": "<Reason>"
  }},
  ...
]

Data:
{prompt_data}
        """

        return run_phi_agent(prompt)

    except Exception as e:
        logger.exception("Coordination agent error")
        return {"error": str(e)}




