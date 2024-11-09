import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from server.logic_evaluator import LogicEvaluator
from server.algos.base import BaseParser
from server.algos.shared_model_store import SharedModelStore

class TransformerParser(BaseParser):
    def get_embedding(self, text, model_name):
        model = SharedModelStore.get_vector_model(model_name)
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
