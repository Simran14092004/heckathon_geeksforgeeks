# load_data.py

import os
import pandas as pd
import logging

DATASET_DIR = "dataset_csv"  # Specify your dataset directory

# Dataset loading function
def load_dataset(file):
    try:
        file_path = os.path.join(DATASET_DIR, file)
        print(f"[INFO] Loading file: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        df = pd.read_csv(file_path)
        print(f"[INFO] Loaded DataFrame:\n{df.head()}")
        return df
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        logging.error(f"File not found: {e}")
        return pd.DataFrame()  # Return an empty DataFrame
    except Exception as e:
        print(f"[ERROR] Could not load {file}: {e}")
        logging.error(f"Error loading dataset: {e}")
        return pd.DataFrame()  # Return an empty DataFrame