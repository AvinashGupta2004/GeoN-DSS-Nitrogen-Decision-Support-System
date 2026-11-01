"""
LightGBM Safety Classifier wrapper.
Loads the saved bundle from ml/saved_models/lgbm_classifier.joblib
and provides prediction, probabilities, and class label explanations.
"""
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np


class NitrogenClassifier:
    CLASS_MAP = {
        0: "NO-GO (Leaching Risk)",
        1: "NO-GO (Fertilizer Burn Risk)",
        2: "GO (Safe Window)"
    }

    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Classifier model file not found at {self.model_path}")

        bundle = joblib.load(self.model_path)
        self.model = bundle["model"]
        self.feature_columns = bundle["feature_columns"]
        self.categorical_features = bundle["categorical_features"]
        self.numerical_features = bundle["numerical_features"]
        self.category_mappings = bundle.get("category_mappings", {})

    def predict(self, feature_dict: Dict[str, Any]) -> Tuple[int, Dict[str, float], str]:
        """
        Accepts a dictionary of features, prepares DataFrame,
        returns:
            predicted_class (int: 0, 1, or 2)
            probabilities (dict: {class_label: float})
            class_description (str)
        """
        df = pd.DataFrame([feature_dict])

        # Ensure all required features are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = np.nan

        # Format types with exact training categorical categories
        for col in self.categorical_features:
            cats = self.category_mappings.get(col)
            if cats:
                df[col] = pd.Categorical(df[col], categories=cats)
            else:
                df[col] = df[col].astype("category")

        for col in self.numerical_features:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        X = df[self.feature_columns]

        predicted_class = int(self.model.predict(X)[0])
        probs = self.model.predict_proba(X)[0]

        prob_dict = {
            "p_leach_risk_0": round(float(probs[0]), 4),
            "p_burn_risk_1": round(float(probs[1]), 4),
            "p_safe_window_2": round(float(probs[2]), 4)
        }

        return predicted_class, prob_dict, self.CLASS_MAP.get(predicted_class, "Unknown")
