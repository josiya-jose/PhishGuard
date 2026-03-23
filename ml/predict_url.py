import joblib
import pandas as pd
import shap
import numpy as np
from catboost import CatBoostClassifier

from ml.feature_extractor import extract_features, get_feature_names

# Paths (your structure)
LGBM_PATH = "ml/lgbm_model.pkl"
CAT_PATH = "ml/catboost_model.cbm"

# Load Meghna models
lgb_model = joblib.load(LGBM_PATH)

cat_model = CatBoostClassifier()
cat_model.load_model(CAT_PATH)

# SHAP
explainer = shap.TreeExplainer(lgb_model)

THRESHOLD = 0.5


def predict_url(url: str):

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Meghna features
    features_dict = extract_features(url)
    feature_cols = get_feature_names()

    X = pd.DataFrame([[features_dict[col] for col in feature_cols]],
                     columns=feature_cols).fillna(0)

    # Probabilities (same logic)
    lgb_prob = float(lgb_model.predict_proba(X)[0][1])
    cat_prob = float(cat_model.predict_proba(X)[0][1])

    R = float((lgb_prob + cat_prob) / 2.0)
    prediction = "Phishing" if R >= THRESHOLD else "Legitimate"
    risk_score = float(round(R * 100, 2))
    confidence_raw = max(R, 1 - R)
    confidence = float(round(confidence_raw, 4))
    anti_phishing_score = float(round((1 - R) * confidence_raw * 100, 2))

    if R >= 0.7:
        risk_level = "High Risk"
    elif R >= 0.4:
        risk_level = "Medium Risk"
    else:
        risk_level = "Low Risk"

    # SHAP (unchanged)
    try:
        shap_values = explainer.shap_values(X)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_output = []

        for i, feature in enumerate(X.columns):
            shap_output.append({
                "feature": feature,
                "value": float(X.iloc[0, i]),
                "shap_value": float(shap_values[0][i])
            })

        if isinstance(explainer.expected_value, (list, np.ndarray)):
            base_value = float(explainer.expected_value[1])
        else:
            base_value = float(explainer.expected_value)

    except Exception:
        shap_output = []
        base_value = 0.0

    return {
        "url": url,
        "prediction": prediction,
        "probability": round(R, 4),
        "confidence": confidence,
        "risk_score": risk_score,
        "anti_phishing_score": anti_phishing_score,  # ✅ NEW
        "risk_level": risk_level,
        "threshold": THRESHOLD,
        "shap_values": shap_output,
        "base_value": base_value
    }