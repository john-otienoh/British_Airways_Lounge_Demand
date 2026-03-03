# Import relevant packages
import pandas as pd

EXCEL_FILEPATH = "data.xlsx"
SHEET_NAME = "british_airways_schedule_summer"
OUTPUT_FILE = "flights.csv"

def convert_to_csv(file_path, sheet_name: str):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.to_csv(OUTPUT_FILE, index=False, header=True, encoding='utf-8')
        print("Succesfully Converted")
    except Exception as e:
        print(e)

def read_from_csv(file_path: str):
    """function is used to extract all activity data from the excel sheet"""
    try:
        df = pd.read_csv(file_path)
        return f"The dataset {file_path} has {df.shape[1]} columns and {df.shape[0]} rows."
    except Exception as e:
        print(e)

if __name__ == "__main__":
    convert_to_csv(file_path=EXCEL_FILEPATH, sheet_name=SHEET_NAME)
    print(read_from_csv(OUTPUT_FILE))
