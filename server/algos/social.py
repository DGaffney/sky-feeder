from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator
from server.algos.shared_model_store import SharedModelStore

class SocialParser(BaseParser):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_user_collection(self, actor_handle, direction):
        return SharedModelStore.get_user_collection(actor_handle, direction, self.username, self.password)

    def social_graph(self, record, create_info, actor_handle, operator, direction):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        if operator == "is_in":
            return create_info["author"] in self.get_user_collection(actor_handle, direction).facet_value
        elif operator == "is_not_in":
            return create_info["author"] not in self.get_user_collection(actor_handle, direction).facet_value

    def social_graph(self, record, create_info, actor_did_list, operator):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        if operator == "is_in":
            return create_info["author"] in actor_did_list
        elif operator == "is_not_in":
            return create_info["author"] not in actor_did_list

    def register_operations(self, logic_evaluator):
        # Register attribute comparison operation
        logic_evaluator.add_operation("social_graph", self.social_graph)
        logic_evaluator.add_operation("social_list", self.social_list)
