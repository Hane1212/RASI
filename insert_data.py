from sqlalchemy.orm import Session

# Create a new session
session = SessionLocal()

# Create a new prediction
new_prediction = Prediction(
    input_features={"temperature": 25.0, "humidity": 60.0, "pm2_5": 12.0, "pm10": 20.0, "no2": 15.0, "so2": 5.0, "co": 0.5, "proximity": 1.0, "population_density": 1000},
    prediction=42.0
)

# Add the new prediction to the session and commit
session.add(new_prediction)
session.commit()

# Close the session
session.close()
Query the data: Add the following code to query the data and print it out:

# Create a new session
session = SessionLocal()

# Query the predictions table
predictions = session.query(Prediction).all()

# Print out the predictions
for prediction in predictions:
    print(prediction.prediction_id, prediction.input_features, prediction.prediction, prediction.timestamp)

# Close the session
session.close()