from flask import jsonify, request
import pandas as pd
import re
import numpy as np

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

    return {"error": f"Could not understand the query: '{query}'. Try something like 'What is the sales quantity of product 123?'."}

# Function to fetch the requested data
def fetch_data_for_term(term, product_id):
    try:
        df = load_dataset("demand_forecasting.csv")
        if term == "sales_quantity" and "Product ID" in df.columns:
            product_data = df[df["Product ID"] == int(product_id)]
            if not product_data.empty:
                # Convert to standard Python int
                return {"sales_quantity": int(product_data["Sales Quantity"].sum())}
            else:
                return {"error": f"No sales data found for product ID {product_id}."}

        # Implement other cases (price and stock)
        elif term == "price":
            # Add logic for price
            return {"error": "Price retrieval not implemented."}

        elif term == "stock":
            # Add logic for stock levels
            return {"error": "Stock retrieval not implemented."}

        else:
            return {"error": f"Unknown term: {term}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# API endpoint for 'Ask Me' queries
def ask_me_query_route(app):
    @app.route('/api/ask-me', methods=['GET'])
    def ask_me():
        query = request.args.get('query', "")
        if not query:
            return jsonify({"error": "Missing 'query' parameter. For example, try 'What is the price of product 123?'"}), 400
        
        result = process_ask_me_query(query)
        return jsonify(result)