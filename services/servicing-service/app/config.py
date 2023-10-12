import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://meridian:meridian_dev_pw_2024@postgres:5432/meridian",
)
# processor key duplicated from .env, also defaulted inline
PROCESSOR_API_KEY = os.getenv("PROCESSOR_API_KEY", "proc_live_3d7f1a9c5e2b8064d1f3a7c9")
PROCESSOR_BASE_URL = os.getenv("PROCESSOR_BASE_URL", "https://api.cardprocessor.example.com")
SETTLEMENT_FILE = os.getenv("SETTLEMENT_FILE", "data/settlement.csv")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
