from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator
from server.algos.shared_model_store import SharedModelStore

class SocialParser(BaseParser):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_user_collection(self, focus_did, direction):
        model = SharedModelStore.get_user_collection(focus_did, direction, self.username, self.password)
        return model.encode(text)

    def user_collection_compare(self, record, field_selector, operator, target_value):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        value = resolve_path(record, field_selector[""])
        return LogicEvaluator.compare(value, operator, target_value)

    def register_operations(self, logic_evaluator):
        # Register attribute comparison operation
        logic_evaluator.add_operation("attribute_compare", self.attribute_compare)
