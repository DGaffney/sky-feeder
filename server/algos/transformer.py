import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from server.algos.base import BaseParser

class TransformerParser(BaseParser):
    def __init__(self):
        self.vector_models = {}

    def load_model(self, model_name):
        if model_name not in self.vector_models:
            model_path = self.manager.load_model("transformer", model_name)
            self.vector_models[model_name] = SentenceTransformer(model_path)
        return self.vector_models[model_name]

    def text_similarity_operator(self, record, field_selector, model_params, comparator, threshold):
        sample_text = getattr(record, field_selector["var"])
        model_info = params[1]
        model_name = model_params["model_name"]
        anchor_text = model_params["anchor_text"]
        model = self.load_model(model_name)
        similarity = cosine_similarity([model.encode(sample_text)], [model.encode(anchor_text)])[0][0]
        return LogicEvaluator.compare(similarity, comparator, threshold)

    def register_operations(self, logic_evaluator):
        logic_evaluator.add_operation("text_similarity", self.text_similarity_operator)
