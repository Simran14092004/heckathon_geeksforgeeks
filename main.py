# from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, session
# from flask_cors import CORS
# import os
# import logging
# import pandas as pd
# from utils.logger import setup_logger
# from utils.celery_config import make_celery
# import redis
# import requests
# import json

# from ask_me import ask_me_query_route
# from load_data import load_dataset

# # === Agents ===
# from agents.demand_agent import get_demand_prediction
# from agents.inventory_agent import get_inventory_status
# from agents.pricing_agent import get_pricing_suggestion
# from agents.coordination_agent import get_coordination_suggestions

# # === Phi-Agents ===
# from agents.demand_agent_phi import get_demand_prediction_phi
# from agents.inventory_agent_phi import get_inventory_status_phi
# from agents.pricing_agent_phi import get_pricing_suggestion_phi
# from agents.coordination_agent_phi import get_coordination_suggestions_phi

# # === Web-scraper ===
# from web_scraper.scrape_data import scrape_latest_data as scrape_latest_price

# # === Celery and Redis ===
# from trigger import run_agents
# from celery.result import AsyncResult

# # === App Initialization ===
# app = Flask(__name__, template_folder='dashboard', static_folder='dashboard')
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# # Use environment variables for sensitive configurations
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")  # Replace fallback in production!
# celery = make_celery(app)

# logger = setup_logger("main")

# # Redis connection using environment variables
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
# REDIS_DB = int(os.getenv("REDIS_DB", "0"))
# r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# # === Health Check ===
# @app.route('/health')
# def health_check():
#     return jsonify({"status": "Server is running"})


# # === Auth Routes ===
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         # Mock credentials — replace with DB check later
#         if username == "admin" and password == "admin":
#             session['logged_in'] = True
#             session['username'] = username
#             return redirect(url_for('index'))
#         else:
#             return render_template('login.html', error="Invalid username or password.")
    
#     return render_template('login.html')


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         # NOTE: Currently we just simulate signup success
#         # In production, save these in DB
#         session['logged_in'] = True
#         session['username'] = username
#         return redirect(url_for('index'))
    
#     return render_template('signup.html')


# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))


# # === Main Page ===
# @app.route('/')
# def index():
#     print("Session info:", session)
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))
#     return send_from_directory('dashboard', 'index.html')



# @app.route('/dashboard/<path:filename>')
# def serve_dashboard_assets(filename):
#     return send_from_directory('dashboard', filename)


# # === Agent Routes ===
# @app.route('/api/demand')
# def demand_api():
#     """
#     API to handle demand predictions.
#     """
#     try:
#         df = load_dataset('demand_forecasting.csv')
#         phi = request.args.get('phi', 'false').lower() == 'true'
#         result = get_demand_prediction_phi(df) if phi else get_demand_prediction(df)
#         return jsonify({"demand_predictions": result})
#     except Exception as e:
#         logger.exception("Demand API error")
#         return jsonify({"error": str(e)}), 500


# @app.route('/api/inventory')
# def inventory_api():
#     """
#     API to handle inventory data.
#     """
#     try:
#         # Load dataset
#         logger.info("Loading inventory dataset...")
#         df = load_dataset('inventory_monitoring.csv')
#         logger.info("Loaded Inventory DataFrame:\n%s", df.head())

#         # Convert DataFrame to JSON serializable format
#         inventory_data = df.to_dict(orient="records")
#         logger.info("Serialized inventory data: %s", inventory_data[:2])  # Log only the first two records for brevity

#         # Return as JSON response
#         return jsonify({"inventory_data": inventory_data})
#     except Exception as e:
#         logger.exception("Inventory API error")
#         return jsonify({"error": str(e)}), 500


# @app.route('/api/pricing')
# def pricing_api():
#     """
#     API to handle pricing suggestions.
#     """
#     try:
#         df = load_dataset('pricing_optimization.csv')
#         phi = request.args.get('phi', 'false').lower() == 'true'
#         result = get_pricing_suggestion_phi(df) if phi else get_pricing_suggestion(df)
#         return jsonify({"pricing_suggestions": result})
#     except Exception as e:
#         logger.exception("Pricing API error")
#         return jsonify({"error": str(e)}), 500


# @app.route('/api/coordination', methods=['POST'])
# def coordination_api():
#     """
#     API to handle coordination suggestions.
#     """
#     try:
#         data = request.json
#         demand_data = data.get('demand_data')
#         inventory_data = data.get('inventory_data')
#         pricing_data = data.get('pricing_data')
#         result = get_coordination_suggestions(demand_data, inventory_data, pricing_data)
#         return jsonify({"coordination_suggestions": result})
#     except Exception as e:
#         logger.exception("Coordination API error")
#         return jsonify({"error": str(e)}), 500



# def call_phi_ai(query):
#     """
#     Calls an external Phi-AI service for natural language processing.
#     """
#     try:
#         if not query:
#             return "Error: Empty query provided to Phi AI."

#         response = requests.post(
#             'http://localhost:11434/api/generate',
#             json={"model": "phi-2", "prompt": query},
#             timeout=10  # Wait up to 10 seconds for a response
#         )

#         if response.ok:
#             response_data = response.json()
#             return response_data.get('response', 'No valid response from Phi AI.')
#         else:
#             return f"Error: Phi AI returned status code {response.status_code}."

#     except requests.exceptions.Timeout:
#         return "Error: Phi AI request timed out. Please try again later."

#     except requests.exceptions.RequestException as e:
#         return f"Request failed: {str(e)}"


# # === Chat Integration ===
# @app.route('/api/chat', methods=['POST'])
# def chat():
#     """
#     API for natural language queries and responses.
#     """
#     try:
#         data = request.json
#         user_query = data.get('query')
#         use_phi = data.get('usePhi', False)

#         if not user_query:
#             return jsonify({"error": "Query is required"}), 400

#         if use_phi:
#             # Call the Phi agent for processing
#             response = call_phi_ai(user_query)
#             return jsonify({"response": response})

#         # Default logic for non-Phi queries
#         if "sales quantity" in user_query.lower():
#             return jsonify({"response": "The sales quantity for product 101 is 500 units."})
#         elif "price" in user_query.lower():
#             return jsonify({"response": "The price for product 202 is $20."})
#         elif "stock level" in user_query.lower():
#             return jsonify({"response": "The stock level for product 303 is 150 units."})
#         else:
#             return jsonify({"response": "Sorry, I didn't understand your question."})
#     except Exception as e:
#         logger.exception("Chat API error")
#         return jsonify({"error": str(e)}), 500


# # === App Start ===
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
import os
import logging
import pandas as pd

# === Agents ===
from agents.demand_agent import get_demand_prediction
from agents.inventory_agent import get_inventory_status
from agents.pricing_agent import get_pricing_suggestion

# === Phi-Agents ===
from agents.demand_agent_phi import get_demand_prediction_phi
from agents.inventory_agent_phi import get_inventory_status_phi
from agents.pricing_agent_phi import get_pricing_suggestion_phi
from agents.coordination_agent_phi import get_coordination_suggestions_phi

# === Web Scraper ===
from web_scraper.scrape_data import scrape_latest_data as scrape_latest_price

# === App Initialization ===
app = Flask(__name__, template_folder='dashboard', static_folder='dashboard')
CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'dataset_csv')

# === Dataset Loading Function ===
def load_dataset(file):
    try:
        file_path = os.path.join(DATASET_DIR, file)
        logger.info(f"[INFO] Loading file: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"[INFO] Loaded DataFrame:\n{df.head()}")
        return df
    except Exception as e:
        logger.error(f"[ERROR] Could not load {file}: {e}")
        return pd.DataFrame()

# === Health Check ===
@app.route('/health')
def health_check():
    return jsonify({"status": "Server is running"})

# === Frontend Routes ===
@app.route('/')
def index():
    return send_from_directory('dashboard', 'index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/dashboard/<path:filename>')
def serve_dashboard_assets(filename):
    return send_from_directory('dashboard', filename)

# === Generic Agent Handler ===
def agent_response(handler_phi, handler_normal, dataset_file):
    phi = request.args.get('phi', 'false').lower() == 'true'
    df = load_dataset(dataset_file)
    try:
        result = handler_phi(df) if phi else handler_normal(df)
        if isinstance(result, dict):
            return jsonify(result)
        elif hasattr(result, 'to_json'):
            return result.to_json(orient='records')
        elif result is None:
            return jsonify({"error": "Agent returned no result"}), 500
        else:
            return jsonify({"error": "Unexpected agent response format"}), 500
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return jsonify({"error": "Agent failed to process request."}), 500

# === Agent APIs ===
@app.route('/api/demand')
def demand_api():
    return agent_response(
        get_demand_prediction_phi,
        get_demand_prediction,
        'demand_forecasting.csv'
    )

@app.route('/api/inventory')
def inventory_api():
    return agent_response(
        get_inventory_status_phi,
        get_inventory_status,
        'inventory_monitoring.csv'
    )

@app.route('/api/pricing')
def pricing_api():
    return agent_response(
        get_pricing_suggestion_phi,
        get_pricing_suggestion,
        'pricing_optimization.csv'
    )

@app.route('/api/scrape')
def scrape_api():
    try:
        result = scrape_latest_price()
        logger.info(f"Scraped data: {result}")
        return jsonify({"scraped_data": result})
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return jsonify({"error": "Failed to scrape data."}), 500

@app.route('/api/coordination', methods=['POST'])
def coordination_api():
    phi = request.args.get('phi', 'false').lower() == 'true'
    demand_df = load_dataset('demand_forecasting.csv')
    inventory_df = load_dataset('inventory_monitoring.csv')

    try:
        if phi:
            result = get_coordination_suggestions_phi(demand_df, inventory_df)
            return jsonify({"coordination": result})
        else:
            demand_result = {row['Product ID']: row['Predicted Demand'] for row in get_demand_prediction(demand_df)}
            inventory_result = get_inventory_status(inventory_df).to_dict(orient='records')

            coordination_suggestions = []
            for item in inventory_result:
                product = item.get('Product ID')
                demand_value = demand_result.get(product, 0)
                if demand_value > 100:
                    coordination_suggestions.append({
                        "product": product,
                        "demand_forecast": demand_value,
                        "inventory_status": item,
                        "suggestion": "High demand + low stock — reorder suggested"
                    })
            return jsonify({"coordination": coordination_suggestions})
    except Exception as e:
        logger.error(f"Coordination error: {e}")
        return jsonify({"error": "Coordination agent failed."}), 500

if __name__ == "__main__":
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True)