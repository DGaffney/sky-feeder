import os
import json
from server.logic_evaluator import LogicEvaluator
from server.algos.probability import ProbabilityParser
from server.algos.regex import RegexParser
from server.algos.transformer import TransformerParser
from server.algos.probability_model import ProbabilityModel

MANIFEST_FILE = os.getenv("MANIFEST_FILE", "algo_manifest.json")

class AlgoManager:
    def __init__(self, manifest_file=MANIFEST_FILE, version_hash=None):
        # Load manifest rules and dependencies
        with open(manifest_file) as f:
            self.algo_manifest = json.load(f)
        self.version_hash = version_hash
        # Initialize LogicEvaluator
        self.logic_evaluator = LogicEvaluator()
        
        # Initialize and register parsers
        transformer_parser = TransformerParser()
        self.parsers = {
            "probability": ProbabilityParser(self.models, transformer_parser),
            "regex": RegexParser(),
            "transformer": transformer_parser,
        }
        
        for parser in self.parsers.values():
            parser.register_operations(self.logic_evaluator)

    @property
    def models(self):
        return self.algo_manifest.get("models", []) or []

    def record_matches_algo(self, record):
        """Evaluate the manifest against a given record."""
        return self.logic_evaluator.evaluate(self.algo_manifest["filter"], record)

    def build_manifest_models(self):
        username = self.algo_manifest["author"]["username"]
        password = self.algo_manifest["author"]["password"]
        for model in self.models:
            probability_model = ProbabilityModel(
                model["model_name"],
                model["feature_modules"],
                None,
                username,
                password,
            )
            probability_model.build_model(json.loads(open(model["training_file"]).read()))

# Initialize the manager
algo_manager = AlgoManager()
