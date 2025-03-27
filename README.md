# **Air Quality Index Analysis and Prediction System 🌍💨**

## **Team Members 👥**
- Revanth Puvaneswaren 
- Imthias Abubakkar
- Huang Ta
- Sravana Sakthidharan
- Anu Neduvely Ashokan

---

## **Project Overview 📋**
This project delivers a comprehensive system for analyzing and predicting Air Quality Index (AQI) metrics. It integrates modern tools and technologies to provide:  
- On-demand and scheduled AQI predictions.  
- A streamlined data pipeline.  
- Robust data validation and monitoring capabilities.  

The goal is to empower users with actionable insights while ensuring data integrity and system scalability.

---

## **System Architecture 🏗️**
The application consists of the following key components:

### **1. User Interface (Streamlit) 🖥️**  
   - Features:  
     - Real-time AQI predictions based on user inputs.  
     - Interactive visualization of historical predictions and used features.  

### **2. API Layer (FastAPI) 🔗**  
   - Responsibilities:  
     - Expose the machine learning model as a REST API.  
     - Store predictions (along with input features) in the database.  

### **3. SQL Database (PostgreSQL, SQLAlchemy) 📂**  
   - Purpose:  
     - Store historical predictions, features, and metadata for efficient querying and analysis.  

### **4. Scheduled Prediction Pipeline (Airflow) ⏱️**  
   - Features:  
     - Automates periodic prediction jobs.  
     - Ensures updated predictions are stored in the database.  

### **5. Data Ingestion and Validation (Great Expectations) ✅**  
   - Purpose:  
     - Ingest AQI datasets automatically.  
     - Validate datasets to detect missing values, anomalies, and other quality issues.  

### **6. Monitoring and Alerting Dashboard (Grafana) 📊**  
   - Features:  
     - Real-time visualization of data quality metrics.  
     - Detection and alerting for data drift issues between training and live datasets.  

---

Features and Highlights 🌟
1. End-to-End Data Pipeline 🔄
Seamlessly integrates all stages of data handling: ingestion, validation, storage, prediction, and monitoring.

Fully automated workflows ensure reliability and scalability.

2. Real-Time and On-Demand Predictions ⚡
Provides instant AQI predictions with user-provided input through an interactive Streamlit interface.

Offers historical analysis, enabling users to review and compare trends over time.

3. Scheduled Predictions ⏱️
Fully automated prediction jobs are executed at regular intervals using Airflow.

Ensures continuous updates for timely insights without manual intervention.

4. Advanced Data Quality Monitoring ✅
Employs robust validation frameworks (Great Expectations or TensorFlow Data Validation) to detect:

Missing or invalid data.

Structural anomalies or inconsistencies.

Guarantees trustworthy datasets for accurate predictions.

5. Drift Detection and Monitoring 📊
Tracks shifts between the distributions of training data and live serving data.

Alerts users to potential model performance degradation, ensuring proactive intervention.

6. Comprehensive Visualization Dashboards 📈
Intuitive Grafana dashboards for monitoring:

Data quality metrics in real time.

Data drift and other anomalies.

Customizable visualizations tailored to user needs.

7. Modular and Scalable Design 🏗️
Built with independent, reusable components to allow easy scaling and integration.

Ensures flexibility for adapting to future requirements or adding new features.

8. Streamlined Database Management 📂
Utilizes PostgreSQL with SQLAlchemy ORM for efficient and organized storage of:

Prediction history.

Input features and metadata.

Simplifies querying and retrieval of data for further analysis.
---

## **Dataset Description 📄**
The Air Quality Index dataset includes:  
- **Pollutant Concentrations**: Levels of PM2.5, PM10, CO, NO2, SO2, etc.  
- **AQI Scores**: Air quality levels based on pollutant measurements.  
- **Temporal Information**: Daily, monthly, or hourly data records for analysis.  

---

## **Installation and Setup ⚙️**

### **1. Clone the Repository 🛠️**
```bash
git clone https://github.com/imthias-abu/RASI.git
cd [project directory]
```

### **2. Install Dependencies 📦**
```bash
pip install -r requirements.txt
```

### **3. Configure the Environment 🌐**
- Set environment variables for database credentials, API keys, etc.

### **4. Set Up System Components 🗂️**
- **Airflow**: Follow the provided instructions to configure Airflow DAGs.  
- **Grafana**: Import pre-configured dashboards or customize your own.  
- **PostgreSQL**: Ensure the database is initialized and running.  

### **5. Launch the Application 🚀**
- Start the **Streamlit Interface**:  
  ```bash
  streamlit run app.py
  ```  
- Run **Airflow Scheduler and Worker**:  
  ```bash
  airflow scheduler
  airflow worker
  ```

---

## **Usage 👩‍💻**

### **1. On-Demand Predictions ⚡**
- Access the Streamlit app to:  
  - Input features for AQI predictions.  
  - Explore historical predictions and visualization of features.

### **2. Scheduled Predictions 🕒**
- Airflow automates prediction jobs at regular intervals.  
- Configure the interval in the Airflow DAG file.  

### **3. Monitoring 🔍**
- Use Grafana dashboards to:  
  - Track data quality metrics in real-time.  
  - Detect and analyze data drift.  

---

## **Contributing 🤝**
We welcome your contributions! Here’s how you can help:  
1. Fork this repository.  
2. Create a new branch for your changes.  
3. Submit a pull request for review.  

Feel free to report any bugs or propose new features via the **Issues** tab.

---

## **Contact Information 📧**
For questions, feedback, or support, reach out to us at:  
imthias-abubakkar.jamaludeen@epita.fr  

