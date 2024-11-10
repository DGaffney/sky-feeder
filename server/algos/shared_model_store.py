# shared_model_store.py
from datetime import datetime, timedelta
from model_provenance import ModelProvenance
from sentence_transformers import SentenceTransformer
import xgboost as xgb
from typing import Dict, List
from server.database import SessionLocal, SearchFacet
from server.bluesky_api import BlueskyAPI

class SharedModelStore:
    _vector_models: Dict[str, SentenceTransformer] = {}
    _probability_models: Dict[str, xgb.XGBClassifier] = {}
    _search_facets: Dict[str, SearchFacet] = {}

    def get_user_collection(actor_handle, direction, username, password):
        keyname = f"{SearchFacet.user_collection_type}__{actor_handle}__{direction}"
        if keyname not in cls._search_facets:
            with SessionLocal() as db:
                search_facet = db.query(SearchFacet).filter(SearchFacet.facet_name==SearchFacet.user_collection_type, SearchFacet.facet_parameters=={"actor_handle": actor_handle, "direction": direction}).first()
                out_of_date = search_facet and (not search_facet.updated_at or search_facet.updated_at < datetime.now() - timedelta(days=1))
                if not search_facet or out_of_date:
                    search_facet = search_facet or SearchFacet(facet_name=SearchFacet.user_collection_type, facet_parameters={"actor_handle": actor_handle, "direction": direction})
                    if direction == "follows":
                        search_facet.facet_value = [e.did for e in BlueskyAPI(username, password).get_all_follows(actor_handle)]
                    elif direction == "followers":
                        search_facet.facet_value = [e.did for e in BlueskyAPI(username, password).get_all_followers(actor_handle)]
                    if not out_of_date:
                        db.add(search_facet)
                    db.commit()
                cls._search_facets[keyname] = search_facet
        return cls._search_facets[keyname]

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
