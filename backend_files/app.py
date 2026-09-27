# app.py - Flask backend for SuperKart sales prediction

import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os

# Initialize Flask app
superkart_api = Flask("superkart_sales_prediction")

# Load the serialized model pipeline (preprocessing + trained regressor)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "superkart_model.joblib")
model = joblib.load(MODEL_PATH)

# The exact feature columns the model pipeline expects, in this order
FEATURE_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Simple health-check / welcome route."""
    return jsonify({"message": "SuperKart Sales Prediction API is up and running."})


@superkart_api.get("/health")
def health():
    """Health-check endpoint used to confirm the container is alive."""
    return jsonify({"status": "ok"})


@superkart_api.post("/v1/predict")
def predict():
    """
    Online (single-record) inference endpoint.
    Expects a JSON body with the 10 feature columns listed in FEATURE_COLUMNS.
    Returns the predicted Product_Store_Sales_Total.
    """
    try:
        payload = request.get_json(force=True)

        # Build a single-row DataFrame in the exact column order the pipeline expects
        input_df = pd.DataFrame([payload], columns=FEATURE_COLUMNS)

        prediction = model.predict(input_df)[0]

        return jsonify({"predicted_sales": round(float(prediction), 2)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@superkart_api.post("/v1/predictbatch")
def predict_batch():
    """
    Batch inference endpoint.
    Expects a multipart/form-data request with a CSV file under the key 'file'.
    The CSV must contain the 10 feature columns listed in FEATURE_COLUMNS.
    Returns a JSON object mapping row index -> predicted sales value.
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part named 'file' in the request."}), 400

        file = request.files["file"]
        batch_df = pd.read_csv(file)

        # Keep only expected columns, in the right order
        batch_df = batch_df[FEATURE_COLUMNS]

        predictions = model.predict(batch_df)

        result = {str(idx): round(float(pred), 2) for idx, pred in enumerate(predictions)}

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    # Port 7860 is used throughout this project (matches the Codespaces port forwarding setup)
    superkart_api.run(host="0.0.0.0", port=7860)
