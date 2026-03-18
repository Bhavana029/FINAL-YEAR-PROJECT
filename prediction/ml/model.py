import numpy as np
from .labels import LABELS
import joblib
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "prediction", "ml", "bloodeye_model.pkl")

def mock_model_predict(features):
    probs = np.random.dirichlet(np.ones(len(LABELS)), size=1)[0]
    return dict(zip(LABELS, probs))
    
def load_model():
    return joblib.load(MODEL_PATH)
