import pdb
import numpy as np
import xgboost as xgb
from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator
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

    def probability_with_operator(self, record, field_selector, model_params, comparator, threshold):
        pdb.set_trace()
        probability = self.probability_for_record(getattr(record, field_selector["var"]), model_params["model_name"])
        return LogicEvaluator.compare(probability, comparator, threshold)

    def register_operations(self, logic_evaluator):
        logic_evaluator.add_operation("model_probability", self.probability_with_operator)

