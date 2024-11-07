import json
from json_logic import jsonLogic
from algos.algo import probability, regex, transformer
jsonlogic.add_operation("probability", probability)
jsonlogic.add_operation("regex", regex)
jsonlogic.add_operation("transformer", transformer)

ALGO_MANIFEST = json.loads(open("algo_manifest.json").read())

def find_relevant_conditions(rule, operator_name):
    """
    Recursively search a JSONLogic rule set for any instance of a specified operator.
    
    Args:
        rule (dict): The JSONLogic rule set to search.
        operator_name (str): The name of the operator to find (default is "xgboost_probability").

    Returns:
        list: A list of all conditions that use the specified operator.
    """
    found_conditions = []
    # If the current rule is a dictionary, look for the operator at this level
    if isinstance(rule, dict):
        for key, value in rule.items():
            # If this rule is the target operator, add it to the results
            if key == operator_name:
                found_conditions.append(rule)
            # Otherwise, recurse into nested rules
            elif isinstance(value, (dict, list)):
                found_conditions.extend(find_relevant_conditions(value, operator_name))
    # If the current rule is a list, check each item
    elif isinstance(rule, list):
        for item in rule:
            found_conditions.extend(find_relevant_conditions(item, operator_name))
    return found_conditions
