# import subprocess
# import json
# import pandas as pd

# def get_pricing_suggestion_phi(df: pd.DataFrame):
#     try:
#         pricing_json = df.to_json(orient='records')

#         # Create the prompt for Phi-2
#         prompt = f"""
# You are a pricing AI agent. Based on the pricing and competitor data, suggest optimal pricing adjustments for each product:
# 1. Suggest a price increase if competitor prices are lower.
# 2. Suggest a price decrease if competitor prices are higher.

# Return a list of suggested price adjustments in this format:
# [ {{ "product": "<Product Name>", "current_price": <Number>, "suggested_price": <Number>, "suggestion": "<Recommendation>" }} ]

# Pricing Data:
# {pricing_json}
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
#         print(f"Error in get_pricing_suggestion_phi: {e}")
#         return {"error": str(e)}


import pandas as pd
from utils.logger import setup_logger
from utils.phi_utils import run_phi_agent

logger = setup_logger("pricing_agent_phi")

def get_pricing_suggestion_phi(pricing_df: pd.DataFrame):
    try:
        if pricing_df.empty:
            return {"error": "Pricing data is empty"}

        required_cols = ['Product ID', 'Store ID', 'Price', 'Competitor Prices']
        if not all(col in pricing_df.columns for col in required_cols):
            return {"error": f"Missing required columns in pricing data. Required: {required_cols}"}

        pricing_json = pricing_df.to_json(orient='records')

        prompt = f"""
You are an AI pricing agent. Based on product pricing, competitor prices, and current sales prices, suggest optimal prices to maximize profit and stay competitive.

Return in this format:
[
    {{
        "Product ID": "<Product ID>",
        "Current Price": <float>,
        "Competitor Prices": <float>,
        "Suggested Price": <float>,
        "Reason": "<Explanation>"
    }},
    ...
]

Pricing Data:
{pricing_json}
        """

        return run_phi_agent(prompt)

    except Exception as e:
        logger.exception("Error in pricing_agent_phi")
        return {"error": str(e)}

