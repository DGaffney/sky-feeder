import pdb
import numpy as np
import xgboost as xgb
from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator
from server.feature_generator import FeatureGenerator

class ProbabilityParser(BaseParser):
    def __init__(self, models, transformer_parser):
        self.model_declarations = models
        self.transformer_parser = transformer_parser
        self.models = {}
        self.feature_generator = FeatureGenerator(transformer_parser)  # Initialize with TransformerParser

    def load_model(self, model_name):
        """Loads the XGBoost model if not already loaded."""
        if model_name not in self.models:
            model = xgb.Booster()
            model.load_model(f"{model_name}.json")
            self.models[model_name] = model
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
        dmatrix = xgb.DMatrix(np.array([features]))
        return model.predict(dmatrix)[0]

    def probability_with_operator(self, record, field_selector, model_params, comparator, threshold):
        """Evaluates the probability and applies a comparison operator against the threshold."""
        probability = self.probability_for_record(getattr(record, field_selector["var"]), model_params["model_name"])
        return LogicEvaluator.compare(probability, comparator, threshold)

    def register_operations(self, logic_evaluator):
        """Registers the model probability operation with the logic evaluator."""
        logic_evaluator.add_operation("model_probability", self.probability_with_operator)
