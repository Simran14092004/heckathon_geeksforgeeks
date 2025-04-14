from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, session
from flask_cors import CORS
import os
import logging
import pandas as pd
from utils.logger import setup_logger
from utils.celery_config import make_celery
import redis
from ask_me import ask_me_query_route
from load_data import load_dataset
from trigger import run_agents  # Import Celery task

# === Agents ===
from agents.demand_agent import get_demand_prediction
from agents.inventory_agent import get_inventory_status
from agents.pricing_agent import get_pricing_suggestion
from agents.coordination_agent import get_coordination_suggestions
from agents.supplier_agent import get_supplier_recommendation

# === Web-scraper ===
from web_scraper.scrape_data import scrape_latest_data

# === App Initialization ===
app = Flask(__name__, template_folder='dashboard', static_folder='dashboard')
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")  # Replace fallback in production!
celery = make_celery(app)
logger = setup_logger("main")

# Redis connection using environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# === Ask Me Route ===
ask_me_query_route(app)  # Includes "Ask Me" API

# === Health Check ===
@app.route('/health')
def health_check():
    return jsonify({"status": "Server is running"})


@app.route('/supplier.html')
def supplier_page():
    return render_template('supplier.html')

# === Contact Page ===
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        logger.info(f"Contact form submitted: Name={name}, Email={email}, Message={message}")
        return render_template('contact.html', success=True)
    return render_template('contact.html')

# === Auth Routes ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "admin":
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# === Main Page ===
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory('dashboard', 'index.html')


@app.route('/dashboard/<path:filename>')
def serve_dashboard_assets(filename):
    return send_from_directory('dashboard', filename)


# === Agent Routes ===
@app.route('/api/demand')
def demand_api():
    try:
        df = load_dataset('demand_forecasting.csv')
        result = get_demand_prediction(df)
        return jsonify({"demand_predictions": result})
    except Exception as e:
        logger.exception("Demand API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/inventory')
def inventory_api():
    try:
        df = load_dataset('inventory_monitoring.csv')
        inventory_data = get_inventory_status(df)
        return jsonify({"inventory_data": inventory_data.to_dict(orient="records")})
    except Exception as e:
        logger.exception("Inventory API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/pricing')
def pricing_api():
    try:
        df = load_dataset('pricing_optimization.csv')
        pricing_data = get_pricing_suggestion(df)
        return jsonify({"pricing_suggestions": pricing_data.to_dict(orient="records")})
    except Exception as e:
        logger.exception("Pricing API error")
        return jsonify({"error": str(e)}), 500


@app.route('/api/coordination', methods=['GET', 'POST'])
def coordination_api():
    try:
        # Load datasets
        demand_df = load_dataset('demand_forecasting.csv')
        inventory_df = load_dataset('inventory_monitoring.csv')
        pricing_df = load_dataset('pricing_optimization.csv')

        # Check for empty datasets
        if demand_df.empty or inventory_df.empty or pricing_df.empty:
            return jsonify({"error": "Missing or empty datasets"}), 400

        if request.method == 'POST':
            # Handle filtering logic for POST requests
            data = request.get_json()
            filter_count = data.get('filter', 10)  # Default to 10 products if no filter is provided

            # Generate coordination suggestions
            demand_pred = get_demand_prediction(demand_df)
            inventory_status = get_inventory_status(inventory_df)
            pricing_data = get_pricing_suggestion(pricing_df)
            coordination_results = get_coordination_suggestions(
                pd.DataFrame(demand_pred), inventory_status, pricing_data, filter_count
            )

            return jsonify({"filtered_products": coordination_results})

        # Default GET request handling (unchanged)
        demand_pred = get_demand_prediction(demand_df)
        inventory_status = get_inventory_status(inventory_df)
        pricing_data = get_pricing_suggestion(pricing_df)
        result = get_coordination_suggestions(pd.DataFrame(demand_pred), inventory_status, pricing_data)
        return jsonify({"coordination_suggestions": result})

    except Exception as e:
        logger.exception("Coordination API error")
        return jsonify({"error": f"Coordination API Error: {str(e)}"}), 500

@app.route('/api/scrape')
def scrape_api():
    try:
        result = scrape_latest_data()
        return jsonify(result)
    except Exception as e:
        logger.exception("Scrape API error")
        return jsonify({"error": str(e)}), 500


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

    except Exception as e:
        logger.exception("Supplier API error")
        return jsonify({"error": f"Supplier API Error: {str(e)}"}), 500


@app.route('/api/filter', methods=['POST'])
def filter_product():
    try:
        data = request.json
        if not data or 'product_id' not in data:
            raise ValueError("Product ID is required")

        product_id = data['product_id']
        inventory_data = load_dataset('inventory_monitoring.csv')

        filtered_product = inventory_data[inventory_data['Product ID'] == product_id]
        if filtered_product.empty:
            return jsonify({"message": "No product found with the given ID"}), 404

        return jsonify({"filtered_product": filtered_product.to_dict(orient='records')[0]})

    except Exception as e:
        logger.exception("Filter Product API error")
        return jsonify({"error": f"Filter Product API Error: {str(e)}"}), 500


# === Trigger Agents ===
@app.route('/api/trigger-agents', methods=['POST'])
def trigger_agents():
    task = run_agents.delay()  # Start Celery task
    return jsonify({"task_id": task.id}), 202


@app.route('/api/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = run_agents.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'result': task.result}
    else:
        response = {'state': task.state, 'error': str(task.info)}
    return jsonify(response)


# === App Start ===
if __name__ == '__main__':
    app.run(debug=True)