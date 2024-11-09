# shared_model_store.py
from model_provenance import ModelProvenance
from sentence_transformers import SentenceTransformer
import xgboost as xgb
from typing import Dict, List

class SharedModelStore:
    _vector_models: Dict[str, SentenceTransformer] = {}
    _probability_models: Dict[str, xgb.XGBClassifier] = {}
    def probability_model_file_paths(self, model_name):
        return f"./probability_models/{model_name}_model.joblib", f"./probability_models/{model_name}_manifest.json", f"./probability_models/{model_name}_sample_dataset.joblib"

    @classmethod
    def get_vector_model(cls, model_name: str) -> SentenceTransformer:
        if model_name not in cls._vector_models:
            cls._vector_models[model_name] = SentenceTransformer(model_name)
        return cls._vector_models[model_name]

    @classmethod
    def get_probability_model(cls, model_name: str, feature_modules: List[Dict]) -> ModelProvenance:
        from server.algos.probability_model import ProbabilityModel
        if model_name not in cls._probability_models:
            cls._probability_models[model_name] = ProbabilityModel(
                model_name,
                feature_modules
            )
            cls._probability_models[model_name].load_model()
        return cls._probability_models[model_name]
