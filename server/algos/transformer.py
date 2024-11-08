import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator

class TransformerParser(BaseParser):
    def __init__(self):
        self.vector_models = {}

    def load_model(self, model_name):
        if model_name not in self.vector_models:
            self.vector_models[model_name] = SentenceTransformer(model_name)
        return self.vector_models[model_name]

    def get_embedding(self, text, model_name):
        model = self.load_model(model_name)
        return model.encode(text)

    def text_similarity_operator(self, record, field_selector, model_params, comparator, threshold):
        sample_text = getattr(record, field_selector["var"])
        model_name = model_params["model_name"]
        anchor_text = model_params["anchor_text"]
        similarity = cosine_similarity(
            [self.get_embedding(sample_text, model_name)],
            [self.get_embedding(anchor_text, model_name)]
        )[0][0]
        return LogicEvaluator.compare(similarity, comparator, threshold)

    def register_operations(self, logic_evaluator):
        logic_evaluator.add_operation("text_similarity", self.text_similarity_operator)
