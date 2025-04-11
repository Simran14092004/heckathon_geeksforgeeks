from flask import Flask, jsonify, request
from flask_talisman import Talisman
from utils.celery_config import make_celery
from functools import wraps
import logging
import pandas as pd
from load_data import load_dataset
from utils.logger import setup_logger
from utils.phi_utils import run_phi_agent

# Standard agents
from agents.demand_agent import get_demand_prediction
from agents.inventory_agent import get_inventory_status
from agents.pricing_agent import get_pricing_suggestion
from agents.supplier_agent import get_supplier_recommendations
from agents.customer_agent import get_customer_product_insights
from agents.coordination_agent import get_coordination_suggestions

# Phi agents
from agents.demand_agent_phi import get_demand_prediction_phi
from agents.inventory_agent_phi import get_inventory_status_phi
from agents.pricing_agent_phi import get_pricing_suggestion_phi
from agents.coordination_agent_phi import get_coordination_suggestions_phi

# Flask app initialization
app = Flask(__name__)
Talisman(app)
logger = setup_logger("api_server")

# Set up Celery
celery = make_celery(app)

# 🔐 API Key Middleware
API_KEY = "your-secure-api-key"

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
        phi = request.args.get('phi', 'false').lower() == 'true'
        result = get_demand_prediction_phi(df) if phi else get_demand_prediction(df)
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
        phi = request.args.get('phi', 'false').lower() == 'true'
        result = get_inventory_status_phi(df) if phi else get_inventory_status(df)
        low_stock_items = result if phi else result.to_dict(orient='records')
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
        phi = request.args.get('phi', 'false').lower() == 'true'
        result = get_pricing_suggestion_phi(df) if phi else get_pricing_suggestion(df)
        return jsonify({"pricing_suggestion": result})
    except Exception as e:
        logger.exception("Pricing API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/coordination')
@require_api_key
def coordination_api():
    try:
        demand_df = load_dataset('demand_forecasting.csv')
        inventory_df = load_dataset('inventory_monitoring.csv')
        if demand_df.empty or inventory_df.empty:
            return jsonify({"error": "Missing or empty datasets"}), 400
        phi = request.args.get('phi', 'false').lower() == 'true'
        if phi:
            result = get_coordination_suggestions_phi(demand_df, inventory_df)
        else:
            demand_pred = get_demand_prediction(demand_df)
            inventory_status = get_inventory_status(inventory_df)
            result = get_coordination_suggestions(pd.DataFrame(demand_pred), inventory_status)
        return jsonify({"coordination_suggestions": result})
    except Exception as e:
        logger.exception("Coordination API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/supplier-recommendations')
@require_api_key
def supplier_api():
    try:
        df = load_dataset('inventory_monitoring.csv')
        low_stock_df = df[df['Stock Levels'] < df['Reorder Point']]
        result = get_supplier_recommendations(low_stock_df)
        return jsonify(result)
    except Exception as e:
        logger.exception("Supplier API error")
        return jsonify({"error": str(e)}), 500


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


@app.route('/api/chat', methods=['POST'])
@require_api_key
def chat_with_phi():
    try:
        data = request.get_json()
        query = data.get("query", "")
        if not query:
            return jsonify({"error": "Missing user query"}), 400

        # Load all 3 datasets
        demand_df = load_dataset('demand_forecasting.csv')
        inventory_df = load_dataset('inventory_monitoring.csv')
        pricing_df = load_dataset('pricing_optimization.csv')

        context = f"""
Demand Forecasting Data:
{demand_df.to_json(orient='records')}

Inventory Monitoring Data:
{inventory_df.to_json(orient='records')}

Pricing Optimization Data:
{pricing_df.to_json(orient='records')}
        """

        full_prompt = f"""
You are a smart retail assistant AI chatbot.
Answer the user query based on the provided data context.

User Question:
{query}

Relevant Data:
{context}
        """

        response = run_phi_agent(full_prompt)
        return jsonify({"response": response})
    except Exception as e:
        logger.exception("Chat API error")
        return jsonify({"error": str(e)}), 500


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
