import os
import json
from server.logic_evaluator import LogicEvaluator
from server.algos.probability import ProbabilityParser
from server.algos.regex import RegexParser
from server.algos.transformer import TransformerParser

MANIFEST_FILE = os.getenv("MANIFEST_FILE", "algo_manifest.json")

class AlgoManager:
    def __init__(self, manifest_file=MANIFEST_FILE):
        # Load manifest rules and dependencies
        with open(manifest_file) as f:
            self.algo_manifest = json.load(f)
        
        # Initialize LogicEvaluator
        self.logic_evaluator = LogicEvaluator()
        
        # Initialize and register parsers
        transformer_parser = TransformerParser()
        self.parsers = {
            "probability": ProbabilityParser(self.algo_manifest.get("models", []) or [], transformer_parser),
            "regex": RegexParser(),
            "transformer": transformer_parser,
        }
        
        for parser in self.parsers.values():
            parser.register_operations(self.logic_evaluator)

    def record_matches_algo(self, record):
        """Evaluate the manifest against a given record."""
        return self.logic_evaluator.evaluate(self.algo_manifest["filter"], record)

# Initialize the manager
algo_manager = AlgoManager()
