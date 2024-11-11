from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator
from server.algos.shared_model_store import SharedModelStore

class SocialParser(BaseParser):
    def __init__(self, username, password, session_string):
        self.username = username
        self.password = password
        self.session_string = session_string

    def get_starter_pack(self, starter_pack_url):
        return SharedModelStore.get_starter_pack(starter_pack_url, self.username, self.password, self.session_string)

    def get_list(self, list_url):
        return SharedModelStore.get_list(list_url, self.username, self.password, self.session_string)

    def get_user_collection(self, actor_handle, direction):
        return SharedModelStore.get_user_collection(actor_handle, direction, self.username, self.password, self.session_string)

    def starter_pack_member(self, record, create_info, starter_pack_url, operator):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        if operator == "is_in":
            return create_info["author"] in self.get_starter_pack(starter_pack_url).facet_value
        elif operator == "is_not_in":
            return create_info["author"] not in self.get_starter_pack(starter_pack_url).facet_value

    def list_member(self, record, create_info, list_url, operator):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        if operator == "is_in":
            return create_info["author"] in self.get_list(list_url).facet_value
        elif operator == "is_not_in":
            return create_info["author"] not in self.get_list(list_url).facet_value

    def social_graph(self, record, create_info, actor_handle, operator, direction):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        if operator == "is_in":
            return create_info["author"] in self.get_user_collection(actor_handle, direction).facet_value
        elif operator == "is_not_in":
            return create_info["author"] not in self.get_user_collection(actor_handle, direction).facet_value

    def social_list(self, record, create_info, actor_did_list, operator):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        if operator == "is_in":
            return create_info["author"] in actor_did_list
        elif operator == "is_not_in":
            return create_info["author"] not in actor_did_list

    def register_operations(self, logic_evaluator):
        # Register attribute comparison operation
        logic_evaluator.add_operation("social_graph", self.social_graph)
        logic_evaluator.add_operation("social_list", self.social_list)
        logic_evaluator.add_operation("starter_pack_member", self.starter_pack_member)
        logic_evaluator.add_operation("list_member", self.list_member)
