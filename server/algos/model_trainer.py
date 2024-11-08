import xgboost as xgb
import joblib
from atproto import AtUri, Client, IdResolver, models
from sklearn.model_selection import train_test_split
from server.algos.feature_generator import FeatureGenerator
from server.algos.transformer import TransformerParser
from typing import List, Tuple, Optional

class ModelTrainer:
    def __init__(self, username, password, transformer_parser=None):
        # Initialize the API client and log in
        self.client = Client()
        self.client.login(username, password)
        
        # Initialize FeatureGenerator with a TransformerParser for embedding support
        self.transformer_parser = transformer_parser or TransformerParser()
        self.feature_generator = FeatureGenerator(self.transformer_parser)

        # Initialize the IdResolver for DID resolution and memoization cache
        self.resolver = IdResolver()
        self.did_cache = {}

    def resolve_did(self, handle: str) -> str:
        """Memoized method to resolve a DID from a handle."""
        if handle in self.did_cache:
            return self.did_cache[handle]
        did = self.resolver.handle.resolve(handle)
        self.did_cache[handle] = did
        return did

    def url_to_uri(self, url: str) -> Optional[str]:
        """
        Convert a Bluesky post URL to an at:// URI.
        
        Example URL: https://bsky.app/profile/username/post/post_id
        Converts to: at://did:plc:xxxxx/app.bsky.feed.post/post_id
        """
        try:
            parts = url.split("/")
            handle = parts[4]  # Extract the username
            post_id = parts[6]  # Extract the post ID
            did = self.resolve_did(handle)  # Resolve DID
            return f"at://{did}/app.bsky.feed.post/{post_id}"
        except Exception as e:
            print(f"Error converting URL {url} to URI: {e}")
            return None

    def fetch_records_batch(self, urls: List[str]) -> dict:
        """
        Fetch records in batches of up to 100 posts, returning records mapped by their original URLs.
        
        Args:
            urls (List[str]): List of URLs for the posts to fetch.
        
        Returns:
            dict: A dictionary mapping each original URL to its fetched record or None if not fetched.
        """
        url_to_record = {}
        uri_batch = []
        
        # Convert each URL to its at:// URI
        for url in urls:
            at_uri = self.url_to_uri(url)
            if at_uri:
                uri_batch.append(at_uri)
                url_to_record[url] = None  # Initialize mapping with None for unfetched records

            # Process in batches of up to 100 URIs
            if len(uri_batch) == 100 or url == urls[-1]:  # Either batch limit or last URL
                try:
                    response = self.client.get_posts(uri_batch)
                    for uri, post in zip(uri_batch, response.posts):
                        original_url = next((k for k, v in url_to_record.items() if v is None and uri.endswith(post.uri.split("/")[-1])), None)
                        if original_url:
                            url_to_record[original_url] = post.record
                except Exception as e:
                    print(f"Error fetching records for batch: {e}")
                
                uri_batch.clear()  # Clear batch after processing

        return url_to_record

    def accumulate_dataset(self, urls: List[str], labels: List[int], feature_modules: List[dict]) -> Tuple[List, List]:
        """
        Given a list of URLs and labels, fetch records, extract features,
        and build a dataset.
        
        Args:
            urls (List[str]): List of URLs for the posts.
            labels (List[int]): List of labels for each post.
            feature_modules (List[dict]): List of feature modules for feature generation.
        
        Returns:
            Tuple[List, List]: Feature matrix (X) and labels (y) as arrays.
        """
        X, y = [], []
        records = self.fetch_records_batch(urls)  # Batch fetch records by URLs
        
        for url, label in zip(urls, labels):
            record = records.get(url)
            if record:
                features = self.feature_generator.generate_features(record, feature_modules)
                X.append(features)
                y.append(label)
        return X, y

    def train_model(self, X: List, y: List, model_name: str = "default_model"):
        """Train an XGBoost model and save it along with the feature generator."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train the XGBoost model
        model = xgb.XGBClassifier(objective="binary:logistic", eval_metric="logloss")
        model.fit(X_train, y_train)
        
        # Evaluate the model
        accuracy = model.score(X_test, y_test)
        print(f"Model trained with accuracy: {accuracy:.2f}")

        # Save model and feature generator
        model_path = f"{model_name}.joblib"
        joblib.dump((model, self.feature_generator), model_path)
        print(f"Model saved to {model_path}")

    def load_model(self, model_name="default_model"):
        """Load a previously saved model."""
        model_path = f"{model_name}.joblib"
        model, feature_generator = joblib.load(model_path)
        return model, feature_generator
