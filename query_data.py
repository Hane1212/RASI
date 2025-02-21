# query_data.py
from models import SessionLocal, Prediction

# Create a new session
session = SessionLocal()

# Query the predictions table
predictions = session.query(Prediction).all()

# Print out the predictions
for prediction in predictions:
    print(prediction.prediction_id, prediction.input_features, prediction.prediction, prediction.timestamp)

# Close the session
session.close()