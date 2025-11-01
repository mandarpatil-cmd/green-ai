"""Backend package for Green AI Agent.
Handles configuration merging and initialization.
"""
import os

# Define the items to be exported from this package
__all__ = [
    'EMAIL_CATEGORIES',
    'NUM_CLASSES',
    'DEFAULT_CONFIDENCE_THRESHOLD',
    'ENERGY_SAVING_THRESHOLD',
    'ACCURACY_DROP_TOLERANCE',
    'DB_PATH',
    'MODELS_PATH',
    'EMAIL_SAMPLES_PATH',
    'FASTTEXT_MODEL_PATH',
    'SKLEARN_MODEL_PATH',
    'ROOT',
    'LIGHT_MODEL',
    'HEAVY_MODEL',
    'MAX_EMAIL_LENGTH',
]

# Core configuration
from .config import (
    EMAIL_CATEGORIES,
    NUM_CLASSES,
    DEFAULT_CONFIDENCE_THRESHOLD,
    ENERGY_SAVING_THRESHOLD,
    ACCURACY_DROP_TOLERANCE,
    DB_PATH,
    MODELS_PATH,
    EMAIL_SAMPLES_PATH,
    FASTTEXT_MODEL_PATH,
    SKLEARN_MODEL_PATH,
    ROOT,
    LIGHT_MODEL,
    HEAVY_MODEL,
)

# Override with production settings if PRODUCTION=true
if os.getenv("PRODUCTION", "false").lower() == "true":
    from .config_prod import (
        LIGHT_MODEL,
        HEAVY_MODEL,
        DEFAULT_CONFIDENCE_THRESHOLD,
        ENERGY_SAVING_THRESHOLD,
        MAX_EMAIL_LENGTH,
        DB_PATH,
        MODELS_CACHE_PATH,
        REDIS_URL,
        CACHE_EXPIRY,
        LOG_LEVEL,
        ENABLE_METRICS
    )
    __all__.extend([
        'MODELS_CACHE_PATH',
        'REDIS_URL',
        'CACHE_EXPIRY',
        'LOG_LEVEL',
        'ENABLE_METRICS'
    ])
