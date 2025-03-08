import pandas as pd
import numpy as np
import random

def generate_data(error_rate=0.12):
      """
      Generates a corrupted dataset by injecting different types of errors.
      
      Parameters:
      - error_rate (float): Percentage of rows to be corrupted (default: 12%).
      """

      input_file="./data/raw_data/sample_test.csv"
      output_file="./data/raw_data/corrupted_data.csv"
      
      # Load raw data & remove "Air Quality" column
      df = pd.read_csv(input_file).drop(columns=["Air Quality"], errors="ignore")

      # Compute number of errors to introduce
      num_errors = int(len(df) * error_rate)

      # Select a fixed subset of rows to corrupt
      error_indices = np.random.choice(df.index, size=num_errors, replace=False)

      # Define possible error types
      error_types = ["missing", "unknown", "string", "outlier", "negative"]
      
      # Apply one random error per selected row
      for idx in error_indices:
            error_type = random.choice(error_types)
            col = random.choice(df.columns)  # Select a random column to modify
            
            if error_type == "missing":
                  df.loc[idx, col] = np.nan
            elif error_type == "unknown":
                  df.loc[idx, col] = "???"
            elif error_type == "string":
                  df.loc[idx, col] = "error_value"
            elif error_type == "outlier":
                  if pd.api.types.is_numeric_dtype(df[col]):
                        df.loc[idx, col] = df[col].max() * 10  # Extreme outlier
            elif error_type == "negative":
                  if pd.api.types.is_numeric_dtype(df[col]):  
                        df.loc[idx, col] = -abs(pd.to_numeric(df[col], errors="coerce").max())  # Force negative values

      # Save corrupted dataset
      df.to_csv(output_file, index=False)

      print(f"✅ Corrupted dataset saved as {output_file}")


def split_data_to_input_data():
      #csv file name to be read in
      in_csv = './data/raw_data/corrupted_data.csv'

      #get the number of lines of the csv file to be read
      number_lines = sum(1 for row in (open(in_csv)))
      # Read the header (first row) separately
      df_header = pd.read_csv(in_csv, nrows=0)
      header = df_header.columns.tolist()  
      print(header)

      rowsize = 10
      #start looping through data writing it to a new file for each set
      for i in range(1,number_lines,rowsize):
            df = pd.read_csv(in_csv,
                  nrows = rowsize,#number of rows to read at each loop
                  skiprows = i, #skip rows that have been read
                  names=header,
                  header=None)
            
            df.columns = header
            #csv to write data to a new file with indexed name. input_1.csv etc.
            out_csv = f'data/input_data/test_{i}.csv'

            df.to_csv(out_csv,
                  index=False,
                  header=True,
                  mode='a',#append data to csv file
                  chunksize=rowsize)#size of data to append for each loop
            
# Run the function
generate_data()
split_data_to_input_data()