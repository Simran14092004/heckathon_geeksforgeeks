# import subprocess
# import json
# import pandas as pd

# def get_demand_prediction_phi(df: pd.DataFrame):
#     try:
#         # Select relevant columns for the demand prediction task
#         df = df[['Product ID', 'Date', 'Sales Quantity', 'Price', 'Promotions', 'Seasonality Factors', 
#                  'External Factors', 'Demand Trend', 'Customer Segments']]

#         # Convert the data to JSON format (compact format)
#         demand_json = df.to_json(orient='records')

#         # Create the prompt for Phi-2
#         prompt = f"""
# You are a demand forecasting AI agent. Based on the following product sales data, predict the demand for each product. 
# The data includes factors like promotions, seasonality, external factors, demand trends, and customer segments.

# Return a list of demand predictions in the following format:
# [ 
#     {{ "product": "<Product ID>", "predicted_demand": <Predicted Demand Number> }},
#     ...
# ]

# Sales Data:
# {demand_json}
#         """

#         # Running Phi-2 model via Ollama
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
#         print(f"Error in get_demand_prediction_phi: {e}")
#         return {"error": str(e)}


#=====to lower file path length====


# import subprocess
# import json

# def get_demand_prediction_phi(demand_df):
#     try:
#         # Convert the DataFrame to JSON string (compact format)
#         demand_json = demand_df.to_json(orient='records')

#         # === Prompt ===
#         prompt = f"""
# You are an AI agent predicting demand based on historical sales data.
# Here is the forecast data for demand:

# Demand Data:
# {demand_json}
#         """

#         # === Run Phi-2 using Ollama ===
#         result = subprocess.run(
#             ["ollama", "run", "phi", prompt],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )

#         # Capture the standard output and error
#         output = result.stdout.strip()
#         error_output = result.stderr.strip()

#         # If there was an error in the subprocess, log it
#         if error_output:
#             return {"error": f"Subprocess error: {error_output}"}

#         # Attempt to parse the JSON result
#         start_index = output.find("[")
#         end_index = output.rfind("]") + 1
#         if start_index != -1 and end_index != -1:
#             try:
#                 parsed_output = json.loads(output[start_index:end_index])
#                 return parsed_output
#             except json.JSONDecodeError:
#                 return {"error": "JSON parsing failed", "raw_output": output}
#         else:
#             return {"error": "Phi-2 output parsing failed", "raw_output": output}

#     except Exception as e:
#         return {"error": str(e)}

# agents/demand_agent_phi.py
import pandas as pd
from utils.logger import setup_logger
from utils.phi_utils import run_phi_agent

logger = setup_logger("demand_agent_phi")

def get_demand_prediction_phi(demand_df: pd.DataFrame):
    try:
        if demand_df.empty:
            logger.warning("Empty demand data")
            return {"error": "Demand data is empty"}

        if 'Product ID' not in demand_df.columns or 'Sales Quantity' not in demand_df.columns:
            return {"error": "Missing required columns in demand data"}

        demand_json = demand_df.to_json(orient='records')

        prompt = f"""
You are a demand forecasting AI. Based on the following data, predict future demand for each product.
Return a JSON list like this:
[
    {{
        "Product ID": "<Product ID>",
        "Predicted Demand": <float>
    }},
    ...
]

Demand Data:
{demand_json}
        """

        return run_phi_agent(prompt)

    except Exception as e:
        logger.exception("Demand prediction Phi agent error")
        return {"error": str(e)}
