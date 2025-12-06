from typing import Any, Dict, List, Tuple
import re
from InquirerPy import inquirer
from utils import infer_column_types


def main_menu(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    answers: Dict[str, Any] = {}

    cols = list(dataset[0].keys()) if dataset else []
    col_types = infer_column_types(dataset)

    # 1. Missing data handling
    missing_choice = inquirer.select( # type: ignore
        message="How to handle missing data?",
        choices=["Remove rows with missing values", "Fill with default"],
        pointer="➜",
    ).execute()

    answers['missing_data'] = {'action': 'remove' if missing_choice.startswith('Remove') else 'fill'}

    if answers['missing_data']['action'] == 'fill':
        # ask defaults for number, string, date
        number_default = inquirer.text( # type: ignore
            message="Enter default value for numbers:",
            validate=lambda val: (val.strip() != "" and (re.match(r"^-?\d+(?:\.\d+)?$", val.strip()) is not None)) or "Enter a numeric value", # type: ignore
        ).execute()

        string_default = inquirer.text( # type: ignore
            message="Enter default value for strings:",
            validate=lambda val: val is not None and val.strip() != "" or "Enter a non-empty string", # type: ignore
        ).execute()

        date_default = inquirer.text( # type: ignore
            message="Enter default value for dates (e.g. 2020-01-01):",
            validate=lambda val: val is not None and val.strip() != "" or "Enter a non-empty date string", # type: ignore
        ).execute()

        answers['missing_data']['defaults'] = { # type: ignore
            'number': float(number_default) if number_default is not None and number_default.strip() != "" else None,
            'string': string_default,
            'date': date_default,
        }

    # 2. Standardize formats for dates
    date_format = inquirer.text( # type: ignore
        message="Enter standard date format (use only y, m, d and dashes, e.g. yyyy-mm-dd):",
        validate=lambda val: (val is not None and val.strip() != "" and set(val.strip().lower()).issubset(set('ymd-/')) and all(c in val.lower() for c in ['y','m','d'])) or "Use only y, m, d and dashes and include y,m,d", # type: ignore
    ).execute()

    answers['date_format'] = date_format.strip()

    # 3. Standardize numerical precision
    precision = inquirer.text( # type: ignore
        message="Enter numerical precision (number of decimals, e.g., 2). Leave empty to skip:",
        validate=lambda val: (val.strip() == "") or (val.isdigit() and int(val) >= 0) or "Enter a non-negative integer or leave empty", # type: ignore
    ).execute()

    answers['numeric_precision'] = int(precision) if precision.strip() != "" else None

    # 4. Filter rows
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

    # 5. Compute a new column
    compute_choice = inquirer.select( # type: ignore
        message="Compute a new column?",
        choices=["Ratio A to B", "Percent Change", "Skip"],
        pointer="➜",
    ).execute()

    answers['compute'] = {'operation': None}

    if not compute_choice.startswith('Skip'):
        numeric_cols = [c for c, t in col_types.items() if t == 'number']
        if len(numeric_cols) < 2:
            # can't compute
            answers['compute']['operation'] = 'skip' # type: ignore
            answers['compute']['reason'] = 'not enough numeric columns' # type: ignore
        else:
            operation = 'ratio' if compute_choice.startswith('Ratio') else 'percent_change'
            col_a = inquirer.select( # type: ignore
                message="Select numerator (A):",
                choices=numeric_cols,
                pointer="➜",
            ).execute()

            col_b = inquirer.select( # type: ignore
                message="Select denominator (B):",
                choices=[c for c in numeric_cols if c != col_a] or numeric_cols,
                pointer="➜",
            ).execute()

            new_col = inquirer.text( # type: ignore
                message="Enter header name for the new computed column:",
                validate=lambda val: val.strip() != "" or "Enter a non-empty column name", # type: ignore
            ).execute()

            answers['compute'] = {
                'operation': operation,
                'col_a': col_a,
                'col_b': col_b,
                'new_column': new_col.strip(),
            }

    return answers

