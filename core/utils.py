from typing import List, Dict, Any
import re

def infer_column_types(dataset: List[Dict[str, Any]]) -> Dict[str, str]:
    types: Dict[str, str] = {}
    if not dataset:
        return types

    cols = list(dataset[0].keys())
    date_pattern1 = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
    date_pattern2 = re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$")

    for col in cols:
        values = [row.get(col) for row in dataset]
        # skip None or empty strings
        samples = [v for v in values if v not in (None, "")]
        if not samples:
            types[col] = "string"
            continue

        num_count = 0
        date_count = 0
        total = min(len(samples), 20)
        for v in samples[:20]:
            s = str(v).strip()
            # numeric?
            try:
                float(s)
                num_count += 1
                continue
            except Exception:
                pass

            # date-like?
            if date_pattern1.match(s) or date_pattern2.match(s) or re.search(r"\d{4}", s) and any(c in s for c in ['-','/']):
                date_count += 1

        if num_count >= total * 0.6:
            types[col] = "number"
        elif date_count >= total * 0.5:
            types[col] = "date"
        else:
            types[col] = "string"

    return types