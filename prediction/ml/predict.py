import joblib
import numpy as np
import pandas as pd
import os
import json

from .preprocess import preprocess_image
from .feature_extraction import extract_fundus_features, extract_sclera_features

BASE_DIR = os.path.dirname(__file__)

model         = joblib.load(os.path.join(BASE_DIR, "bloodeye_model.pkl"))
label_encoder = joblib.load(os.path.join(BASE_DIR, "label_encoder.pkl"))
scaler        = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))

# Load feature list saved by train.py (includes interaction features)
with open(os.path.join(BASE_DIR, "feature_names.json")) as f:
    ALL_FEATURES = json.load(f)

BASE_FEATURES = [
    "cnn_pca1", "AVR", "vessel_red", "sclera_mean",
    "AV_sat_diff", "tortuosity", "sclera_red",
    "vessel_den", "perivascular", "pulse_std"
]


def _add_interactions(d: dict) -> dict:
    """Add the same interaction features used during training."""
    d = dict(d)
    d['red_sat']     = d['vessel_red']  * d['AV_sat_diff']
    d['avr_tort']    = d['AVR']         * d['tortuosity']
    d['cnn_avr']     = d['cnn_pca1']    * d['AVR']
    d['sclera_diff'] = d['sclera_red']  - d['sclera_mean']
    d['pulse_avr']   = d['pulse_std']   * d['AVR']
    d['den_peri']    = d['vessel_den']  * d['perivascular']
    return d


def predict_blood_group(fundus_path: str, sclera_path: str) -> dict:
    # Preprocess
    fundus_img = preprocess_image(fundus_path)
    sclera_img = preprocess_image(sclera_path)

    # Extract base features
    fundus_features = extract_fundus_features(fundus_img)
    sclera_features = extract_sclera_features(sclera_img)

    # Merge and add interactions — MUST match training exactly
    combined = {**fundus_features, **sclera_features}
    combined = _add_interactions(combined)

    # Build input array in correct feature order
    X = np.array([[combined[f] for f in ALL_FEATURES]])

    # Scale using the same scaler fitted during training
    X = scaler.transform(X)

    # Predict
    probabilities    = model.predict_proba(X)[0]
    predicted_index  = int(np.argmax(probabilities))
    predicted_label  = label_encoder.inverse_transform([predicted_index])[0]

    print("Features:", {k: round(combined[k], 4) for k in BASE_FEATURES})
    print("Predicted:", predicted_label,
          f"({round(probabilities[predicted_index]*100, 2)}%)")

    return {
        "predicted_group": predicted_label,
        "confidence": round(float(probabilities[predicted_index]) * 100, 2),
        "all_probabilities": {
            label_encoder.inverse_transform([i])[0]: round(float(probabilities[i]) * 100, 2)
            for i in range(len(probabilities))
        }
    }