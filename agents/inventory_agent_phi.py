# import subprocess
# import json
# import pandas as pd

# def get_inventory_status_phi(df: pd.DataFrame):
#     try:
#         inventory_json = df.to_json(orient='records')

#         # Create the prompt for Phi-2
#         prompt = f"""
# You are a supply chain AI agent. Based on the inventory status, identify products that:
# 1. Are low in stock (stock < reorder point).
# 2. Need to be reordered.

# Return a list of such product insights in the following format:
# [ {{ "product": "<Product Name>", "stock_level": <Number>, "suggestion": "<Recommendation>" }} ]

# Inventory Status Data:
# {inventory_json}
#         """

#         # Running the Phi-2 model via Ollama
#         result = subprocess.run(
#             ["ollama", "run", "phi", prompt],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )

#         output = result.stdout.strip()

#         # Parse the Phi-2 output
#         start_index = output.find("[")
#         end_index = output.rfind("]") + 1
#         if start_index != -1 and end_index != -1:
#             parsed_output = json.loads(output[start_index:end_index])
#             return parsed_output
#         else:
#             return {"error": "Phi-2 output parsing failed", "raw_output": output}

#     except Exception as e:
#         print(f"Error in get_inventory_status_phi: {e}")
#         return {"error": str(e)}



# agents/inventory_agent_phi.py

import pandas as pd
from utils.logger import setup_logger
from utils.phi_utils import run_phi_agent

logger = setup_logger("inventory_agent_phi")

def get_inventory_status_phi(inventory_df: pd.DataFrame):
    try:
        if inventory_df.empty:
            return {"error": "Inventory data is empty"}

        required_cols = ['Product ID', 'Stock Levels', 'Reorder Point']
        if not all(col in inventory_df.columns for col in required_cols):
            return {"error": f"Missing required columns in inventory data. Required: {required_cols}"}

        inventory_json = inventory_df.to_json(orient='records')

        prompt = f"""
You are an AI agent for analyzing inventory levels. Based on the following inventory data, identify which products are low in stock (stock < reorder point). 

Return this JSON format:
[
    {{
        "Product ID": "<Product ID>",
        "Stock Levels": <int>,
        "Reorder Point": <int>,
        "Status": "Low Stock" or "Sufficient"
    }},
    ...
]

Inventory Data:
{inventory_json}
        """

        return run_phi_agent(prompt)

    except Exception as e:
        logger.exception("Error in inventory_agent_phi")
        return {"error": str(e)}
