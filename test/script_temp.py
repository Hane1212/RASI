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
    
    # Error functions
    def introduce_missing_values(df, col):
        """Randomly set some values to NaN."""
        idx = np.random.choice(df.index, size=num_errors // 7, replace=False)
        df.loc[idx, col] = np.nan

#     def remove_column(df):
#         """Remove a required column."""
#         return df.drop(columns=[random.choice(df.columns)], errors="ignore")

    def introduce_unknown_values(df, col):
        """Replace values with unknown symbols."""
        idx = np.random.choice(df.index, size=num_errors // 7, replace=False)
        df.loc[idx, col] = "???"

    def introduce_string_in_numeric(df, col):
        """Replace some numeric values with strings."""
        idx = np.random.choice(df.index, size=num_errors // 7, replace=False)
        df.loc[idx, col] = "error_value"

    def introduce_duplicate_rows(df):
        """Duplicate some rows."""
        duplicate_rows = df.sample(n=num_errors // 7, replace=True)
        return pd.concat([df, duplicate_rows]).reset_index(drop=True)

    def introduce_outliers(df, col):
        """Inject extreme values."""
        idx = np.random.choice(df.index, size=num_errors // 7, replace=False)
        df.loc[idx, col] = df[col].max() * 10  # Exaggerate the max value

    def introduce_negative_values(df, col):
        """Inject negative values where they are not expected."""
        idx = np.random.choice(df.index, size=num_errors // 7, replace=False)
        df.loc[idx, col] = -abs(df[col].max())  # Force negative values

    # Apply errors to random columns
    random.seed(42)
    error_columns = random.sample(list(df.columns), 5)  # Pick random columns for errors

    introduce_missing_values(df, error_columns[0])
    introduce_unknown_values(df, error_columns[1])
    introduce_string_in_numeric(df, error_columns[2])
    df = introduce_duplicate_rows(df)
    introduce_outliers(df, error_columns[3])
    introduce_negative_values(df, error_columns[4])

    # Randomly remove a required column
#     df = remove_column(df)

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