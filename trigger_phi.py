import requests
import time

# Trigger Agents
trigger_url = "http://localhost:5000/api/trigger-agents"
response = requests.post(trigger_url)
if response.status_code == 200:
    data = response.json()
    task_id = data.get("task_id")
    print(f"Agents triggered successfully! Task ID: {task_id}")
else:
    print(f"Error triggering agents: {response.text}")
    exit()

# Check Task Status
status_url = f"http://localhost:5000/api/task-status/{task_id}"
while True:
    status_response = requests.get(status_url)
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"Task Status: {status_data['state']}")
        if status_data["state"] == "SUCCESS":
            print(f"Task Result: {status_data['result']}")
            break
    else:
        print(f"Error fetching task status: {status_response.text}")
    time.sleep(5)  # Wait 5 seconds before checking again