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

def output_analysis(report: Dict[str, Any]) -> None:
    """Pretty-print the analysis report returned by `run_pipeline`.

    Expected report format (as produced by `imperative_impl.DataAnalyzer.analyze`):
      {
          'mean': {col: value, ...},
          'median': {col: value, ...},
          'variance': {col: value, ...},
          'trend': {'YYYY-MM': aggregated_value, ...}
      }

    The function prints each section in a readable, sorted order.
    """
    if not report:
        print("No analysis report to display.")
        return

    print("Analysis Report:")

    # Helper to print numeric maps
    def _print_map(title: str, mapping: Dict[str, Any], fmt_number: bool = True):
        print(f"\n{title}:")
        if not mapping:
            print("  (no data)")
            return
        for key in sorted(mapping.keys()):
            val = mapping[key]
            if fmt_number and isinstance(val, (int, float)):
                # choose reasonable formatting
                if isinstance(val, int) or abs(val) >= 1:
                    out = f"{val:.4f}" if isinstance(val, float) else f"{val}"
                else:
                    out = f"{val:.6f}"
            else:
                out = str(val)
            print(f"  - {key}: {out}")

    # Print known sections in a predictable order
    for section in ("mean", "median", "variance"):
        if section in report:
            _print_map(section.capitalize(), report.get(section, {}))

    # Trend is typically a time series (YYYY-MM -> value)
    if "trend" in report:
        trend = report.get("trend", {}) or {}
        print("\nTrend (monthly):")
        if not trend:
            print("  (no trend data)")
        else:
            for month in sorted(trend.keys()):
                val = trend[month]
                print(f"  - {month}: {val:.4f}" if isinstance(val, (int, float)) else f"  - {month}: {val}")




def save_csv(data: List[Dict[str, Any]], file_path: str) -> None:
    if not data:
        print("No data to save.")
        return
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to '{file_path}' successfully.")
    except Exception as e:
        print(f"Error saving file: {e}")