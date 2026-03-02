import joblib
import shap
import numpy as np
from urllib.parse import urlparse

from ml.feature_engineering.extract_url_features import extract_features


# ==========================================================
# LOAD MODELS (Loaded once when server starts)
# ==========================================================

cat_model = joblib.load("ml/models/catboost_phishing_model.pkl")
lgb_model = joblib.load("ml/models/lightgbm_phishing_model.pkl")

explainer = shap.TreeExplainer(lgb_model)

THRESHOLD = 0.5


# ==========================================================
# URL NORMALIZER (UPDATED)
# ==========================================================

def normalize_url(url: str) -> str:
    url = url.strip()

    # Handle defanged phishing URLs
    url = url.replace("[.]", ".")
    url = url.replace("(.)", ".")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


# ==========================================================
# URL VALIDATOR (SAFE VERSION)
# ==========================================================

def validate_url(url: str):
    try:
        parsed = urlparse(url)

        if not parsed.netloc or "." not in parsed.netloc:
            raise ValueError("Invalid domain format.")

    except Exception:
        raise ValueError("Invalid URL. Please enter a valid website link.")


# ==========================================================
# MAIN PREDICTION FUNCTION
# ==========================================================

def predict_url(url: str):

    # Normalize
    url = normalize_url(url)

    # Validate safely
    validate_url(url)

    # Feature Extraction
    X = extract_features(url)

    if not hasattr(X, "columns"):
        raise ValueError("Feature extraction failed.")
    
    print("--------------------------------------------------")
    print("URL:", url)
    print("Features:", X.iloc[0].to_dict())
    print("--------------------------------------------------")

    # LightGBM probability
    if hasattr(lgb_model, "predict_proba"):
        P1 = float(lgb_model.predict_proba(X)[0][1])
    else:
        P1 = float(lgb_model.predict(X)[0])

    # CatBoost probability
    P2 = float(cat_model.predict_proba(X)[0][1])

    # Ensemble probability
    R = (P1 + P2) / 2.0

    # Classification
    prediction = "Phishing" if R >= THRESHOLD else "Legitimate"

    # Risk Score (0–100)
    risk_score = round(R * 100, 2)

    # Confidence (certainty of prediction)
    confidence = round(max(R, 1 - R), 4)

    # Risk Level
    if R >= 0.7:
        risk_level = "High Risk"
    elif R >= 0.4:
        risk_level = "Medium Risk"
    else:
        risk_level = "Low Risk"

    # SHAP Explanation
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
        "risk_level": risk_level,
        "threshold": THRESHOLD,
        "shap_values": shap_output,
        "base_value": base_value
    }