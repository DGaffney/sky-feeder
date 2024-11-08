import re
from server.algos.base import BaseParser

class RegexParser(BaseParser):
    def matches_operator(self, record, field_selector, pattern):
        """Returns True if the field matches the pattern."""
        return bool(re.search(pattern, getattr(record, field_selector["var"])))

    def negation_matches_operator(self, record, field_selector, pattern):
        """Returns True if the field does NOT match the pattern."""
        return not bool(re.search(pattern, getattr(record, field_selector["var"])))

    def register_operations(self, logic_evaluator):
        # Register both matches and negation matches operations
        logic_evaluator.add_operation("regex_matches", self.matches_operator)
        logic_evaluator.add_operation("regex_negation_matches", self.negation_matches_operator)
