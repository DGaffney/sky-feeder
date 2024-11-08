import numpy as np
import xgboost as xgb
from server.algos.base import BaseParser
class ProbabilityParser(BaseParser):
    def __init__(self):
        self.models = {}

    def load_model(self, model_name):
        if model_name not in self.models:
            model_path = self.manager.load_model("probability", model_name)
            model = xgb.Booster()
            model.load_model(model_path)
            self.models[model_name] = model
        return self.models[model_name]

    def probability_for_record(self, record, model_name):
        model = self.load_model(model_name)
        features = record.get("features")
        dmatrix = xgb.DMatrix(np.array([features]))
        return model.predict(dmatrix)[0]

    def probability_with_operator(self, params, record):
        model_name = params[1]["model_name"]
        operator = params[2]
        threshold = params[3]
        probability = self.probability_for_record(record, model_name)
        return LogicEvaluator.compare(probability, operator, threshold)

    def register_operations(self, logic_evaluator):
        logic_evaluator.add_operation("model_probability", self.probability_with_operator)
