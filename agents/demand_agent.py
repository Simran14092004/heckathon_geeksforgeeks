# def get_demand_prediction(df):
#     # Ensure the dataframe has the necessary columns
#     if 'Product ID' not in df or 'Sales Quantity' not in df:
#         return {"error": "Required columns are missing in the dataset"}

#     # Sort the dataframe by 'Sales Quantity' (which represents demand)
#     sorted_df = df.sort_values(by='Sales Quantity', ascending=False)

#     # Create a dictionary of Product IDs and their corresponding sales quantity (demand)
#     demand_dict = dict(zip(sorted_df['Product ID'], sorted_df['Sales Quantity']))

#     return demand_dict
# agents/demand_agent.py
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from utils.logger import setup_logger

logger = setup_logger("demand_agent")

def get_demand_prediction(df: pd.DataFrame):
    try:
        required_columns = ['Product ID', 'Sales Quantity', 'Store ID']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing column: {col}")
                return {"error": f"Required column '{col}' is missing"}

        if df.empty:
            logger.warning("Empty dataset received in demand agent")
            return {"error": "Dataset is empty"}

        # Basic preprocessing
        df['Product ID'] = df['Product ID'].astype('category').cat.codes
        df['Store ID'] = df['Store ID'].astype('category').cat.codes

        X = df[['Product ID', 'Store ID']]
        y = df['Sales Quantity']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        logger.info(f"Demand prediction model trained. MSE: {mse:.2f}")

        df['Predicted Demand'] = model.predict(X)

        return df[['Product ID', 'Store ID', 'Predicted Demand']].to_dict(orient='records')

    except Exception as e:
        logger.exception("Failed in get_demand_prediction")
        return {"error": f"Unexpected error in demand agent: {str(e)}"}
