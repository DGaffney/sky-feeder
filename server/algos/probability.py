import pdb
import numpy as np
import xgboost as xgb
from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator
from server.algos.feature_generator import FeatureGenerator
from server.algos.probability_model import ProbabilityModel

class ProbabilityParser(BaseParser):
    def __init__(self, models, transformer_parser):
        self.model_declarations = models
        self.transformer_parser = transformer_parser
        self.models = {}
        self.feature_generator = FeatureGenerator(transformer_parser)  # Initialize with TransformerParser

    def load_model(self, model_name):
        """Loads the XGBoost model if not already loaded."""
        if model_name not in self.models:
            relevant_declarations = [e for e in self.model_declarations if e['model_name'] == model_name]
            if relevant_declarations:
                model_declaration = relevant_declarations[0]
                self.models[model_name] = ProbabilityModel(
                    model_declaration["model_name"],
                    model_declaration["feature_modules"]
                )
                self.models[model_name].load_model()
        return self.models[model_name]

    def get_feature_modules_for_model(self, model_name):
        """Finds feature modules for the specified model in the manifest."""
        for model in self.model_declarations:
            if model["model_name"] == model_name:
                return model.get("feature_modules", [])
        return []

    def probability_for_record(self, record, model_name):
        """Generates features for the model and evaluates probability based on the record."""
        model = self.load_model(model_name)
        feature_modules = self.get_feature_modules_for_model(model_name)
        # Use FeatureGenerator to generate features based on specified modules
        features = self.feature_generator.generate_features(record, feature_modules)
        # Don't laugh at this, noobody look, nobody look https://www.youtube.com/watch?v=E8Ew6K0W3RY
        return float(model.model.model.predict_proba([features])[0][0])

    def probability_with_operator(self, record, model_params, comparator, threshold):
        """Evaluates the probability and applies a comparison operator against the threshold."""
        probability = self.probability_for_record(record, model_params["model_name"])
        return LogicEvaluator.compare(probability, comparator, threshold)

    def register_operations(self, logic_evaluator):
        """Registers the model probability operation with the logic evaluator."""
        logic_evaluator.add_operation("model_probability", self.probability_with_operator)
