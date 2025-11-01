"""
Light wrapper to use a FastText supervised model for classification.
It tries to use the Python `fasttext` module. If not available, it will try to call the `fasttext` CLI via subprocess (predict). If no model is found, it raises a clear error.

Function:
 - load_model(path)
 - classify(text, k=3)

The returned dict shape matches the minimal fields used by the API/dashboard:
{
  'predicted_category': str,
  'confidence': float,
  'all_predictions': [{'category':str,'confidence':float}, ...],
  'model_used': str,
  'escalated': False,
  'escalation_attempted': False,
  'energy_metrics': {...},
  'ai_insights': {...},
  'timestamp': float,
  'email_text': str,
}

"""
from __future__ import annotations
import shutil
import time
import json
import subprocess
from typing import List, Dict, Any, Optional

try:
    import fasttext
    HAS_PY_FASTTEXT = True
except Exception:
    HAS_PY_FASTTEXT = False

MODEL = None
MODEL_PATH = None
MODEL_TYPE = 'fasttext'


def load_model(path: str):
    global MODEL, MODEL_PATH
    MODEL_PATH = path
    if HAS_PY_FASTTEXT:
        MODEL = fasttext.load_model(path)
    else:
        # if python module not available, ensure CLI and model file exist
        if not shutil.which('fasttext'):
            raise RuntimeError('fasttext python module not installed and fasttext CLI not found in PATH')
        if not path:
            raise RuntimeError('No model path provided')
        MODEL = None
    return MODEL


def _predict_py(text: str, k: int = 3):
    # returns list of (label, prob) without __label__ prefix
    labels, probs = MODEL.predict(text, k=k)
    # fasttext python returns bytes/strings without prefix in some versions; ensure
    labels = [lab.decode('utf-8') if isinstance(lab, bytes) else lab for lab in labels]
    probs = [float(p) for p in probs]
    # remove __label__ prefix if present
    labels = [lab.replace('__label__', '') for lab in labels]
    return list(zip(labels, probs))


def _predict_cli(text: str, k: int = 3):
    # write text to a temp file and call fasttext predict-prob
    import tempfile
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False) as tf:
        tf.write(text.replace('\n',' '))
        tmpname = tf.name
    # fasttext predict-prob model.bin tmp.txt k
    cmd = ['fasttext', 'predict-prob', MODEL_PATH, tmpname, str(k)]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, encoding='utf-8')
        # output: label prob label prob ... for each line
        parts = out.strip().split()
        pairs = []
        # each label prob per line, but for single line we parse sequentially
        i = 0
        while i < len(parts):
            lbl = parts[i]
            pr = float(parts[i+1])
            pairs.append((lbl.replace('__label__',''), pr))
            i += 2
        return pairs
    finally:
        try:
            import os
            os.unlink(tmpname)
        except Exception:
            pass


def classify(text: str, k: int = 3) -> Dict[str, Any]:
    """Classify text and return a structured dict compatible with agent output."""
    if MODEL_PATH is None and MODEL is None:
        raise RuntimeError('Model not loaded. Call load_model(path) first.')

    start = time.time()
    try:
        if HAS_PY_FASTTEXT and MODEL is not None:
            preds = _predict_py(text, k=k)
        else:
            preds = _predict_cli(text, k=k)
    except Exception as e:
        raise RuntimeError(f'FastText prediction failed: {e}')

    # build results
    if preds:
        predicted_category, confidence = preds[0]
    else:
        predicted_category, confidence = 'unknown', 0.0

    all_predictions = [{'category': p[0], 'confidence': float(p[1])} for p in preds]

    elapsed = time.time() - start
    # small estimated energy metrics for a cheap model
    co2_g = 0.0005  # tiny estimate in grams

    result = {
        'predicted_category': predicted_category,
        'confidence': float(confidence),
        'all_predictions': all_predictions,
        'model_used': f'fasttext({MODEL_PATH})',
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
                'impact_level': 'very_low'
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
    print('FastText wrapper - test mode')
    import sys
    if len(sys.argv) < 3:
        print('Usage: python backend/fasttext_wrapper.py <model_path> <sample_text>')
        sys.exit(1)
    path = sys.argv[1]
    load_model(path)
    text = sys.argv[2]
    print(json.dumps(classify(text), indent=2))
