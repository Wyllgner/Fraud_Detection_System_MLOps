# src/api/model.py

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from mlflow import MlflowClient
from config import MLFLOW_TRACKING_URI, MODEL_NAME


_model = None
_feature_names = None


def load_model():
    global _model, _feature_names

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    if not versions:
        raise RuntimeError(f"no registered model found with name '{MODEL_NAME}'")

    latest = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
    model_uri = f"models:/{MODEL_NAME}/{latest.version}"
    print(f"  loading version {latest.version} from {model_uri}")

    _model = mlflow.sklearn.load_model(model_uri)
    _feature_names = _model.feature_name_
    print(f"  model expects {len(_feature_names)} features")

    return _model


def predict(model, data: dict) -> float:
    # build a dataframe with all expected features, defaulting missing ones to 0
    row = {feat: data.get(feat, 0) for feat in _feature_names}
    df = pd.DataFrame([row])

    prob = model.predict_proba(df)[:, 1][0]
    return float(prob)