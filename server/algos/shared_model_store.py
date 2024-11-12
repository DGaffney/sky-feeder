# shared_model_store.py
from datetime import datetime, timedelta, timezone
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

    @classmethod
    def manage_search_facet(cls, keyname, facet_name, facet_parameters, value_provider):
        if keyname not in cls._search_facets:
            with SessionLocal() as db:
                search_facet = db.query(SearchFacet).filter(
                    SearchFacet.facet_name == facet_name,
                    SearchFacet.facet_parameters == facet_parameters
                ).first()
                out_of_date = search_facet and (
                    not search_facet.updated_at or 
                    search_facet.updated_at < datetime.now(timezone.utc) - timedelta(days=10)
                )
                if not search_facet or out_of_date:
                    search_facet = search_facet or SearchFacet(
                        facet_name=facet_name,
                        facet_parameters=facet_parameters
                    )
                    search_facet.facet_value = value_provider(facet_parameters)
                    
                    if not out_of_date:
                        db.add(search_facet)
                    db.commit()
                val = search_facet.facet_value
                if isinstance(search_facet.facet_value, list):
                    try:
                        val = set(search_facet.facet_value)
                    except:
                        val = search_facet.facet_value
                cls._search_facets[keyname] = val

    @classmethod
    def get_facet(cls, facet_type, facet_parameters, social_auth, keyname_template, value_function):
        keyname = keyname_template.format(**facet_parameters)
        value_provider = lambda params: value_function(
            params, social_auth["username"], social_auth["password"], social_auth["session_string"]
        )
        cls.manage_search_facet(keyname, facet_type, facet_parameters, value_provider)
        return cls._search_facets[keyname]

    @classmethod
    def get_user_collection_value(cls, params, username, password, session_string):
        api = BlueskyAPI(username, password, session_string)
        if params["direction"] == "follows":
            return [e.did for e in api.get_all_follows(params["actor_handle"])]
        elif direction == "followers":
            return [e.did for e in api.get_all_followers(params["actor_handle"])]
        return []

    @classmethod
    def get_starter_pack_value(cls, params, username, password, session_string):
        return [e.subject.did for e in BlueskyAPI(username, password, session_string).get_starter_pack_members(params["starter_pack_url"])]

    @classmethod
    def get_list_value(cls, params, username, password, session_string):
        client = BlueskyAPI(username, password, session_string)
        _,_,_,_,handle,_,id = params["list_url"].split("/")
        profile = client.client.get_profile(handle)
        return [e.subject.did for e in client.get_all_list_members(f"at://{profile.did}/app.bsky.graph.list/{id}")]

    @classmethod
    def get_user_collection(cls, actor_handle, direction, username, password, session_string):
        return cls.get_facet(
            facet_type=SearchFacet.user_collection_type,
            facet_parameters={"actor_handle": actor_handle, "direction": direction},
            social_auth={"username": username, "password": password, "session_string": session_string},
            keyname_template="{actor_handle}__{direction}",
            value_function=cls.get_user_collection_value
        )

    @classmethod
    def get_starter_pack(cls, starter_pack_url, username, password, session_string):
        return cls.get_facet(
            facet_type=SearchFacet.starter_pack_type,
            facet_parameters={"starter_pack_url": starter_pack_url},
            social_auth={"username": username, "password": password, "session_string": session_string},
            keyname_template="{starter_pack_url}",
            value_function=cls.get_starter_pack_value
        )

    @classmethod
    def get_list(cls, list_url, username, password, session_string):
        return cls.get_facet(
            facet_type=SearchFacet.list_type,
            facet_parameters={"list_url": list_url},
            social_auth={"username": username, "password": password, "session_string": session_string},
            keyname_template="{list_url}",
            value_function=cls.get_list_value
        )

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
