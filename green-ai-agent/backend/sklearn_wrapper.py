"""
Wrapper for sklearn TF-IDF + LogisticRegression pipeline saved via joblib.
Provides load_model(path) and classify(text,k=3) -> dict matching API shape used elsewhere.
"""
from __future__ import annotations
import time
import joblib
import os
from typing import List, Dict, Any

MODEL = None
MODEL_PATH = None


def load_model(path: str):
    global MODEL, MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    MODEL = joblib.load(path)
    MODEL_PATH = path
    return MODEL


def classify(text: str, k: int = 3) -> Dict[str, Any]:
    if MODEL is None:
        raise RuntimeError('Model not loaded. Call load_model(path) first.')

    start = time.time()
    # model is a pipeline: vectorizer + classifier
    clf = MODEL.named_steps[list(MODEL.named_steps.keys())[-1]]
    classes = list(clf.classes_)
    probs = MODEL.predict_proba([text])[0]
    pairs = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
    topk = pairs[:k]

    predicted_category, confidence = topk[0] if topk else ('unknown', 0.0)

    elapsed = time.time() - start
    co2_g = 0.001  # small estimate

    result = {
        'predicted_category': predicted_category,
        'confidence': float(confidence),
        'all_predictions': [{'category': p[0], 'confidence': float(p[1])} for p in pairs],
        'model_used': f'sklearn({os.path.basename(MODEL_PATH)})',
        'escalated': False,
        'escalation_attempted': False,
        'energy_metrics': {
            'co2_emissions_g': co2_g,
            'processing_time_seconds': round(elapsed, 6),
            'energy_efficiency_score': round(co2_g / max(elapsed, 1e-6), 6),
        },
        'ai_insights': {
            'environmental_impact': {
                'co2_this_classification': co2_g,
                'impact_level': 'low'
            },
            'accuracy_assessment': {
                'confidence_level': 'high' if confidence >= 0.85 else ('medium' if confidence >= 0.7 else 'low'),
                'should_review': confidence < 0.7
            },
            'suggestions': []
        },
        'timestamp': time.time(),
        'email_text': text,
    }
    return result


if __name__ == '__main__':
    print('sklearn wrapper test')
    import sys
    if len(sys.argv) < 3:
        print('Usage: python backend/sklearn_wrapper.py <model_path> <sample_text>')
        sys.exit(1)
    load_model(sys.argv[1])
    print(classify(sys.argv[2]))
