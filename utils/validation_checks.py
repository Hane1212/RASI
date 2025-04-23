from great_expectations import PandasDataset
import great_expectations as ge
import pandas as pd


EXPECTED_COLUMNS = [
    "Temperature", "Humidity", "PM2.5", "PM10", "NO2", "SO2", "CO",
    "Proximity_to_Industrial_Areas", "Population_Density"
]


class CustomDataset(PandasDataset):
    @staticmethod
    def validate_data(df: pd.DataFrame):
        ge_df = CustomDataset(df)

        # 1. Required column check
        for col in EXPECTED_COLUMNS:
            ge_df.expect_column_to_exist(col)

        # 2. Missing values
        for col in EXPECTED_COLUMNS:
            ge_df.expect_column_values_to_not_be_null(col)

        # 3. Unknown values
        for col in EXPECTED_COLUMNS:
            ge_df.expect_column_values_to_not_be_in_set(col, ["NaN", "???"])

        # 4. Logical invalid values
        ge_df.expect_column_values_to_be_between("humidity", min_value=0, max_value=100)
        ge_df.expect_column_values_to_be_between("pm10", min_value=0)
        ge_df.expect_column_values_to_be_between("so2", min_value=0)
        

        # 5. String in numeric column
        for col in EXPECTED_COLUMNS:
            ge_df.expect_column_values_to_match_strict_type_list(col, ["float", "int"])

        # 6. Duplicate rows
        ge_df.expect_table_row_count_to_be_between(
            min_value=1, max_value=df.drop_duplicates().shape[0]
        )

        # 7. Outlier check (500 < PM10)
        ge_df.expect_column_values_to_be_between("Proximity_to_Industrial_Areas", max_value=500)
        True, False
        result = ge_df.validate()
        df["is_valid"] = [res["success"] for res in result["results"]]
        return {
            "result": result,
            "good_data": df[df["is_valid"]],
            "bad_data": df[~df["is_valid"]],
        }



# import pandas as pd
# import great_expectations as ge

# def check_missing_columns(df: pd.DataFrame, required_columns: list):
#     issues = []
#     nb_invalid = 0

#     for col in required_columns:
#         if col not in df.columns:
#             issues.append(f"Missing required column: {col}")
#             nb_invalid += len(df)  # assume all rows are invalid
#     return issues, nb_invalid


# def check_missing_values(df: pd.DataFrame, required_columns: list):
#     issues = []
#     nb_invalid = 0

#     for column in required_columns:
#         result = ge.from_pandas(df).expect_column_values_to_not_be_null(column)
#         if not result.success:
#             issues.append(f"Missing values in '{column}'")
#             nb_invalid = len(result.result["unexpected_index_list"])
#     return issues, nb_invalid


# def check_unknown_values(df: pd.DataFrame):
#     issues = []
#     nb_invalid = 0

#     for col in df.columns:
#         count = df[col].astype(str).str.contains(r"\?\?\?", na=False).sum()
#         if count > 0:
#             issues.append(f"Unknown value '???' in column: {col}")
#             nb_invalid += count
#     return issues, nb_invalid


# def check_invalid_ranges(df: pd.DataFrame):
#     issues = []
#     nb_invalid = 0
#     ge_df = ge.from_pandas(df)

#     ranges = {
#         "Humidity (%)": {"max_value": 100},
#         "PM10 (µg/m³)": {"min_value": 0},
#         "SO2 (ppb)": {"min_value": 0}
#     }

#     for col, params in ranges.items():
#         if col in df.columns:
#             result = ge_df.expect_column_values_to_be_between(col, **params)
#             if not result.success:
#                 issues.append(f"Invalid values in '{col}'")
#                 nb_invalid += len(result.result["unexpected_index_list"])
#     return issues, nb_invalid


# def check_string_in_numeric(df: pd.DataFrame, EXPECTED_COLUMNS):
#     issues = []
#     nb_invalid = 0

#     for column in EXPECTED_COLUMNS:
#         invalid = df[column].apply(lambda x: isinstance(x, str)).sum()
#         if invalid > 0:
#             issues.append(f"Non-numeric values in '{column}'")
#             nb_invalid += invalid
#     return issues, nb_invalid


# def check_duplicates(df: pd.DataFrame):
#     issues = []
#     nb_invalid = 0

#     if df.duplicated().any():
#         issues.append("Duplicate rows found")
#         nb_invalid += df.duplicated().sum()
#     return issues, nb_invalid


# def check_outliers(df: pd.DataFrame, column: str, max_value: float = 500):
#     issues = []
#     nb_invalid = 0

#     if column in df.columns:
#         result = ge.from_pandas(df).expect_column_values_to_be_between(column, max_value=max_value)
#         if not result.success:
#             issues.append(f"Outliers detected in '{column}'")
#             nb_invalid += len(result.result["unexpected_index_list"])
#     return issues, nb_invalid
