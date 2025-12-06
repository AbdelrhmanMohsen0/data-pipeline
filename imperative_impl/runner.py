from typing import List, Dict, Any
from imperative_impl.cleaning import DataCleaner
from imperative_impl.transformation import DataTransformer

def run_pipeline(config, dataset) -> List[Dict[str, Any]]:
    cleaner = DataCleaner(dataset, config)
    cleaner.clean()

    transformer = DataTransformer(dataset, config)
    transformer.transform()

    return dataset
