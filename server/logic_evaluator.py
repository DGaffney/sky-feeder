class LogicEvaluator:
    def __init__(self):
        self.operations = {}

    def add_operation(self, name, func):
        """Registers a custom operation."""
        self.operations[name] = func

    def evaluate(self, condition, record):
        """Evaluates a JSON-like condition structure."""
        if "and" in condition:
            return all(self.evaluate(cond, record) for cond in condition["and"])
        elif "or" in condition:
            return any(self.evaluate(cond, record) for cond in condition["or"])
        else:
            for op, params in condition.items():
                if op in self.operations:
                    return self.operations[op](record, *params)
            raise ValueError(f"Unknown operation '{op}'")

    @staticmethod
    def compare(value, operator, threshold):
        """Performs comparison based on the specified operator."""
        if operator == "==":
            return value == threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        else:
            raise ValueError(f"Unknown comparator '{operator}'")
