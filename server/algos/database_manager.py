import json
import hashlib
from typing import Optional
from server.algos.manager import AlgoManager
class AlgoDatabaseManager:
    def generate_version_hash(self, manifest: dict) -> str:
        """Generate a hash for the given manifest dictionary."""
        manifest_str = json.dumps(manifest, sort_keys=True)
        return hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()

    def save_algorithm(self, user_id: str, algo_uri: str, manifest: dict):
        """Save or update an algorithm entry with version hash check."""
        version_hash = self.generate_version_hash(manifest)
        manifest_str = json.dumps(manifest)

        # Insert or update the UserAlgorithm entry
        UserAlgorithm.insert(
            user_id=user_id,
            algo_uri=algo_uri,
            manifest=manifest_str,
            version_hash=version_hash
        ).on_conflict(
            conflict_target=(UserAlgorithm.user_id, UserAlgorithm.algo_uri),
            preserve=(UserAlgorithm.manifest, UserAlgorithm.version_hash)
        ).execute()

    def load_algorithm(self, user_id: str, algo_uri: str) -> Optional[dict]:
        """Load an algorithm manifest by user ID and algo URI."""
        try:
            algo_entry = UserAlgorithm.get(UserAlgorithm.user_id == user_id, UserAlgorithm.algo_uri == algo_uri)
            return AlgoManager(json.loads(algo_entry.manifest), algo_entry.version_hash)
        except UserAlgorithm.DoesNotExist:
            return None

    def get_algorithm(self, user_id: str, algo_uri: str, new_manifest: dict) -> bool:
        """Check if a new version exists for the user's algorithm and update if necessary."""
        new_version_hash = self.generate_version_hash(new_manifest)
        algorithm = self.load_algorithm(user_id, algo_uri)

        # Update and reload if version hash has changed
        if not manifest_data or manifest_data[1] != new_version_hash:
            self.save_algorithm(user_id, algo_uri, new_manifest)
            return True  # Indicate that the algorithm needs to be reloaded
        return False  # No update required

    def get_all_user_algorithms(self):
        """Retrieve all active user algorithms."""
        return UserAlgorithm.select(UserAlgorithm.user_id, UserAlgorithm.algo_uri)