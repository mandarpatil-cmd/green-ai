"""Model management for Green AI Agent.
Handles loading and caching of machine learning models.
"""
from pathlib import Path
import joblib
from typing import Dict, Any

from backend.config import SKLEARN_MODEL_PATH, MODELS_PATH

_model_cache: Dict[str, Any] = {}

def get_sklearn_model():
    """Get the scikit-learn model, loading it if necessary."""
    if 'sklearn' not in _model_cache:
        model_path = Path(SKLEARN_MODEL_PATH)
        if model_path.exists():
            try:
                _model_cache['sklearn'] = joblib.load(model_path)
            except Exception as e:
                print(f"Error loading sklearn model: {e}")
                return None
        else:
            print(f"Sklearn model not found at {model_path}")
            return None
    return _model_cache['sklearn']

def save_sklearn_model(model: Any) -> bool:
    """Save a scikit-learn model to the models directory."""
    try:
        # Ensure models directory exists
        Path(MODELS_PATH).mkdir(parents=True, exist_ok=True)
        
        # Save the model
        joblib.dump(model, SKLEARN_MODEL_PATH)
        
        # Update cache
        _model_cache['sklearn'] = model
        return True
    except Exception as e:
        print(f"Error saving sklearn model: {e}")
        return False