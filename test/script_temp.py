import pandas as pd

#csv file name to be read in
in_csv = './data/raw_data/sample_test.csv'

#get the number of lines of the csv file to be read
number_lines = sum(1 for row in (open(in_csv)))
# Read the header (first row) separately
df_header = pd.read_csv(in_csv, nrows=0)
header = df_header.columns.tolist()  
header = header[:-1] 
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
      df = df.iloc[:, :-1]  # Remove the Air Quality column
      #csv to write data to a new file with indexed name. input_1.csv etc.
      out_csv = f'data/input_data/test_{i}.csv'

      df.to_csv(out_csv,
            index=False,
            header=True,
            mode='a',#append data to csv file
            chunksize=rowsize)#size of data to append for each loop