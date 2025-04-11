# # utils/phi_utils.py
# import subprocess
# import json
# from utils.logger import setup_logger

# logger = setup_logger("phi_utils")

# def run_phi_agent(prompt: str):
#     try:
#         result = subprocess.run(
#             ["ollama", "run", "phi", prompt],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )

#         stdout = result.stdout.strip()
#         stderr = result.stderr.strip()

#         if stderr:
#             logger.error(f"Ollama stderr: {stderr}")
#             return {"error": f"Ollama Error: {stderr}"}

#         start = stdout.find("[")
#         end = stdout.rfind("]") + 1
#         if start != -1 and end != -1:
#             try:
#                 return json.loads(stdout[start:end])
#             except json.JSONDecodeError:
#                 logger.warning("Failed to parse JSON, returning raw output")
#                 return {"error": "Failed to parse JSON from Phi", "raw_output": stdout}
#         else:
#             return {"error": "Unexpected output format from Phi", "raw_output": stdout}

#     except Exception as e:
#         logger.exception("Error running Phi model")
#         return {"error": str(e)}


# utils/phi_utils.py
import requests

def run_phi_agent(prompt):
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "phi",  # or "phi-2" if that's what you pulled
                "prompt": prompt,
                "stream": False  # Important to disable streaming
            }
        )
        result = response.json()
        return result.get('response', 'No valid response from Phi AI.')
    except Exception as e:
        return f"Error contacting Phi AI: {str(e)}"