from typing import Any, Dict, List, Tuple
import re
from InquirerPy import inquirer
from core.utils import infer_column_types


def main_menu(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    answers: Dict[str, Any] = {}

    cols = list(dataset[0].keys()) if dataset else []
    col_types = infer_column_types(dataset)

    # Missing data handling
    missing_choice = inquirer.select( # type: ignore
        message="How to handle missing data?",
        choices=["Remove rows with missing values", "Fill with default"],
        pointer="➜",
    ).execute()

    answers['missing_data_action'] = 'remove' if missing_choice.startswith('Remove') else 'fill'

    # Filter rows
    filter_choice = inquirer.select( # type: ignore
        message="Filter rows based on conditions or skip?",
        choices=["Skip filtering", "Filter rows"],
        pointer="➜",
    ).execute()

    answers['filter'] = {'apply': filter_choice.startswith('Filter')}

    if answers['filter']['apply']:
        # choose a column
        col = inquirer.select( # type: ignore
            message="Select a column to filter on:",
            choices=cols,
            pointer="➜",
        ).execute()

        ctype = col_types.get(col, 'string')

        if ctype == 'number':
            ops = ['>', '<', '<=', '>=', '==']
        else:
            ops = ['Exactly equal', 'Contains']

        op = inquirer.select( # type: ignore
            message=f"Select operator for column '{col}':",
            choices=ops,
            pointer="➜",
        ).execute()

        value = inquirer.text( # type: ignore
            message=f"Enter value to compare against for column '{col}':",
            validate=(lambda val: ((ctype != 'number') or (re.match(r"^-?\d+(?:\.\d+)?$", val.strip()) is not None)) or "Enter a numeric value") if ctype == 'number' else (lambda val: val.strip() != "" or "Enter a non-empty value"), # type: ignore
        ).execute()

        answers['filter'].update({'column': col, 'operator': op, 'value': (float(value) if ctype == 'number' else value)})

    # Compute a new column
    compute_choice = inquirer.select( # type: ignore
        message="Compute new column?",
        choices=["Profit", "Skip"],
        pointer="➜",
    ).execute()

    answers['compute'] = compute_choice if compute_choice != "Skip" else None

    # Aggregate by region
    aggregate_choice = inquirer.select( # type: ignore
        message="Aggregate data by key?",
        choices=["Aggregate total sales by region", "Skip"],
        pointer="➜",
    ).execute()

    answers['aggregate'] = aggregate_choice if aggregate_choice != "Skip" else None


    # Output options
    output_choice = inquirer.select( # type: ignore
        message="How to output results?",
        choices=["Save to CSV", "Print summary to console"],
        pointer="➜",
    ).execute()

    answers['output'] = output_choice

    return answers

