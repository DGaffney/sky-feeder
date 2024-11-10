import os
import json
from server.logic_evaluator import LogicEvaluator
from server.algos.operators.probability import ProbabilityParser
from server.algos.operators.regex import RegexParser
from server.algos.operators.transformer import TransformerParser
from server.algos.operators.attribute import AttributeParser
from server.algos.operators.social import SocialParser
from server.algos.probability_model import ProbabilityModel

MANIFEST_FILE = os.getenv("MANIFEST_FILE", "algo_manifest.json")

class AlgoManager:
    def __init__(self, algo_manifest, version_hash=None):
        # Store the version and initialize parsers with shared model references
        self.algo_manifest = algo_manifest
        self.version_hash = version_hash
        self.logic_evaluator = LogicEvaluator()
        self.parsers = {
            "probability": ProbabilityParser(algo_manifest.get("models", [])),
            "regex": RegexParser(),
            "transformer": TransformerParser(),
            "attribute": AttributeParser(),
            "social": SocialParser(*self.username_password_from_algo_manifest),
        }
        for parser in self.parsers.values():
            parser.register_operations(self.logic_evaluator)

    @property
    def username_password_from_algo_manifest(self):
        return [
            (self.algo_manifest.get("author", {}) or {}).get("username"),
            (self.algo_manifest.get("author", {}) or {}).get("password")
        ]

    @property
    def models(self):
        return self.algo_manifest.get("models", []) or []

    def record_matches_algo(self, record, create_info):
        """Evaluate the manifest against a given record."""
        return self.logic_evaluator.evaluate(self.algo_manifest["filter"], record, create_info)

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

