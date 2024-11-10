ATProto Feed Generator with Advanced Algorithmic Logic
======================================================

> Feed Generators are services that provide custom algorithms to users through the AT Protocol.

Powered by [The AT Protocol SDK for Python](https://github.com/MarshalX/atproto)

This project is a forked version of the original [ATProto Feed Generator](https://github.com/bluesky-social/feed-generator). It distinguishes itself by incorporating advanced algorithmic logic that allows for chaining diverse types of rules, including regular expressions, transformer similarities, and machine learning (ML) probabilities. These enhancements empower the generator to apply sophisticated analytics on data feeds to curate and filter them intelligently.

[Official overview of Feed Generators](https://github.com/bluesky-social/feed-generator#overview) *(read it first)*

Key Features
------------

-   **Rule Chaining**: Supports chaining multiple rules using logical operators like `AND` and `OR` to build complex conditions for feed filtration.

-   **Regex Evaluation**: Utilize regular expressions to match patterns within the data feed content.

-   **Transformer Similarities**: Integrate transformer models for semantic text similarity analysis.

-   **ML Probability Assessments**: Calculate probabilities based on feature evaluations using ML models to classify and filter data.

-   **Modular Design**: Facilitates the addition of new models and rule types with minimal changes to existing code.

Getting Started
---------------

We've set up this server with SQLite to store and query data. Feel free to switch this out for whichever database you prefer.

### Prerequisites

-   Python 3.7+
-   Optionally, create a virtual environment.

### Installation

Install dependencies:

`pip install -r requirements.txt`

Copy `.env.example` as `.env`. Fill in the variables.

> **Note** To get the value for `FEED_URI`, you should publish the feed first.

### Implementing Logic

Next, you will need to do two things:

1.  **Implement indexing logic** in `server/data_filter.py`.

2.  **Implement feed generation logic** in `server/algos`.

    -   Use the provided `algorithm_manifest.json` file as the configuration blueprint for deploying the feed algorithms.
    -   The `algorithm_manifest.json` contains definitions of models, their configurations, and how they interlink through rules to filter data.

We've taken care of setting this server up with a `did:web`. However, you're free to switch this out for `did:plc` if you like---this may be preferable if you expect this Feed Generator to be long-standing and possibly migrating domains.

### Algorithm Manifest

#### `algorithm_manifest.json`

The `algorithm_manifest.json` file serves as the configuration blueprint for deploying the feed algorithms. It contains the definition of models, their respective configurations, and how they interlink through rules to filter data.

##### Structure

-   **`filter`**: Defines the condition set used for evaluating each feed item. The conditions use operations like `regex_matches`, `text_similarity`, and `model_probability`.

-   **`models`**: Lists the ML models used along with their feature modules. Each model declaration includes:

    -   `model_name`: Unique identifier for the ML model.
    -   `training_file`: Source data used for model training.
    -   `feature_modules`: Features used to generate the necessary input vector for ML predictions.
-   **`author`**: Provides credentials to authenticate the model-building process.

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

Publishing Your Feed
--------------------

To publish your feed, go to the script at `publish_feed.py` and fill in the variables at the top. Examples are included, and some are optional. To publish your feed generator, simply run:

`python publish_feed.py`

To update your feed's display data (name, avatar, description, etc.), just update the relevant variables and re-run the script.

After successfully running the script, you should be able to see your feed from within the app, as well as share it by embedding a link in a post (similar to a quote post).

Running the Server
------------------

Run the development FastAPI server:

`uvicorn $APP_MODULE --host $HOST --port $PORT`

> **Note** Duplication of data stream instances in debug mode is fine. Read the warning below.

> **Warning** In production, you should use a production WSGI server instead.

> **Warning** If you want to run the server with multiple workers, you should run the Data Stream (Firehose) separately.

### Endpoints

-   `/.well-known/did.json`
-   `/xrpc/app.bsky.feed.describeFeedGenerator`
-   `/xrpc/app.bsky.feed.getFeedSkeleton`

Major Enhancements
------------------

1.  **Logic Evaluation**: Integrated a Logic Evaluator in Python that applies JSON-like conditions using registered operations such as regex matching, text similarity, and model probability calculation.

2.  **Algorithms Implementation in Python**: Implemented key classes like `AlgoManager`, `ProbabilityParser`, `RegexParser`, and `TransformerParser` which handle respective tasks and provide operations for evaluation.

3.  **Feature Generation**: The `FeatureGenerator` class captures various features such as vectorized text using transformer models, metadata, and temporal features, which enrich the ML model inputs.

4.  **Compatibility with AT Protocol**: The generator interfaces seamlessly with the AT Protocol for publishing and managing feed generators.

5.  **Enhanced Model Management**: Support for XGBoost and transformer models, including features for model training, evaluation, and inference.

Conclusion
----------

This project significantly extends the capabilities of the original feed generator. By deploying advanced algorithmic features, it positions itself as a dynamic and flexible system for curating data feeds using state-of-the-art machine learning techniques. Further development can explore deeper integration with additional ML models and enhanced scalability for high-volume data operations.

License
-------

MIT