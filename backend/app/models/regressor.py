"""
XGBoost Dosage Regressor wrapper.
Loads the saved bundle from ml/saved_models/xgb_regressor.joblib
and provides nitrogen demand estimation (kg/ha) with Urea & DAP conversions.
"""
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np


class NitrogenRegressor:
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Regressor model file not found at {self.model_path}")

        bundle = joblib.load(self.model_path)
        self.model = bundle["model"]
        self.feature_columns = bundle["feature_columns"]
        self.categorical_features = bundle["categorical_features"]
        self.numerical_features = bundle["numerical_features"]
        self.category_mappings = bundle.get("category_mappings", {})

    def predict(self, feature_dict: Dict[str, Any], field_area_ha: float = 1.0) -> Dict[str, float]:
        """
        Accepts a dictionary of features and field area (ha),
        returns dosage calculations:
            recommended_N_kg_ha: Optimal elemental N (kg/ha)
            immediate_N_kg_ha: 40% initial split
            post_irrigation_N_kg_ha: 60% subsequent split
            urea_kg_ha: Standard urea requirement (46% N)
            dap_kg_ha: DAP supplement (18% N)
            total_urea_field_kg: Scaled to field area
            total_dap_field_kg: Scaled to field area
        """
        df = pd.DataFrame([feature_dict])

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

        raw_pred = float(self.model.predict(X)[0])
        # Biological bounds
        n_rec = max(0.0, min(160.0, raw_pred))

        immediate_n = round(n_rec * 0.40, 2)
        post_irrig_n = round(n_rec * 0.60, 2)

        # Fertilizer chemical conversions
        urea_per_ha = round(n_rec / 0.46, 2)
        dap_per_ha = round((n_rec * 0.25) / 0.18, 2)

        area = max(0.01, float(field_area_ha))

        return {
            "recommended_N_kg_ha": round(n_rec, 2),
            "immediate_N_kg_ha": immediate_n,
            "post_irrigation_N_kg_ha": post_irrig_n,
            "urea_kg_ha": urea_per_ha,
            "dap_kg_ha": dap_per_ha,
            "total_urea_field_kg": round(urea_per_ha * area, 2),
            "total_dap_field_kg": round(dap_per_ha * area, 2),
            "field_area_ha": round(area, 2),
        }
