from typing import Any

def analyze(data):
    if not data:
        return {}
    
    summary: dict[str, dict[str, Any]] = {
        'mean': {},
        'median': {},
        'variance': {},
        'trend': {},
    }

    return summary