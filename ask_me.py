# ask_me.py

from flask import jsonify, request
import pandas as pd
import re

# Load dataset function
def load_dataset(file):
    """
    Load a CSV dataset from the 'dataset_csv' folder.
    """
    try:
        dataset_path = f"dataset_csv/{file}"
        df = pd.read_csv(dataset_path)
        return df
    except Exception as e:
        return {"error": f"Error loading dataset: {e}"}

# Function to process 'Ask Me' queries
def process_ask_me_query(query):
    patterns = {
        "sales_quantity": r"(sales quantity|quantity) of product (\d+)",
        "price": r"(price) of product (\d+)",
        "stock": r"(stock|inventory) level of product (\d+)"
    }

    for term, pattern in patterns.items():
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            product_id = match.group(2)
            return fetch_data_for_term(term, product_id)

    return {"error": f"Could not understand the query: {query}"}

# Function to fetch the requested data
def fetch_data_for_term(term, product_id):
    """
    Fetch data based on the term and product ID.
    """
    if term == "sales_quantity":
        df = load_dataset("demand_forecasting.csv")
        if "Product ID" in df.columns:
            result = df[df["Product ID"] == int(product_id)]["Sales Quantity"].sum()
            return {"sales_quantity": result}
    
    elif term == "price":
        df = load_dataset("pricing_optimization.csv")
        if "Product ID" in df.columns:
            result = df[df["Product ID"] == int(product_id)]["Price"].values[0]
            return {"price": result}
    
    elif term == "stock":
        df = load_dataset("inventory_monitoring.csv")
        if "Product ID" in df.columns:
            result = df[df["Product ID"] == int(product_id)]["Stock Levels"].sum()
            return {"stock_level": result}
    
    return {"error": "Product ID not found or data is missing."}

# API endpoint for 'Ask Me' queries
def ask_me_query_route(app):
    @app.route('/api/ask-me', methods=['GET'])
    def ask_me():
        query = request.args.get('query', "")
        if not query:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        
        result = process_ask_me_query(query)
        return jsonify(result)
