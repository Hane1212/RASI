from sqlalchemy import Column, Integer, Float, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    pm_25 = Column(Float)
    pm_10 = Column(Float)
    no2 = Column(Float)
    so2 = Column(Float)
    co = Column(Float)
    proximity_level = Column(Float)
    population_density = Column(Float)
    prediction = Column(String) 
    timestamp = Column(DateTime, default=func.now())
    source = Column(String, default="webapp")