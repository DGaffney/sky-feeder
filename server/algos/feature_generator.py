# feature_generator.py

import numpy as np
from server.algos.transformer import TransformerParser
from server.algos.shared_model_store import SharedModelStore
class FeatureGenerator:
    def generate_features(self, record, feature_modules):
        """Generates features for a given record based on specified feature modules."""
        features = []
        for module in feature_modules:
            module_type = module.get("type")
            if module_type == "time_features":
                features.extend(self.time_features(record))
            elif module_type == "vectorizer":
                model_name = module.get("model_name")
                features.extend(self.vectorizer(record, model_name))
            elif module_type == "post_metadata":
                features.extend(self.post_metadata(record))
            else:
                raise ValueError(f"Unknown feature module type: {module_type}")
        return features

    def time_features(self, record):
        """Generates time-related features based on the record's creation time."""
        created_at = getattr(record, "created_at", "")
        hour = int(created_at[11:13]) if created_at else 0  # Extract hour, default to 0 if no timestamp
        weekday = np.datetime64(created_at).astype('datetime64[D]').astype(int) % 7 if created_at else 0
        return [hour, weekday]

    def vectorizer(self, record, model_name):
        """Generates text embeddings using a specified transformer model."""
        text = getattr(record, "text", "")
        if not text:
            return [0.0] * SharedModelStore.get_vector_model(model_name).get_sentence_embedding_dimension()
        # Get the embedding via TransformerParser
        embedding = TransformerParser().get_embedding(text, model_name)
        return embedding.tolist()

    def post_metadata(self, record):
        """Generates metadata features based on post content, such as text length and punctuation counts."""
        text = getattr(record, "text", "")
        return [len(text), text.count("!")]  # Example metadata features
