import os
import json
from server.logic_evaluator import LogicEvaluator
from server.algos.probability import ProbabilityParser
from server.algos.regex import RegexParser
from server.algos.transformer import TransformerParser
from server.algos.model_trainer import ModelTrainer

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
        model = {'model_name': 'news_without_science_model', 'training_file': 'prototype_labeled_dataset.json', 'feature_modules': [{'type': 'time_features'}, {'type': 'vectorizer', 'model_name': 'all-MiniLM-L6-v2'}, {'type': 'post_metadata'}]}
        username = "devingaffney.com"
        password = "hguj-nz5b-fb3g-b57a"
        for model in self.models:
            model_trainer = ModelTrainer(
                username,
                password,
                model["model_name"],
                model["feature_modules"]
            )
            model_trainer.build_model(json.loads(open(model["training_file"]).read()))

# Initialize the manager
algo_manager = AlgoManager()
