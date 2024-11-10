Sky-Feeder
======================================================

> Feed Generators are services that provide custom algorithms to users through the AT Protocol.

Powered by [The AT Protocol SDK for Python](https://github.com/MarshalX/atproto)

This project is a forked version of the original [ATProto Feed Generator](https://github.com/bluesky-social/feed-generator). It extends that functionality by:

- Adding a web portal for creating and manipulating feeds,
- Establishing a "feed manifest" syntax for expressing the rule set for any type of algorithmic recipe for a feed,
- Creating algorithm "operators" that generate boolean results for different types of comparisons to be made against the skeet stream

A public-facing site that anyone can use to create their own feeds is currently available at the [Hellofeed](https://hellofeed.cognitivesurpl.us/) demo site. To learn more about feed generators please [review this documentation](https://github.com/bluesky-social/feed-generator#overview).

Key Features
------------

-   **Rule Chaining**: Supports chaining multiple rules using logical operators like `AND` and `OR` to build complex conditions for feed filtration.
-   **Regex Evaluation**: Utilize regular expressions to match patterns within the data feed content.
-   **Transformer Similarities**: Integrate transformer models for semantic text similarity analysis.
-   **Social Graph Filtering**: Select/Reject skeets based on follower/following graph properties.
-   **Attribute Matching**: Select/Reject skeets based on direct comparison on properties of the skeet stream.
-   **ML Probability Assessments**: Calculate probabilities based on feature evaluations using ML models to classify and filter data.
-   **Modular Design**: Facilitates the addition of new models and rule types with minimal changes to existing code.

Getting Started
---------------

We've set up this server with Postgres to store and query data. Feel free to switch this out for whichever database you prefer.

### Prerequisites

-   Python 3.7+
-   Optionally, create a virtual environment.
-   Can run as Dockerized set up

### Installation

Install dependencies:

`pip install -r requirements.txt`

Copy `.env.example` as `.env`. Fill in the variables.

### Implementing Logic

Next, you will need to do two things:

1.  **JetStream ingest** in `server/data_filter.py`.
2.  **Skeet Filtering Logic** in `server/algos`.
    -   Use the provided `algorithm_manifest.json.example` file as the configuration blueprint for deploying the feed algorithms.
    -   The `algorithm_manifest.json.example` contains definitions of models, their configurations, and how they interlink through rules to filter data.
3. **Management Layer** in `server/app.py`, `server/database.py` and files referenced from there on.

### Algorithm Manifest

#### `algorithm_manifest.json`

The `algorithm_manifest.json` file serves as the configuration blueprint for deploying the feed algorithms. In our implementation, we store algorithm manifests against `UserAlgorithm` objects, but these can be applied any other way you'd prefer. It contains the definition of models, their respective configurations, and how they interlink through rules to filter data. To learn more about the full set of available operators please review the [manifest documentation](https://github.com/DGaffney/sky-feeder/blob/main/MANIFEST_DOC.md).

##### Structure

-   **`filter`**: Defines the condition set used for evaluating each feed item. The conditions use operations like `regex_matches`, `text_similarity`, and `model_probability`.
-   **`models`**: Lists the ML models used along with their feature modules. Note that, for any model, you *must* provide the correct definition for a model as well as its feature modules in the correct order. We'll make that unnecessary later... at some point. Each model declaration includes:
    -   `model_name`: Unique identifier for the ML model.
    -   `training_file`: Source data used for model training.
    -   `feature_modules`: Features used to generate the necessary input vector for ML predictions.
-   **`author`**: Provides credentials to authenticate the model-building process and social graph traversals.

##### Example

```json
{
  "filter": {
    "and": [
      {
        "regex_matches": [
          {"var": "text"},
          "\\bimportant\\b"
        ]
      },
      {
        "regex_negation_matches": [
          {"var": "text"},
          "\\bunwanted_term\\b"
        ]
      },
      {
        "social_graph": [
          "devingaffney.com",
          "is_in",
          "follows",
        ]
      },
      {
        "text_similarity": [
          {"var": "text"},
          {
            "model_name": "all-MiniLM-L6-v2",
            "anchor_text": "This is an important update"
          },
          ">=",
          0.3
        ]
      },
      {
        "model_probability": [
          {"model_name": "toxicity_model"},
          ">=",
          0.9
        ]
      }
    ]
  },
  "models": [
    {
      "model_name": "toxicity_model",
      "training_file": "prototype_labeled_dataset.json",
      "feature_modules": [
        {"type": "time_features"},
        {"type": "vectorizer", "model_name": "all-MiniLM-L6-v2"},
        {"type": "post_metadata"}
      ]
    }
  ],
  "author": {
    "username": "user",
    "password": "pass"
  }
}
```

Running the Server
------------------

Run the development FastAPI server:

`uvicorn $APP_MODULE --host $HOST --port $PORT`

> **Note** Duplication of data stream instances in debug mode is fine. Read the warning below.

> **Warning** In production, you should use a production WSGI server instead.

> **Warning** If you want to run the server with multiple workers, you should run the Data Stream (Firehose) separately.

### Bluesky-Facing Endpoints

-   `/.well-known/did.json`
-   `/xrpc/app.bsky.feed.describeFeedGenerator`
-   `/xrpc/app.bsky.feed.getFeedSkeleton`

Major Enhancements
------------------

1.  **Logic Evaluation**: Integrated a Logic Evaluator in Python that applies JSON-like conditions using registered operations such as regex matching, text similarity, and model probability calculation.

2.  **Algorithmic Operator Implementations in Python**: Implemented key classes like `AttributeParser`, `ProbabilityParser`, `RegexParser`, `SocialParser`, and `TransformerParser` which handle respective tasks and provide operations for evaluation.

3.  **Feature Generation**: The `FeatureGenerator` class captures various features such as vectorized text using transformer models, metadata, and temporal features, which enrich the ML model inputs.

4.  **Compatibility with AT Protocol**: The generator interfaces seamlessly with the AT Protocol for publishing and managing feed generators.

5.  **Enhanced Model Management**: Support for XGBoost and transformer models, including features for model training, evaluation, and inference.

