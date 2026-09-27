# app.py - Streamlit frontend for SuperKart sales prediction

import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="SuperKart Sales Predictor", layout="centered")

# The backend Flask container is reached by its service name on the shared
# Docker network (see docker network / docker run instructions). This can be
# overridden with an environment variable when running locally.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://superkart-backend:7860")

st.title("🛒 SuperKart Sales Forecasting")
st.write(
    "Predict the expected total sales revenue for a product at a given store, "
    "either one record at a time or in bulk from a CSV file."
)

tab_single, tab_batch = st.tabs(["🔹 Single Prediction", "📄 Batch Prediction"])

# ---------------------------------------------------------------------------
# Single (online) prediction
# ---------------------------------------------------------------------------
with tab_single:
    st.subheader("Enter product and store details")

    col1, col2 = st.columns(2)

    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66, step=0.1)
        product_sugar_content = st.selectbox(
            "Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"]
        )
        product_allocated_area = st.number_input(
            "Product Allocated Area", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f"
        )
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08, step=0.1)
        product_id_char = st.selectbox("Product Id Prefix", ["FD", "DR", "NC"])

    with col2:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox(
            "Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"]
        )
        store_type = st.selectbox(
            "Store Type",
            ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"],
        )
        store_age_years = st.number_input("Store Age (Years)", min_value=0, value=16, step=1)
        product_type_category = st.selectbox(
            "Product Type Category", ["Perishables", "Non Perishables"]
        )

    if st.button("Predict Sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category,
        }

        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Predicted Total Sales: **{result['predicted_sales']}**")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend API: {e}")

# ---------------------------------------------------------------------------
# Batch prediction
# ---------------------------------------------------------------------------
with tab_batch:
    st.subheader("Upload a CSV file for batch prediction")
    st.caption(
        "The CSV must contain the columns: Product_Weight, Product_Sugar_Content, "
        "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, "
        "Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category"
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        preview_df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(preview_df.head())

        if st.button("Run Batch Prediction"):
            uploaded_file.seek(0)
            files = {"file": uploaded_file.getvalue()}
            try:
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=60)
                if response.status_code == 200:
                    predictions = response.json()
                    pred_series = pd.Series(predictions, name="Predicted_Sales")
                    pred_series.index = pred_series.index.astype(int)
                    pred_series = pred_series.sort_index()

                    results_df = preview_df.copy()
                    results_df["Predicted_Sales"] = pred_series.values

                    st.write("Predictions:")
                    st.dataframe(results_df)

                    csv_out = results_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download predictions as CSV",
                        data=csv_out,
                        file_name="superkart_predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"API error ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend API: {e}")
