
-- Create the predictions table
CREATE TABLE predictions (
    prediction_id SERIAL PRIMARY KEY,  -- Auto-incrementing primary key
    input_features JSONB NOT NULL,     -- Store input features as JSON
    prediction FLOAT NOT NULL,         -- Store the model's prediction
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of the prediction
);

-- Create the data_quality_issues table
CREATE TABLE data_quality_issues (
    issue_id SERIAL PRIMARY KEY,       -- Auto-incrementing primary key
    issue_type VARCHAR(100) NOT NULL,  -- Type of issue (e.g., missing value)
    description TEXT,                  -- Description of the issue
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of the issue
);

-- Create the data_drift_metrics table
CREATE TABLE data_drift_metrics (
    metric_id SERIAL PRIMARY KEY,      -- Auto-incrementing primary key
    metric_name VARCHAR(100) NOT NULL, -- Name of the metric (e.g., mean, std_dev)
    training_value FLOAT NOT NULL,     -- Value of the metric in training data
    serving_value FLOAT NOT NULL,      -- Value of the metric in serving data
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp of the metric
);