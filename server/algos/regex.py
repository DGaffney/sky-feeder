# regex.py
import re
from server.algos.base import BaseParser

class RegexParser(BaseParser):
    def matches_operator(self, record, field_selector, pattern):
        return bool(re.search(pattern, getattr(record, field_selector["var"])))

    def register_operations(self, logic_evaluator):
        logic_evaluator.add_operation("regex_matches", self.matches_operator)