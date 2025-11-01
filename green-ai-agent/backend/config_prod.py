import os
from pathlib import Path

# Production Models (you might want to use optimized versions)
LIGHT_MODEL = os.getenv("LIGHT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
HEAVY_MODEL = os.getenv("HEAVY_MODEL", "textattack/bert-base-uncased-SST-2")

# Performance settings for production
DEFAULT_CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.87"))
ENERGY_SAVING_THRESHOLD = float(os.getenv("ENERGY_SAVING_THRESHOLD", "0.25"))
MAX_EMAIL_LENGTH = int(os.getenv("MAX_EMAIL_LENGTH", "10000"))

# Database settings
DB_PATH = Path(os.getenv("DB_PATH", "/app/data/green_metrics.sqlite3"))
MODELS_CACHE_PATH = Path(os.getenv("MODELS_CACHE", "/app/models"))

# Redis for caching (production)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_EXPIRY = int(os.getenv("CACHE_EXPIRY", "3600"))  # 1 hour

# Monitoring
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"

# Categories
EMAIL_CATEGORIES = [
    "work", "spam", "promotions", 
    "personal", "support", "newsletter"
]


# config.py

# from pathlib import Path

# # Email Classification Models
# LIGHT_MODEL = "distilbert-base-uncased"  # Will fine-tune for email
# HEAVY_MODEL = "bert-base-uncased"        # Will fine-tune for email

# # Categories
# EMAIL_CATEGORIES = ["work", "spam", "promotions", "personal", "support", "newsletter"]
# NUM_CLASSES = len(EMAIL_CATEGORIES)

# # Energy & Performance Thresholds
# DEFAULT_CONFIDENCE_THRESHOLD = 0.85
# ENERGY_SAVING_THRESHOLD = 0.30  # 30% energy savings required to switch
# ACCURACY_DROP_TOLERANCE = 0.02  # Max 2% accuracy drop allowed

# # Paths
# ROOT = Path(__file__).resolve().parents[1]
# DB_PATH = ROOT / "green_metrics.sqlite3"
# MODELS_PATH = ROOT / "models"
# EMAIL_SAMPLES_PATH = ROOT / "data" / "email_samples.txt"


