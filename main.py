from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import datetime
from typing import List
from models import Prediction, Base
import pandas as pd
import joblib

DATABASE_URL = "postgresql+asyncpg://postgres:test1234!@localhost:5432/predictions"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

async def get_db():
    async with async_session() as session:
        yield session

try:
    model = joblib.load("./model.pkl")
except Exception as e:
    print(f"Model loading failed: {e}")
    model = None

@app.post("/predict")
async def predict(inputs: list[dict], db: AsyncSession = Depends(get_db)):
    df = pd.DataFrame(inputs)
    predictions = model.predict(df)

    actual_labels = ["Good", "Hazardous", "Moderate", "Poor"]
    results = []  
    for input_data, pred in zip(inputs, predictions):  
        prediction_label = actual_labels[int(pred)]  
        timestamp = datetime.utcnow() 

        results.append({"input": input_data, "prediction": prediction_label}) #, "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')})

        # Save to database  
        new_prediction = Prediction(
            temperature=input_data['temperature'],  
            humidity=input_data['humidity'],  
            pm_25=input_data['pm_25'],  
            pm_10=input_data['pm_10'],  
            no2=input_data['no2'],  
            so2=input_data['so2'],  
            co=input_data['co'],  
            proximity_level=input_data['proximity_level'],  
            population_density=input_data['population_density'],  
            prediction=prediction_label,  
            timestamp=timestamp,  
            source="webapp" 
        )  
        db.add(new_prediction)
    # results = [{"input": inp, "prediction": actual_labels[int(pred)]} for inp, pred in zip(inputs, predictions)]
    
    # for inp, pred in zip(inputs, predictions):
    #     db.add(Prediction(**inp, prediction=actual_labels[int(pred)]))
    await db.commit()

    return results

@app.get("/past-predictions")
async def get_past_predictions(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    source: str = Query("all", description="Prediction source (webapp, scheduled, or all)"),
    db: AsyncSession = Depends(get_db)
):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        query = select(Prediction).where(Prediction.timestamp.between(start_dt, end_dt))
        
        if source.lower() != "all":
            query = query.where(Prediction.source == source.lower())
        
        result = await db.execute(query)
        records = result.scalars().all()
        if not records:
            return {"message": "No data available for the selected date range and source."}

        
        return [
            {
                # "id": record.id,
                "temperature": record.temperature,
                "humidity": record.humidity,
                "pm_25": record.pm_25,
                "pm_10": record.pm_10,
                "no2": record.no2,
                "so2": record.so2,
                "co": record.co,
                "proximity_level": record.proximity_level,
                "population_density": record.population_density,
                "prediction": record.prediction,
                # "timestamp": record.timestamp,
                # "source": record.source,
            }
            for record in records
        ]
    except Exception as e:
        return {"error": str(e)}

# from fastapi import FastAPI, Depends, Query
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.future import select
# from datetime import datetime
# from typing import List
# from models import Prediction, Base
# import pandas as pd
# import joblib

# DATABASE_URL = "postgresql+asyncpg://postgres:test1234!@localhost:5432/preds"

# engine = create_async_engine(DATABASE_URL, echo=False)
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# app = FastAPI()

# async def get_db():
#     async with async_session() as session:
#         yield session

# try:
#     model = joblib.load("./model.pkl")
# except Exception as e:
#     print(f"Model loading failed: {e}")
#     model = None

# @app.post("/predict")
# async def predict(inputs: List[dict], db: AsyncSession = Depends(get_db)):
#     if not model:
#         return {"error": "Model is not loaded properly."}

#     df = pd.DataFrame(inputs)
#     predictions = model.predict(df)

#     actual_labels = ["Good", "Hazardous", "Moderate", "Poor"]
#     results = []

#     for input_data, pred in zip(inputs, predictions):  
#         prediction_label = actual_labels[int(pred)]  
#         timestamp = datetime.utcnow()  # ✅ Store UTC timestamp

#         results.append({
#             "input": input_data,
#             "prediction": prediction_label,
#             "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')
#         })

#         # ✅ Save prediction with timestamp
#         new_prediction = Prediction(
#             temperature=input_data['temperature'],
#             humidity=input_data['humidity'],
#             pm_25=input_data['pm_25'],
#             pm_10=input_data['pm_10'],
#             no2=input_data['no2'],
#             so2=input_data['so2'],
#             co=input_data['co'],
#             proximity_level=input_data['proximity_level'],
#             population_density=input_data['population_density'],
#             prediction=prediction_label,
#             timestamp=timestamp,  
#             source="webapp"  # ✅ Store source
#         )  
#         db.add(new_prediction)

#     await db.commit()
#     return results

# @app.get("/past-predictions")
# async def get_past_predictions(
#     start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
#     end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
#     source: str = Query("all", description="Prediction source (webapp, scheduled, or all)"),
#     db: AsyncSession = Depends(get_db)
# ):
#     try:
#         start_dt = datetime.strptime(start_date, "%Y-%m-%d")
#         end_dt = datetime.strptime(end_date, "%Y-%m-%d")

#         query = select(Prediction).where(Prediction.timestamp.between(start_dt, end_dt))

#         if source.lower() != "all":
#             query = query.where(Prediction.source == source.lower())

#         result = await db.execute(query)
#         records = result.scalars().all()

#         if not records:
#             return {"message": "No data available for the selected date range and source."}

#         return [
#             {
#                 "id": record.id,
#                 "temperature": record.temperature,
#                 "humidity": record.humidity,
#                 "pm_25": record.pm_25,
#                 "pm_10": record.pm_10,
#                 "no2": record.no2,
#                 "so2": record.so2,
#                 "co": record.co,
#                 "proximity_level": record.proximity_level,
#                 "population_density": record.population_density,
#                 "prediction": record.prediction,
#                 "timestamp": record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # ✅ Ensure timestamp is formatted correctly
#                 "source": record.source,
#             }
#             for record in records
#         ]
#     except Exception as e:
#         return {"error": str(e)}
