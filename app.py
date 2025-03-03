import streamlit as st
import pandas as pd
import requests

# Function to navigate through the app
def main():
    selected_box = st.sidebar.selectbox(
        "Choose any operation below",
        ("Welcome", "Single or Multiple Data Predictions", "Past Predictions Page"),
    )

    if selected_box == "Welcome":
        welcome()
    elif selected_box == "Single or Multiple Data Predictions":
        data_predict()
    elif selected_box == "Past Predictions Page":
        past_predict()

# Welcome Page
def welcome():
    st.title("AIR QUALITY PREDICTION")
    st.subheader("By Team RASI")
    st.write("Use the left sidebar to navigate through the app.")

# Prediction Page
def data_predict():
    st.title("Single or Multiple Data Predictions")

    value = st.selectbox("Select your option:", ["Single Sample Prediction", "Multiple Sample Prediction"])

    if value == "Single Sample Prediction":
        with st.form(key="single_sample_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                c1 = st.number_input("Temperature:", min_value=-50.0, max_value=50.0, step=0.1)
            with col2:
                c2 = st.number_input("Humidity (%):", min_value=0.0, max_value=100.0, step=0.1)
            with col3:
                c3 = st.number_input("PM2.5:", min_value=0.0, step=0.1)

            col4, col5, col6 = st.columns(3)
            with col4:
                c4 = st.number_input("PM10:", min_value=0.0, step=0.1)
            with col5:
                c5 = st.number_input("NO2:", min_value=0.0, step=0.1)
            with col6:
                c6 = st.number_input("SO2:", min_value=0.0, step=0.1)

            col7, col8, col9 = st.columns(3)
            with col7:
                c7 = st.number_input("CO:", min_value=0.0, step=0.01)
            with col8:
                c8 = st.number_input("Proximity to Industrial Areas:", min_value=0.0, step=0.1)
            with col9:
                c9 = st.number_input("Population Density:", min_value=0.0, step=1.0)

            submit_button = st.form_submit_button("Predict")

            if submit_button:
                input_data = {
                    "temperature": c1,
                    "humidity": c2,
                    "pm_25": c3,
                    "pm_10": c4,
                    "no2": c5,
                    "so2": c6,
                    "co": c7,
                    "proximity_level": c8,
                    "population_density": c9,
                }

                try:
                    response = requests.post("http://localhost:8000/predict", json=[input_data])
                    if response.status_code == 200:
                        prediction = response.json()[0]
                        df = pd.DataFrame([prediction['input']])
                        df["Air Quality"] = prediction["prediction"]
                        st.dataframe(df)
                    else:
                        st.error("Failed to fetch prediction!")
                except Exception as e:
                    st.error(f"Error: {e}")

    else:
        st.write("Upload a CSV file")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file:
            column_names = ['temperature', 'humidity', 'pm_25','pm_10','no2','so2','co','proximity_level','population_density']
            df = pd.read_csv(uploaded_file,names=column_names)
            st.write("CSV preview:", df.head())

            if st.button("Predict for CSV Data"):
                data_records = df.to_dict(orient="records")
                try:
                    response = requests.post("http://localhost:8000/predict", json=data_records)
                    if response.status_code == 200:
                        predictions = response.json()
                        df_input_list = []  
                        df_output_list = []  

                        for prediction in predictions:  
                            df_input = pd.json_normalize(prediction['input'], record_prefix='input_')  
                            df_output = pd.DataFrame({"air_quality": [prediction['prediction']]})  
                            df_input_list.append(df_input)  
                            df_output_list.append(df_output)  

                        # Concatenate all inputs and outputs into a single DataFrame  
                        df_combined_input = pd.concat(df_input_list, ignore_index=True)  
                        df_combined_output = pd.concat(df_output_list, ignore_index=True)  
                        
                        # Combine the input DataFrame with the prediction DataFrame  
                        df_final = pd.concat([df_combined_input, df_combined_output], axis=1) 
                        st.write("Here are the predictions based on your uploaded CSV:")  
                        st.dataframe(df_final)
                        # df_predictions = pd.DataFrame(predictions)
                        # st.dataframe(df_predictions)
                    else:
                        st.error("Failed to get predictions")
                except Exception as e:
                    st.error(f"Error: {e}")

# Past Predictions Page
def past_predict():
    st.title("Past Predictions Page")

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    source_options = ['Webapp', 'Scheduled Predictions', 'All']
    selected_source = st.selectbox("Prediction Source", source_options)

    if st.button("Get Predictions"):
        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "source": selected_source.lower()
        }
        try:
            response = requests.get("http://localhost:8000/past-predictions", params=params)
            if response.status_code == 200:
                predictions = response.json()
                if isinstance(predictions, list) and len(predictions) > 0:
                    st.dataframe(pd.DataFrame(predictions))
                else:
                    st.warning("No data available for the selected date range and source.")
                # st.dataframe(pd.DataFrame(predictions))
            else:
                st.error("Failed to retrieve predictions")
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()


