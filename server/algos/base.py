import json
import json_logic

class BaseParser:
    def register_operations(self):
        """Register operations specific to each parser."""
        raise NotImplementedError("Subclasses must implement register_operations")
