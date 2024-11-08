import json
import json_logic

class BaseParser:
    def register_operations(self):
        """Register operations specific to each parser."""
        raise NotImplementedError("Subclasses must implement register_operations")

# # Load the JSONLogic manifest
# with open("algo_manifest.json") as f:
#     ALGO_MANIFEST = json.load(f)

# # main.py
# from server.algos import algo_manager
#
# record = {"status": "active", "text": "This is important", "features": [0.3, 1.5, 2.7]}
# rule = {
#     "and": [
#         {"probability_with_operator": [{"model_name": "probability_toxic", "features": {"var": "features"}}, ">=", 0.9]},
#         {"matches": [{"var": "text"}, r"\bimportant\b"]},
#         {
#             "text_similarity": [
#                 {"model_name": "all-MiniLM-L6-v2", "text1": {"var": "text"}, "text2": "This is an important update"},
#                 0.8
#             ]
#         }
#     ]
# }

# # Evaluate the rule
# is_match = algo_manager.adjudicate(rule, record)
# print(is_match)  # Outputs True or False based on the rule evaluation

# # Initialize the manager
# algo_manager = AlgoManager()
#
# import json
# from json_logic import json_logic
# from server.algos import probability, regex, transformer
# json_logic.add_operation("probability_with_operator", probability.probability_with_operator)
# json_logic.add_operation("regex", regex.matches_operator)
# json_logic.add_operation("transformer", transformer.text_similarity_operator)
#
# ALGO_MANIFEST = json.loads(open("algo_manifest.json").read())
# # rule = {
# #     "and": [
# #         {"==": [{"var": "status"}, "active"]},
# #         {"matches": [{"var": "text"}, r"\bimportant\b"]}  # Check if 'text' contains the word "important"
# #     ]
# # }
# # rule = {
# #     "and": [
# #         {"probability_with_operator": [{"model_name": "probability_toxic", "features": {"var": "features"}}, ">=", 0.9]},
# #         {"probability_with_operator": [{"model_name": "probability_funny", "features": {"var": "features"}}, "==", 0.7]}
# #     ]
# # }
# # rule = {
# #     "and": [
# #         {"==": [{"var": "status"}, "active"]},
# #         {
# #             "text_similarity": [
# #                 {
# #                     "model_name": "all-MiniLM-L6-v2",
# #                     "text1": {"var": "text"},
# #                     "text2": "This is an important update"
# #                 },
# #                 0.8  # Threshold for similarity
# #             ]
# #         }
# #     ]
# # }
# MODELS = {}
#
# def hydrate_resources():
#     # Load all models from the models/ directory
#     models_path = "models/"
#     for rule in find_relevant_conditions(ALGO_MANIFEST, "probability"):
#         model_dir = os.path.join(models_path, rule["model_name"])
#         if os.path.isdir(model_dir):
#             model = xgb.Booster()
#             model.load_model(os.path.join(model_dir, "model.json"))
#             MODELS[rule["model_name"]] = model
#
# def find_relevant_conditions(rule, operator_name):
#     """
#     Recursively search a JSONLogic rule set for any instance of a specified operator.
#
#     Args:
#         rule (dict): The JSONLogic rule set to search.
#         operator_name (str): The name of the operator to find (default is "xgboost_probability").
#
#     Returns:
#         list: A list of all conditions that use the specified operator.
#     """
#     found_conditions = []
#     # If the current rule is a dictionary, look for the operator at this level
#     if isinstance(rule, dict):
#         for key, value in rule.items():
#             # If this rule is the target operator, add it to the results
#             if key == operator_name:
#                 found_conditions.append(rule)
#             # Otherwise, recurse into nested rules
#             elif isinstance(value, (dict, list)):
#                 found_conditions.extend(find_relevant_conditions(value, operator_name))
#     # If the current rule is a list, check each item
#     elif isinstance(rule, list):
#         for item in rule:
#             found_conditions.extend(find_relevant_conditions(item, operator_name))
#     return found_conditions
