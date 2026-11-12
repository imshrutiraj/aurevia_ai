"""Loader for the bundled job-role classifier.

backend/job_predictor.py looks for the classifier at
Config.SAVED_MODEL_DIR/job_predictor_model.pkl and calls
train_and_save_model() when that file is missing. The repository ships the
already-trained scikit-learn pipeline at the project root
(job_predictor_model.pkl), so this function loads that artifact instead of
retraining from the dataset.
"""
import os

import joblib

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_MODEL_PATH = os.path.join(ROOT_DIR, "job_predictor_model.pkl")


def train_and_save_model():
    """Return (pipeline, metrics) for the bundled classifier."""
    pipeline = joblib.load(BUNDLED_MODEL_PATH)
    return pipeline, {}
