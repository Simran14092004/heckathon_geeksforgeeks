from flask import Flask, jsonify, request
from flask_talisman import Talisman
from utils.celery_config import make_celery
from functools import wraps
import logging
import pandas as pd
from load_data import load_dataset
from utils.logger import setup_logger
import os

#ask_me tab:
from ask_me import process_ask_me_query  

# Standard agents
from agents.demand_agent import get_demand_prediction
from agents.inventory_agent import get_inventory_status
from agents.pricing_agent import get_pricing_suggestion
from agents.supplier_agent import get_supplier_recommendation
from agents.customer_agent import get_customer_product_insights
from agents.coordination_agent import get_coordination_suggestions

# Flask app initialization
app = Flask(__name__)
Talisman(app)
logger = setup_logger("api_server")

# Set up Celery
celery = make_celery(app)

# API Key Middleware
from dotenv import load_dotenv
load_dotenv("api.env")
API_KEY = os.getenv("API_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("X-API-KEY") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ===================== Celery Task =====================

@celery.task(bind=True)
def long_running_task(self, data):
    """ Simulate a long-running task (e.g., data processing, API scraping) """
    try:
        import time
        time.sleep(10)  # Simulating task
        return f"Task completed with data: {data}"
    except Exception as e:
        raise self.retry(exc=e)

# ===================== API ROUTES =====================

@app.route('/api/demand')
@require_api_key
def demand_api():
    try:
        df = load_dataset('demand_forecasting.csv')
        if df.empty:
            return jsonify({"error": "No demand data found"}), 500
        result = get_demand_prediction(df)
        return jsonify(result)
    except Exception as e:
        logger.exception("Demand API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/inventory')
@require_api_key
def inventory_api():
    try:
        df = load_dataset('inventory_monitoring.csv')
        if df.empty:
            return jsonify({"error": "No inventory data found"}), 500
        result = get_inventory_status(df)
        low_stock_items = result.to_dict(orient='records')
        return jsonify({"low_stock_items": low_stock_items})
    except Exception as e:
        logger.exception("Inventory API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/pricing')
@require_api_key
def pricing_api():
    try:
        df = load_dataset('pricing_optimization.csv')
        if df.empty:
            return jsonify({"error": "No pricing data found"}), 500
        result = get_pricing_suggestion(df)
        return jsonify({"pricing_suggestion": result})
    except Exception as e:
        logger.exception("Pricing API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/coordination', methods=['GET', 'POST'])
@require_api_key
def coordination_api():
    try:
        # Load datasets
        demand_df = load_dataset('demand_forecasting.csv')
        inventory_df = load_dataset('inventory_monitoring.csv')

        # Check for empty datasets
        if demand_df.empty or inventory_df.empty:
            return jsonify({"error": "Missing or empty datasets"}), 400

        if request.method == 'POST':
            # Handle filtering logic for POST requests
            data = request.get_json()
            filter_count = data.get('filter', 10)  # Default to 10 products if no filter is provided

            # Generate coordination suggestions
            demand_pred = get_demand_prediction(demand_df)
            inventory_status = get_inventory_status(inventory_df)
            coordination_results = get_coordination_suggestions(
                pd.DataFrame(demand_pred), inventory_status
            )

            # Sort results based on some criteria (e.g., demand) and filter top N
            filtered_results = sorted(
                coordination_results, key=lambda x: x.get('demand', 0), reverse=True
            )[:int(filter_count)]

            return jsonify({"filtered_products": filtered_results})

        # Default GET request handling (unchanged)
        demand_pred = get_demand_prediction(demand_df)
        inventory_status = get_inventory_status(inventory_df)
        result = get_coordination_suggestions(pd.DataFrame(demand_pred), inventory_status)
        return jsonify({"coordination_suggestions": result})

    except Exception as e:
        logger.exception("Coordination API error")
        return jsonify({"error": f"Coordination API Error: {str(e)}"}), 500


@app.route('/api/supplier', methods=['GET', 'POST'])
def supplier_api():
    try:
        if request.method == 'POST':
            # Handle specific recommendation based on product_id and demand
            data = request.json
            if not data:
                raise ValueError("Request body is missing")

            product_id = data.get("product_id")
            demand = data.get("demand")
            if not product_id or demand is None:
                raise ValueError("Both 'product_id' and 'demand' are required")

            recommendation = get_supplier_recommendation(product_id, demand)
            return jsonify({"supplier_recommendation": recommendation})

        elif request.method == 'GET':
            # Handle general recommendations for low-stock products
            inventory_data = load_dataset('inventory_monitoring.csv')
            if inventory_data.empty:
                raise ValueError("Inventory dataset is missing or empty")

            low_stock_df = inventory_data[inventory_data['Stock Levels'] < inventory_data['Reorder Point']]
            if low_stock_df.empty:
                return jsonify({"message": "No low-stock products found"})

            recommendations = []
            for _, row in low_stock_df.iterrows():
                recommendation = get_supplier_recommendation(
                    product_id=row['Product ID'],
                    demand=row['Stock Levels'],
                    lead_time_days=row.get('Lead Time', 5)  # Use default lead time if not available
                )
                recommendations.append(recommendation)

            return jsonify({"supplier_recommendations": recommendations})

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.exception("Supplier API error")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/customer-query')
@require_api_key
def customer_query():
    try:
        product = request.args.get('product')
        if not product:
            return jsonify({"error": "Missing 'product' query param"}), 400
        df = load_dataset('demand_forecasting.csv')
        result = get_customer_product_insights(df, product)
        return jsonify(result)
    except Exception as e:
        logger.exception("Customer query error")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask-me', methods=['GET'])
@require_api_key
def ask_me():
    try:
        query = request.args.get('query', "")
        if not query:
            return jsonify({"error": "Missing 'query' parameter. For example, try 'What is the price of product 123?'"}), 400

        result = process_ask_me_query(query)
        return jsonify(result)
    except Exception as e:
        logger.exception("Ask Me API error")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500



@app.route('/api/async-chat', methods=['POST'])
def chat_async():
    data = request.get_json()
    query = data.get("query", "")

    # Call the long-running task with Celery
    task = long_running_task.apply_async(args=[query])
    return jsonify({"task_id": task.id})


@app.route('/api/task-status/<task_id>')
def get_status(task_id):
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id)
    return jsonify({"state": task_result.state, "result": task_result.result})

# ===================== START SERVER =====================
if __name__ == '__main__':
    app.run(debug=True)