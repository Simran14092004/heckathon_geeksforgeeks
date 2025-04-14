# #trigger.py
# from celery import Celery
# from agents.demand_agent import get_demand_prediction
# from agents.inventory_agent import get_inventory_status
# from agents.pricing_agent import get_pricing_suggestion
# from agents.coordination_agent import get_coordination_suggestions

# celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# @celery_app.task(bind=True)
# def run_agents(self, phi_mode=False):
#     try:
#         if phi_mode:
#             from agents.demand_agent_phi import get_demand_prediction_phi as get_demand_prediction
#             from agents.inventory_agent_phi import get_inventory_status_phi as get_inventory_status
#             from agents.pricing_agent_phi import get_pricing_suggestion_phi as get_pricing_suggestion
#             from agents.coordination_agent_phi import get_coordination_suggestions_phi as get_coordination_suggestions
#         else:
#             from agents.demand_agent import get_demand_prediction
#             from agents.inventory_agent import get_inventory_status
#             from agents.pricing_agent import get_pricing_suggestion
#             from agents.coordination_agent import get_coordination_suggestions

#         demand_data = get_demand_prediction()
#         inventory_data = get_inventory_status()
#         pricing_data = get_pricing_suggestion()
#         coordination_data = get_coordination_suggestions(demand_data, inventory_data, pricing_data)

#         results = {
#             "phi_mode": phi_mode,
#             "demand": demand_data,
#             "inventory": inventory_data,
#             "pricing": pricing_data,
#             "coordination": coordination_data,
#         }

#         return results

#     except Exception as e:
#         raise self.retry(exc=e, countdown=60, max_retries=3)




# trigger.py
from celery import Celery
from agents.demand_agent import get_demand_prediction
from agents.inventory_agent import get_inventory_status
from agents.pricing_agent import get_pricing_suggestion
from agents.coordination_agent import get_coordination_suggestions
from load_data import load_dataset  # Import load_dataset

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task(bind=True)
def run_agents(self):
    try:
        demand_df = load_dataset('demand_forecasting.csv')
        inventory_df = load_dataset('inventory_monitoring.csv')
        pricing_df = load_dataset('pricing_optimization.csv')

        if demand_df.empty or inventory_df.empty or pricing_df.empty:
            return {"error": "One or more datasets could not be loaded."}

        demand_data = get_demand_prediction(demand_df)
        inventory_data = get_inventory_status(inventory_df)
        pricing_data = get_pricing_suggestion(pricing_df)
        coordination_data = get_coordination_suggestions(demand_data, inventory_data, pricing_data)

        results = {
            "demand": demand_data,
            "inventory": inventory_data,
            "pricing": pricing_data,
            "coordination": coordination_data,
        }

        return results

    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
