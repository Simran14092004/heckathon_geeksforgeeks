
from celery import Celery
from agents.demand_agent import get_demand_prediction
from agents.inventory_agent import get_inventory_status
from agents.pricing_agent import get_pricing_suggestion
from agents.coordination_agent import get_coordination_suggestions

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task(bind=True)
def run_agents(self):
    """Trigger all agents and return the results."""
    try:
        # Run demand agent
        demand_data = get_demand_prediction()
        
        # Run inventory agent
        inventory_data = get_inventory_status()
        
        # Run pricing agent
        pricing_data = get_pricing_suggestion()
        
        # Run coordination agent
        coordination_data = get_coordination_suggestions(demand_data, inventory_data, pricing_data)
        
        # Return combined results
        results = {
            "demand": demand_data,
            "inventory": inventory_data,
            "pricing": pricing_data,
            "coordination": coordination_data,
        }
        return results
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)