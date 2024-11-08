import os
import json
from server.logic_evaluator import LogicEvaluator
from server.algos.probability import ProbabilityParser
from server.algos.regex import RegexParser
from server.algos.transformer import TransformerParser

MANIFEST_FILE = os.getenv("MANIFEST_FILE", "algo_manifest.json")
DEPENDENCIES_FILE = os.getenv("DEPENDENCIES_FILE", "algo_dependencies.json")

class AlgoManager:
    def __init__(self, manifest_file=MANIFEST_FILE, dependencies_file=DEPENDENCIES_FILE):
        # Load manifest rules and dependencies
        with open(manifest_file) as f:
            self.algo_manifest = json.load(f)
        with open(dependencies_file) as f:
            self.dependencies = json.load(f)
        
        # Initialize LogicEvaluator
        self.logic_evaluator = LogicEvaluator()
        
        # Initialize and register parsers
        self.parsers = {
            "probability": ProbabilityParser(),
            "regex": RegexParser(),
            "transformer": TransformerParser(),
        }
        
        for parser in self.parsers.values():
            parser.register_operations(self.logic_evaluator)

    def record_matches_algo(self, record):
        """Evaluate the manifest against a given record."""
        return self.logic_evaluator.evaluate(self.algo_manifest, record)

    def load_model(self, parser_name, model_name):
        """Dynamically loads models based on the dependencies.json configuration."""
        model_path = self.dependencies.get(parser_name, {}).get(model_name)
        if not model_path:
            raise ValueError(f"No model path found for '{model_name}' in '{parser_name}' dependencies.")
        return model_path  # The path is returned; actual loading is handled within each parser

# Initialize the manager
algo_manager = AlgoManager()
