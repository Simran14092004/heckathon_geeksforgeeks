#customer_agent.py
import pandas as pd

def get_customer_product_insights(df: pd.DataFrame, product_query: str):
    product_query = product_query.lower()

    # Filter products matching query
    filtered = df[df['Product ID'].str.lower().str.contains(product_query)]
    if filtered.empty:
        return {"message": "No matching products found."}
    return filtered.to_dict(orient="records")
