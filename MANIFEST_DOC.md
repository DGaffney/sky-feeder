# Algorithm Manifest Documentation

This document explains how to define an algorithm manifest for our system, which supports four types of algorithms:

1.  **Attribute Comparison** (`attribute_compare`)
2.  **Regular Expression Matching** (`regex_matches` and `regex_negation_matches`)
3.  **Text Similarity** (`text_similarity`)
4.  **Model Probability** (`model_probability`)

Each manifest includes a `filter` section where you define the logic for filtering records, and a `models` section where you configure machine learning models and feature extraction.

## General Structure

A manifest is defined as a JSON object with two main sections:

-   `filter`: Contains conditions that specify when the algorithm should classify a record as a match. Each condition type has its own syntax.
-   `models`: Defines the machine learning models and associated feature modules used by `model_probability`.

## Example Manifest

```json
{
    "filter": {
        "and": [
            {
                "attribute_compare": [
                    {
                        "var": "embed.external.uri"
                    },
                    "==",
                    "https://www.youtube.com/watch?v=E8Ew6K0W3RY"
                ]
            },
            {
                "regex_matches": [
                    {
                        "var": "text"
                    },
                    "\\bthe\\b"
                ]
            },
            {
                "regex_negation_matches": [
                    {
                        "var": "text"
                    },
                    "\\bunwanted_term\\b"
                ]
            },
            {
                "text_similarity": [
                    {
                        "var": "text"
                    },
                    {
                        "anchor_text": "This is an important update",
                        "model_name": "all-MiniLM-L6-v2"
                    },
                    ">=",
                    0.3
                ]
            },
            {
                "model_probability": [
                    {
                        "model_name": "news_without_science"
                    },
                    ">=",
                    0.9
                ]
            }
        ]
    },
    "models": [
        {
            "feature_modules": [
                {
                    "type": "time_features"
                },
                {
                    "model_name": "all-MiniLM-L6-v2",
                    "type": "vectorizer"
                },
                {
                    "type": "post_metadata"
                }
            ],
            "model_name": "news_without_science"
        }
    ]
}
```

## Filter Section

The `filter` section defines the logical structure of the filtering criteria. Each criterion checks specific attributes, matches patterns, or evaluates machine learning models based on record data.

### 1\. Attribute Comparison

The `attribute_compare` operation allows comparing an attribute of a record to a target value.

-   **Syntax**:

```json
{
    "attribute_compare": [
        {
            "var": "<attribute_path>"
        },
        "<operator>",
        "<target_value>"
    ]
}
```

-   **Fields**:
    -   `var`: Specifies the JSONPath-like path to the attribute in the record.
    -   `<operator>`: Comparison operator (e.g., `==`, `>`, `>=`, `<`, `<=`).
    -   `<target_value>`: The target value to compare the attribute against.
-   **Example**:

    json

    Copy code

    `{
        "attribute_compare": [
            {
                "var": "posts[0].blah.foo"
            },
            "==",
            "bar"
        ]
    }`

### 2\. Regular Expression Matching

The `regex_matches` and `regex_negation_matches` operations match or negate a regular expression pattern in an attribute's value.

-   **Syntax**:

```json
{
    "regex_matches": [
        {
            "var": "<attribute_path>"
        },
        "<regex_pattern>"
    ]
}
```

-   **Fields**:

    -   `var`: Specifies the JSONPath-like path to the attribute in the record.
    -   `<regex_pattern>`: A regular expression pattern to match against.
-   **Examples**:
    
```json
{
    "regex_matches": [
        {
            "var": "text"
        },
        "\\bthe\\b"
    ]
}
```

```json
{
    "regex_negation_matches": [
        {
            "var": "text"
        },
        "\\bunwanted_term\\b"
    ]
}
```

### 3\. Text Similarity

The `text_similarity` operation evaluates the similarity between the text in an attribute and an anchor text using a transformer model.

-   **Syntax**:

```json
{
    "text_similarity": [
        {
            "var": "<attribute_path>"
        },
        {
            "anchor_text": "<reference_text>",
            "model_name": "<transformer_model_name>"
        },
        "<operator>",
        "<threshold>"
    ]
}
```

-   **Fields**:

    -   `var`: Path to the text attribute in the record.
    -   `anchor_text`: The reference text to compare.
    -   `model_name`: The name of the transformer model used for embeddings.
    -   `<operator>`: Comparison operator, typically `>=` for similarity.
    -   `<threshold>`: The similarity threshold.
-   **Example**:

```json
{
    "text_similarity": [
        {
            "var": "text"
        },
        {
            "anchor_text": "This is an important update",
            "model_name": "all-MiniLM-L6-v2"
        },
        ">=",
        0.3
    ]
}
```

### 4\. Model Probability

The `model_probability` operation evaluates the likelihood that a record matches a specific classification using an XGBoost model.

-   **Syntax**:

    json

    Copy code

```json
{
    "model_probability": [
        {
            "model_name": "<xgboost_model_name>"
        },
        "<operator>",
        "<threshold>"
    ]
}
```

-   **Fields**:

    -   `model_name`: The name of the XGBoost model used for classification.
    -   `<operator>`: Comparison operator (e.g., `>=` for probability).
    -   `<threshold>`: Probability threshold to determine if the record meets the condition.
-   **Example**:

```json
{
    "model_probability": [
        {
            "model_name": "news_without_science"
        },
        ">=",
        0.9
    ]
}
```

## Models Section

The `models` section defines machine learning models used in `model_probability`. Each model entry specifies the model name, feature modules, and configuration. Currently, the only model provided is `news_without_science`, an XGBoost classifier trained on ≈100 news article skeets and ≈100 science-based skeets. In the guts of this codebase is the ability to train new models, but its _very early_. Expect (a) lots of ML modules to be made available over time and (b) the ability to easily train and deploy modules yourself via the site.

-   **Fields**:

    -   `model_name`: The unique name of the model, referenced in `model_probability`.
    -   `feature_modules`: An array defining the feature extraction modules for the model.
        -   `type`: The type of feature (e.g., `"time_features"`, `"post_metadata"`).
        -   `model_name`: (Optional) Model used for vectorizing, typically with type `"vectorizer"`.
-   **Example**:

```json
"models": [
    {
        "feature_modules": [
            {
                "type": "time_features"
            },
            {
                "model_name": "all-MiniLM-L6-v2",
                "type": "vectorizer"
            },
            {
                "type": "post_metadata"
            }
        ],
        "model_name": "news_without_science"
    }
]
```


## Comparator Reference

In the `LogicEvaluator` class, comparisons between values are handled by the `compare` method, which supports several common operators. Each operator is used to compare a given `value` to a specified `threshold`. Here's a breakdown of how each comparator works:

### Available Comparators

1.  **Equality (`==`)**

    -   **Description**: Checks if `value` is equal to `threshold`.
    -   **Usage**: Use this comparator when you want an exact match.
    -   **Example**: If `value == 10` and `threshold == 10`, the result is `True`.
    -   **Code**: `value == threshold`
2.  **Greater Than or Equal (`>=`)**

    -   **Description**: Checks if `value` is greater than or equal to `threshold`.
    -   **Usage**: Use this comparator to ensure `value` meets or exceeds a minimum requirement.
    -   **Example**: If `value == 10` and `threshold == 5`, the result is `True`. If `value == 5` and `threshold == 5`, the result is also `True`.
    -   **Code**: `value >= threshold`
3.  **Less Than or Equal (`<=`)**

    -   **Description**: Checks if `value` is less than or equal to `threshold`.
    -   **Usage**: Use this comparator to ensure `value` does not exceed a maximum limit.
    -   **Example**: If `value == 3` and `threshold == 5`, the result is `True`. If `value == 5` and `threshold == 5`, the result is also `True`.
    -   **Code**: `value <= threshold`
4.  **Greater Than (`>`)**

    -   **Description**: Checks if `value` is strictly greater than `threshold`.
    -   **Usage**: Use this comparator when `value` must be higher than `threshold`.
    -   **Example**: If `value == 10` and `threshold == 5`, the result is `True`. If `value == 5` and `threshold == 5`, the result is `False`.
    -   **Code**: `value > threshold`
5.  **Less Than (`<`)**

    -   **Description**: Checks if `value` is strictly less than `threshold`.
    -   **Usage**: Use this comparator when `value` must be lower than `threshold`.
    -   **Example**: If `value == 3` and `threshold == 5`, the result is `True`. If `value == 5` and `threshold == 5`, the result is `False`.
    -   **Code**: `value < threshold`

### Error Handling

If an unsupported operator is passed to `compare`, it raises a `ValueError`, ensuring only defined comparisons are allowed. The error message explicitly states the unknown operator, making debugging easier.

**Example Error Message**:

```python
raise ValueError(f"Unknown comparator '{operator}'")
```
