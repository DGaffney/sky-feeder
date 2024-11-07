import os
import numpy as np
import xgboost as xgb
from server.algos.manifest import ALGO_MANIFEST, find_relevant_conditions
MODELS = {}


# Load all models from the models/ directory
models_path = "models/"
for rule in find_relevant_conditions(ALGO_MANIFEST, "probability"):
    model_dir = os.path.join(models_path, rule["model_name"])
    if os.path.isdir(model_dir):
        model = xgb.Booster()
        model.load_model(os.path.join(model_dir, "model.json"))
        MODELS[rule["model_name"]] = model

def operator(record, model_name, threshold):
    """
    Custom operator to evaluate model probability and compare it to a threshold.
    
    Args:
        record (dict): The record containing features for the model input.
        model_name (str): The name of the model to use for prediction.
        threshold (float): The threshold for probability comparison.

    Returns:
        bool: True if the predicted probability is above the threshold, otherwise False.
    """
    # Check if model_name exists in the loaded models
    if model_name not in MODELS:
        raise ValueError(f"Model '{model_name}' not found in the loaded models.")

    # Retrieve the model
    model = MODELS[model_name]

    # Extract features from the record and convert to DMatrix
    features = record.get("features")
    if features is None:
        raise ValueError("No features found in the record.")
    
    dmatrix = xgb.DMatrix(np.array([features]))
    
    # Get the probability prediction
    probability = model.predict(dmatrix)[0]
    
    # Return True if the probability is above the threshold, else False
    return probability > threshold
