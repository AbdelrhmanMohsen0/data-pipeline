from typing import List, Dict, Any, Tuple
from imperative_impl.cleaning import DataCleaner
from imperative_impl.transformation import DataTransformer

def run_pipeline(config, dataset) -> Tuple[List[Dict[str, Any]], str, dict | None]:
    cleaner = DataCleaner(dataset, config)
    cleaner.clean()

    transformer = DataTransformer(dataset, config)
    transformer.transform()

    return dataset, "Pipeline executed successfully.", transformer.aggregate_by_key()
