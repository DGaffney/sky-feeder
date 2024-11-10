import re
from server.algos.base import BaseParser
from server.logic_evaluator import LogicEvaluator

def resolve_path(obj, path):
    """
    Resolve a JSONPath-like path on a given object.
    
    Args:
        obj (Any): The root object to start traversing.
        path (str): Dot/bracket notation path, e.g., "posts[0].blah.foo".

    Returns:
        Any: The value at the end of the path, or None if the path is invalid.
    """
    try:
        for part in re.split(r'\.(?![^\[]*\])', path):  # Split by '.' but ignore within brackets
            # Check for list indexing, e.g., 'posts[0]'
            match = re.match(r'([a-zA-Z_]\w*)\[(\d+)\]$', part)
            if match:
                attr, index = match.groups()
                obj = getattr(obj, attr)[int(index)]
            else:
                obj = getattr(obj, part)
        return obj
    except (AttributeError, IndexError, TypeError, KeyError) as e:
        print(f"Path resolution error for '{path}': {e}")
        return None

class AttributeParser(BaseParser):
    def __init__(self):
        pass

    def attribute_compare(self, record, create_info, field_selector, operator, target_value):
        """Resolve the attribute path and apply a comparison operation using LogicEvaluator.compare."""
        value = resolve_path(record, field_selector["var"])
        return LogicEvaluator.compare(value, operator, target_value)

    def register_operations(self, logic_evaluator):
        # Register attribute comparison operation
        logic_evaluator.add_operation("attribute_compare", self.attribute_compare)
