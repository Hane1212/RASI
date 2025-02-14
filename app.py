import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# API Base URL
API_URL = "http://localhost:8000"

# Streamlit UI
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Welcome", "Predict Air Quality", "View Past Predictions"])
    
    if page == "Welcome":
        welcome_page()
    elif page == "Predict Air Quality":
        prediction_page()
    elif page == "View Past Predictions":
        past_predictions_page()

def welcome_page():
    st.title("Welcome to the Air Quality Prediction App")
    st.write("This application allows you to predict air quality based on various environmental factors.\n\n")
    st.write("Use the sidebar to navigate between pages:")
    st.write("- **Predict Air Quality**: Make single or batch predictions using a trained model.")
    st.write("- **View Past Predictions**: Retrieve past air quality predictions based on date and source.")

def prediction_page():
    st.title("Predict Air Quality")
    option = st.radio("Choose Prediction Type", ["Single Entry", "Batch (CSV Upload)"])
    
    if option == "Single Entry":
        predict_single()
    else:
        predict_batch()

def predict_single():
    st.subheader("Single Sample Prediction")
    
    inputs = {}
    labels = ['Temperature', 'Humidity', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'Proximity to Industrial Areas', 'Population Density']
    keys = ['temperature', 'humidity', 'pm_25', 'pm_10', 'no2', 'so2', 'co', 'proximity_level', 'population_density']
    
    for key, label in zip(keys, labels):
        inputs[key] = st.number_input(label, value=None)
    
    if st.button("Predict"):
        response = requests.post(f"{API_URL}/predict", json=[inputs])
        if response.status_code == 200:
            prediction = response.json()
            df_result = pd.json_normalize(prediction[0])
            st.write("Prediction Result:")
            st.dataframe(df_result)
        else:
            st.error("Error fetching prediction")

def predict_batch():
    st.subheader("Batch Prediction via CSV Upload")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        if st.button("Predict for CSV Data"):
            response = requests.post(f"{API_URL}/predict", json=df.to_dict(orient="records"))
            if response.status_code == 200:
                predictions = response.json()
                df_result = pd.DataFrame(predictions)
                st.write("Predicted Air Quality:")
                st.dataframe(df_result)
            else:
                st.error("Error fetching batch predictions")

def past_predictions_page():
    st.title("View Past Predictions")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    source = st.selectbox("Prediction Source", ["Webapp", "Scheduled Predictions", "All"])
    
    if st.button("Retrieve Past Predictions"):
        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "source": source.lower()
        }
        
        response = requests.get(f"{API_URL}/past-predictions", params=params)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            st.dataframe(df)
        else:
            st.error("Error retrieving past predictions")

if __name__ == "__main__":
    main()
