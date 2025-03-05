CREATE TABLE predictions (  
    id SERIAL PRIMARY KEY,  
    temperature FLOAT,  
    humidity FLOAT,  
    pm_25 FLOAT,  
    pm_10 FLOAT,  
    no2 FLOAT,  
    so2 FLOAT,  
    co FLOAT,  
    proximity_level FLOAT,  
    population_density FLOAT,  
    prediction VARCHAR(255),  
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),  
    source VARCHAR(255) DEFAULT 'webapp'  
);  
