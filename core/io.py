import csv
import json
from typing import List, Dict, Any


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)
            
            for row in csv_reader:
                row_dict = {}
                for i in range(len(headers)):
                    if i < len(row):
                        row_dict[headers[i]] = row[i]
                    else:
                        row_dict[headers[i]] = None
                data.append(row_dict)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error loading file: {e}")
    
    return data

def load_json(file_path: str) -> List[Dict[str, Any]]:
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"Error loading file: {e}")
    
    return data

def output_summary(data: List[Dict[str, Any]]) -> None:
    if not data:
        print("No data to summarize.")
        return
    
    num_rows = len(data)
    num_cols = len(data[0]) if num_rows > 0 else 0
    print(f"Dataset Summary:")
    print(f"Number of rows: {num_rows}")
    print(f"Number of columns: {num_cols}")
    print("Columns:")
    for col in data[0].keys():
        print(f" - {col}")